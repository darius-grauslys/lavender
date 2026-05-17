"""clang_server.py — Persistent clangd subprocess management via pygls.

Manages a clangd Language Server Protocol subprocess that stays alive
across MCP tool invocations.  Configuration is read from
``.lavender/clangd.json`` in the project root.

The asyncio event loop for pygls runs in a dedicated daemon thread.
All public methods are synchronous wrappers suitable for use from the
MCP server's main thread.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence, Union

from lsprotocol import types
from pygls.lsp.client import LanguageClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes for results
# ---------------------------------------------------------------------------

@dataclass
class Location:
    """A source location (file, line, column)."""
    file: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


@dataclass
class SymbolInfo:
    """A symbol with its kind and location."""
    name: str
    kind: str
    file: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.kind} {self.name} {self.file}:{self.line}:{self.column}"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class ClangdConfig:
    """Parsed .lavender/clangd.json configuration."""
    clangd_path: str = "/usr/lib/llvm/21/bin/clangd"
    compile_commands_path: str = "compile_commands.json"
    startup: str = "eager"
    restart_on_failure: bool = True
    initialization_timeout: float = 30.0
    request_timeout: float = 10.0

    @classmethod
    def load(cls, project_root: Path) -> Optional["ClangdConfig"]:
        """Load from .lavender/clangd.json.  Returns None if not found."""
        config_path = project_root / ".lavender" / "clangd.json"
        if not config_path.exists():
            return None
        try:
            with open(config_path) as f:
                data = json.load(f)
            return cls(
                clangd_path=data.get("clangd_path", cls.clangd_path),
                compile_commands_path=data.get("compile_commands_path",
                                               cls.compile_commands_path),
                startup=data.get("startup", cls.startup),
                restart_on_failure=data.get("restart_on_failure",
                                            cls.restart_on_failure),
                initialization_timeout=float(
                    data.get("initialization_timeout_seconds",
                             cls.initialization_timeout)),
                request_timeout=float(
                    data.get("request_timeout_seconds",
                             cls.request_timeout)),
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read clangd config: %s", exc)
            return None


# ---------------------------------------------------------------------------
# SymbolKind mapping
# ---------------------------------------------------------------------------

_SYMBOL_KIND_NAMES = {
    types.SymbolKind.File: "File",
    types.SymbolKind.Module: "Module",
    types.SymbolKind.Namespace: "Namespace",
    types.SymbolKind.Package: "Package",
    types.SymbolKind.Class: "Class",
    types.SymbolKind.Method: "Method",
    types.SymbolKind.Property: "Property",
    types.SymbolKind.Field: "Field",
    types.SymbolKind.Constructor: "Constructor",
    types.SymbolKind.Enum: "Enum",
    types.SymbolKind.Interface: "Interface",
    types.SymbolKind.Function: "Function",
    types.SymbolKind.Variable: "Variable",
    types.SymbolKind.Constant: "Constant",
    types.SymbolKind.String: "String",
    types.SymbolKind.Number: "Number",
    types.SymbolKind.Boolean: "Boolean",
    types.SymbolKind.Array: "Array",
    types.SymbolKind.Object: "Object",
    types.SymbolKind.Key: "Key",
    types.SymbolKind.Null: "Null",
    types.SymbolKind.EnumMember: "EnumMember",
    types.SymbolKind.Struct: "Struct",
    types.SymbolKind.Event: "Event",
    types.SymbolKind.Operator: "Operator",
    types.SymbolKind.TypeParameter: "TypeParameter",
}


def _symbol_kind_name(kind: types.SymbolKind) -> str:
    return _SYMBOL_KIND_NAMES.get(kind, f"Unknown({kind})")


# ---------------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------------

def _file_uri(path: str) -> str:
    """Convert a file path to a file:// URI."""
    return Path(os.path.abspath(path)).as_uri()


def _uri_to_path(uri: str) -> str:
    """Convert a file:// URI to a file path."""
    if uri.startswith("file://"):
        return uri[len("file://"):]
    return uri


# ---------------------------------------------------------------------------
# Location extraction helpers
# ---------------------------------------------------------------------------

def _extract_locations(
    result: Union[
        types.Location,
        Sequence[types.Location],
        Sequence[types.LocationLink],
        None,
    ],
) -> list[Location]:
    """Normalize LSP definition/references results into Location list."""
    if result is None:
        return []
    if isinstance(result, types.Location):
        return [Location(
            file=_uri_to_path(result.uri),
            line=result.range.start.line + 1,
            column=result.range.start.character + 1,
        )]
    locations: list[Location] = []
    for item in result:
        if isinstance(item, types.Location):
            locations.append(Location(
                file=_uri_to_path(item.uri),
                line=item.range.start.line + 1,
                column=item.range.start.character + 1,
            ))
        elif isinstance(item, types.LocationLink):
            locations.append(Location(
                file=_uri_to_path(item.target_uri),
                line=item.target_range.start.line + 1,
                column=item.target_range.start.character + 1,
            ))
    return locations


def _extract_symbols_from_document(
    result: Union[
        Sequence[types.SymbolInformation],
        Sequence[types.DocumentSymbol],
        None,
    ],
    file_path: str,
) -> list[SymbolInfo]:
    """Extract symbols from documentSymbol response."""
    if result is None:
        return []
    symbols: list[SymbolInfo] = []

    def _walk_document_symbols(
        items: Sequence[types.DocumentSymbol],
        file: str,
    ) -> None:
        for sym in items:
            symbols.append(SymbolInfo(
                name=sym.name,
                kind=_symbol_kind_name(sym.kind),
                file=file,
                line=sym.range.start.line + 1,
                column=sym.range.start.character + 1,
            ))
            if sym.children:
                _walk_document_symbols(sym.children, file)

    for item in result:
        if isinstance(item, types.SymbolInformation):
            symbols.append(SymbolInfo(
                name=item.name,
                kind=_symbol_kind_name(item.kind),
                file=_uri_to_path(item.location.uri),
                line=item.location.range.start.line + 1,
                column=item.location.range.start.character + 1,
            ))
        elif isinstance(item, types.DocumentSymbol):
            _walk_document_symbols([item], file_path)
    return symbols


def _extract_symbols_from_workspace(
    result: Union[
        Sequence[types.SymbolInformation],
        Sequence[types.WorkspaceSymbol],
        None,
    ],
) -> list[SymbolInfo]:
    """Extract symbols from workspace/symbol response."""
    if result is None:
        return []
    symbols: list[SymbolInfo] = []
    for item in result:
        if isinstance(item, types.SymbolInformation):
            symbols.append(SymbolInfo(
                name=item.name,
                kind=_symbol_kind_name(item.kind),
                file=_uri_to_path(item.location.uri),
                line=item.location.range.start.line + 1,
                column=item.location.range.start.character + 1,
            ))
        elif isinstance(item, types.WorkspaceSymbol):
            loc = item.location
            if isinstance(loc, types.Location):
                symbols.append(SymbolInfo(
                    name=item.name,
                    kind=_symbol_kind_name(item.kind),
                    file=_uri_to_path(loc.uri),
                    line=loc.range.start.line + 1,
                    column=loc.range.start.character + 1,
                ))
            else:
                # WorkspaceSymbol can have a uri-only location
                symbols.append(SymbolInfo(
                    name=item.name,
                    kind=_symbol_kind_name(item.kind),
                    file=_uri_to_path(loc.uri) if hasattr(loc, "uri") else "",
                    line=0,
                    column=0,
                ))
    return symbols


# ---------------------------------------------------------------------------
# ClangdSession
# ---------------------------------------------------------------------------

class ClangdSession:
    """Manages a persistent clangd subprocess via pygls LanguageClient.

    The asyncio event loop runs in a dedicated daemon thread.  All public
    query methods are synchronous and safe to call from any thread.
    """

    def __init__(self, config: ClangdConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self._client: Optional[LanguageClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._opened_files: set[str] = set()
        self._started = False
        self._lock = threading.Lock()
        self._compile_commands_ok = False  # tracks whether CDB was valid at start

    # -- lifecycle -----------------------------------------------------------

    def start(self) -> None:
        """Start clangd subprocess and perform LSP initialize handshake."""
        with self._lock:
            if self._started and self.is_alive():
                return
            self._do_start()

    def _do_start(self) -> None:
        """Internal start (caller must hold self._lock)."""
        # Create a fresh event loop and thread
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever,
            daemon=True,
            name="clangd-event-loop",
        )
        self._thread.start()

        # Start the client
        try:
            self._run_sync(self._async_start())
            self._started = True
            self._opened_files.clear()
            self._compile_commands_ok = self.compile_commands_is_populated()
            logger.info("clangd started successfully at %s (cdb_ok=%s)",
                        self.config.clangd_path, self._compile_commands_ok)
        except Exception:
            self._cleanup()
            raise

    async def _async_start(self) -> None:
        """Async startup: create client, start IO, initialize."""
        self._client = LanguageClient("lavender-clangd", "1.0.0")

        await self._client.start_io(self.config.clangd_path)

        root_uri = self.project_root.as_uri()
        init_result = await asyncio.wait_for(
            self._client.initialize_async(types.InitializeParams(
                capabilities=types.ClientCapabilities(),
                root_uri=root_uri,
                workspace_folders=[
                    types.WorkspaceFolder(uri=root_uri, name="lavender"),
                ],
            )),
            timeout=self.config.initialization_timeout,
        )
        logger.debug("clangd initialize result: %s",
                      init_result.capabilities if init_result else "None")
        self._client.initialized(types.InitializedParams())

    def stop(self) -> None:
        """Shutdown clangd gracefully."""
        with self._lock:
            if not self._started:
                return
            try:
                self._run_sync(self._async_stop(), timeout=5.0)
            except Exception as exc:
                logger.warning("Error during clangd shutdown: %s", exc)
            finally:
                self._cleanup()

    async def _async_stop(self) -> None:
        if self._client:
            try:
                await self._client.shutdown_async(None)
                self._client.exit(None)
            except Exception:
                pass
            self._client.stop()

    def _cleanup(self) -> None:
        """Clean up loop and thread."""
        self._started = False
        self._client = None
        self._opened_files.clear()
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._loop = None
        self._thread = None

    def is_alive(self) -> bool:
        """Check if clangd process is still running."""
        if not self._started or not self._client:
            return False
        # Check if the underlying transport is still open
        try:
            transport = getattr(self._client, "_transport", None)
            if transport is None:
                return self._started
            # pygls uses _writer / _reader or similar
            return self._started
        except Exception:
            return False

    def ensure_ready(self) -> None:
        """Ensure clangd is running.  Restart if dead and config allows."""
        if self._started and self.is_alive():
            return
        if not self.config.restart_on_failure:
            raise RuntimeError("clangd is not running and restart is disabled")
        logger.info("clangd not running, restarting...")
        with self._lock:
            self._cleanup()
            self._do_start()

    def restart(self) -> None:
        """Stop and re-start clangd (e.g. after compile_commands.json changes)."""
        logger.info("Restarting clangd to pick up updated compile_commands.json")
        with self._lock:
            if self._started:
                try:
                    # Use a short timeout — don't block forever on shutdown
                    self._run_sync(self._async_stop(), timeout=5.0)
                except Exception as exc:
                    logger.warning("Error during clangd restart shutdown: %s", exc)
                finally:
                    self._cleanup()
            self._do_start()
            self._compile_commands_ok = self.compile_commands_is_populated()

    def compile_commands_is_populated(self) -> bool:
        """Check whether compile_commands.json exists and contains entries.

        Returns True if the file referenced by the config contains at
        least one compilation-database entry (i.e. is not ``[]`` or missing).
        """
        cdb_path = self.project_root / self.config.compile_commands_path
        # Follow symlinks
        try:
            resolved = cdb_path.resolve(strict=True)
        except (OSError, FileNotFoundError):
            return False
        try:
            content = resolved.read_text().strip()
            # Fast check: empty file, empty JSON array, or too short to hold an entry
            if not content or content == "[]" or len(content) < 10:
                return False
            return True
        except OSError:
            return False

    @property
    def started_with_valid_cdb(self) -> bool:
        """Whether clangd was started with a populated compile_commands.json."""
        return self._compile_commands_ok

    # -- file tracking -------------------------------------------------------

    def ensure_file_open(self, file_path: str) -> None:
        """Send didOpen for a file if not already opened in this session."""
        abs_path = os.path.abspath(file_path)
        uri = _file_uri(abs_path)
        if uri in self._opened_files:
            return
        try:
            content = Path(abs_path).read_text(errors="replace")
        except OSError as exc:
            raise FileNotFoundError(
                f"Cannot open {abs_path}: {exc}"
            ) from exc
        self._run_sync(self._async_did_open(uri, content))
        self._opened_files.add(uri)

    async def _async_did_open(self, uri: str, content: str) -> None:
        if self._client:
            self._client.text_document_did_open(
                types.DidOpenTextDocumentParams(
                    text_document=types.TextDocumentItem(
                        uri=uri,
                        language_id="c",
                        version=1,
                        text=content,
                    )
                )
            )

    # -- LSP queries (synchronous wrappers) ----------------------------------

    def definition(self, file: str, line: int, column: int) -> list[Location]:
        """textDocument/definition.  line/column are 1-indexed."""
        self.ensure_file_open(file)
        result = self._run_sync(self._async_definition(file, line, column))
        return _extract_locations(result)

    async def _async_definition(self, file: str, line: int, column: int):
        if not self._client:
            return None
        return await asyncio.wait_for(
            self._client.text_document_definition_async(
                types.DefinitionParams(
                    text_document=types.TextDocumentIdentifier(
                        uri=_file_uri(file)),
                    position=types.Position(
                        line=line - 1, character=column - 1),
                )
            ),
            timeout=self.config.request_timeout,
        )

    def references(self, file: str, line: int, column: int) -> list[Location]:
        """textDocument/references.  line/column are 1-indexed."""
        self.ensure_file_open(file)
        result = self._run_sync(self._async_references(file, line, column))
        return _extract_locations(result)

    async def _async_references(self, file: str, line: int, column: int):
        if not self._client:
            return None
        return await asyncio.wait_for(
            self._client.text_document_references_async(
                types.ReferenceParams(
                    text_document=types.TextDocumentIdentifier(
                        uri=_file_uri(file)),
                    position=types.Position(
                        line=line - 1, character=column - 1),
                    context=types.ReferenceContext(
                        include_declaration=True),
                )
            ),
            timeout=self.config.request_timeout,
        )

    def document_symbols(self, file: str) -> list[SymbolInfo]:
        """textDocument/documentSymbol."""
        self.ensure_file_open(file)
        result = self._run_sync(self._async_document_symbols(file))
        return _extract_symbols_from_document(result, os.path.abspath(file))

    async def _async_document_symbols(self, file: str):
        if not self._client:
            return None
        return await asyncio.wait_for(
            self._client.text_document_document_symbol_async(
                types.DocumentSymbolParams(
                    text_document=types.TextDocumentIdentifier(
                        uri=_file_uri(file)),
                )
            ),
            timeout=self.config.request_timeout,
        )

    def workspace_symbols(self, query: str) -> list[SymbolInfo]:
        """workspace/symbol."""
        result = self._run_sync(self._async_workspace_symbols(query))
        return _extract_symbols_from_workspace(result)

    async def _async_workspace_symbols(self, query: str):
        if not self._client:
            return None
        return await asyncio.wait_for(
            self._client.workspace_symbol_async(
                types.WorkspaceSymbolParams(query=query),
            ),
            timeout=self.config.request_timeout,
        )

    def hover(self, file: str, line: int, column: int) -> Optional[str]:
        """textDocument/hover.  Returns hover content as string or None."""
        self.ensure_file_open(file)
        result = self._run_sync(self._async_hover(file, line, column))
        if result is None:
            return None
        contents = result.contents
        if isinstance(contents, types.MarkupContent):
            return contents.value
        if isinstance(contents, str):
            return contents
        # MarkedString or list
        if isinstance(contents, list):
            parts = []
            for item in contents:
                if isinstance(item, str):
                    parts.append(item)
                elif hasattr(item, "value"):
                    parts.append(item.value)
            return "\n".join(parts)
        if hasattr(contents, "value"):
            return contents.value
        return str(contents)

    async def _async_hover(self, file: str, line: int, column: int):
        if not self._client:
            return None
        return await asyncio.wait_for(
            self._client.text_document_hover_async(
                types.HoverParams(
                    text_document=types.TextDocumentIdentifier(
                        uri=_file_uri(file)),
                    position=types.Position(
                        line=line - 1, character=column - 1),
                )
            ),
            timeout=self.config.request_timeout,
        )

    # -- sync/async bridge ---------------------------------------------------

    def _run_sync(self, coro, timeout: Optional[float] = None):
        """Run an async coroutine synchronously via the background loop."""
        if self._loop is None:
            raise RuntimeError("Event loop not started")
        if timeout is None:
            timeout = self.config.request_timeout
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_session: Optional[ClangdSession] = None
_session_lock = threading.Lock()


def get_session(project_root: Optional[Path] = None) -> Optional[ClangdSession]:
    """Get or create the module-level ClangdSession singleton.

    Returns None if ``.lavender/clangd.json`` doesn't exist.
    """
    global _session
    with _session_lock:
        if _session is not None:
            return _session

        if project_root is None:
            project_root = Path.cwd()

        config = ClangdConfig.load(project_root)
        if config is None:
            logger.info("No .lavender/clangd.json found — clangd disabled")
            return None

        session = ClangdSession(config, project_root)

        if config.startup == "eager":
            try:
                session.start()
            except Exception as exc:
                logger.warning("Failed to start clangd eagerly: %s", exc)
                # Don't set _session — next call will retry
                return None

        _session = session
        return _session


def shutdown_session() -> None:
    """Shutdown the module-level session if it exists."""
    global _session
    with _session_lock:
        if _session is not None:
            _session.stop()
            _session = None
