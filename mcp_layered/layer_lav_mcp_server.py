"""Layer 6: Session routing and session management middleware.

This layer is responsible for:
- Per-connection session tracking
- Session ID routing
- Forwarding config initialization to Layer 4 on session creation
- Managing the lifecycle of LavSession instances

It wraps the Layer 5 adapter in a session-aware envelope.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import uuid
from pathlib import Path
from typing import Any, Callable

from mcp_layered.layer_lav_init import LavSession, create_session, default_session
from mcp_layered.layer_lav_mcp import MCPAdapter, TOOL_DEFINITIONS

logger = logging.getLogger("mcp_layered.server")


class SessionRegistry:
    """Manages LavSession instances with unique session IDs.

    Thread-safe. Used by Layer 6 to track sessions per MCP connection.
    """

    def __init__(self):
        self._sessions: dict[str, LavSession] = {}
        self._lock = threading.Lock()

    def create(self, session: LavSession | None = None, **session_kwargs) -> str:
        """Create a new session and return its ID.

        Args:
            session: An existing LavSession to register. If None, a new one
                     is created via create_session(**session_kwargs).
            **session_kwargs: Forwarded to create_session() if session is None.

        Returns:
            The unique session ID string.
        """
        if session is None:
            session = create_session(**session_kwargs)

        session_id = uuid.uuid4().hex
        with self._lock:
            self._sessions[session_id] = session
        return session_id

    def get(self, session_id: str) -> LavSession | None:
        """Get a session by ID, or None if not found."""
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None = None) -> tuple[str, LavSession]:
        """Get an existing session or create a new one.

        Returns:
            Tuple of (session_id, LavSession).
        """
        if session_id and session_id in self._sessions:
            with self._lock:
                return session_id, self._sessions[session_id]
        new_id = self.create()
        return new_id, self.get(new_id)

    def remove(self, session_id: str) -> bool:
        """Remove a session by ID. Returns True if it existed."""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions.pop(session_id)
                session.close()
                return True
        return False

    def list_ids(self) -> list[str]:
        """Return a list of all session IDs."""
        with self._lock:
            return list(self._sessions.keys())

    def clear(self) -> int:
        """Close and remove all sessions. Returns the number removed."""
        with self._lock:
            count = len(self._sessions)
            for session in self._sessions.values():
                session.close()
            self._sessions.clear()
        return count

    @property
    def count(self) -> int:
        """Number of active sessions."""
        with self._lock:
            return len(self._sessions)


class SessionManager:
    """Manages the relationship between MCP connections and sessions.

    This is the main entry point for Layer 6. It:
    1. Uses a SessionRegistry to track sessions.
    2. Creates MCPAdapter instances per session.
    3. Routes MCP tool calls to the correct session's adapter.
    """

    def __init__(
        self,
        use_single_session: bool = False,
        default_config_path: str | None = None,
        default_executable: str | None = None,
        log_file: str | None = None,
    ):
        """Initialize the session manager.

        Args:
            use_single_session: If True, all connections share one session
                               (no per-connection session IDs).
            default_config_path: Path to config file for new sessions.
            default_executable: Executable override for new sessions.
            log_file: Path to log MCP tool calls (per-session UUID file if dir).
        """
        self._registry = SessionRegistry()
        self._use_single_session = use_single_session
        self._default_config_path = default_config_path
        self._default_executable = default_executable
        self._log_file = log_file
        self._single_session_id: str | None = None
        self._single_adapter: MCPAdapter | None = None

        if use_single_session:
            self._single_session_id = self._registry.create(
                config_path=default_config_path,
                executable=default_executable,
            )

    @property
    def registry(self) -> SessionRegistry:
        """Return the session registry."""
        return self._registry

    def create_session(self, session_id: str | None = None) -> MCPAdapter:
        """Create a new session (or return existing single session).

        Args:
            session_id: If use_single_session=True, this is ignored.
                        Otherwise, a new session is created (or the existing
                        one with this ID is returned if it exists).

        Returns:
            An MCPAdapter wrapping the session.
        """
        def _make_adapter(session):
            adapter = MCPAdapter(session)
            if self._log_file:
                adapter.set_log_file(self._log_file)
            return adapter

        if self._use_single_session:
            if self._single_adapter is None:
                session = self._registry.get(self._single_session_id)
                self._single_adapter = _make_adapter(session)
            return self._single_adapter

        if session_id and session_id in self._registry._sessions:
            session = self._registry.get(session_id)
            return _make_adapter(session)

        new_id = self._registry.create(
            config_path=self._default_config_path,
            executable=self._default_executable,
        )
        session = self._registry.get(new_id)
        return _make_adapter(session)

    def get_adapter(self, session_id: str | None = None) -> MCPAdapter | None:
        """Get the MCPAdapter for a session.

        For single-session mode, returns the shared adapter.
        For multi-session mode, returns the adapter for the given session_id.
        """
        if self._use_single_session:
            if self._single_adapter is None:
                return self.create_session()
            return self._single_adapter

        if session_id is None:
            return None

        session = self._registry.get(session_id)
        if session is None:
            return None
        return MCPAdapter(session)

    def dispatch_tool(
        self, session_id: str | None, name: str, arguments: dict[str, Any] | None = None
    ) -> str:
        """Route a tool call to the correct session's adapter.

        Args:
            session_id: The session ID (None for single-session mode).
            name: The MCP tool name.
            arguments: Tool arguments.

        Returns:
            The tool result string.

        Raises:
            ValueError: If session_id is None in multi-session mode and no
                        default session exists.
            CommandError: If the tool invocation fails.
        """
        adapter = self.get_adapter(session_id)
        if adapter is None:
            raise ValueError(
                "No session found. In multi-session mode, a valid session_id is required."
            )
        return adapter.dispatch_tool(name, arguments)

    def close_session(self, session_id: str) -> bool:
        """Close a session by ID. Returns True if it existed."""
        if self._use_single_session and session_id == self._single_session_id:
            self._single_adapter = None
        return self._registry.remove(session_id)

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the list of available MCP tools (same for all sessions)."""
        return TOOL_DEFINITIONS[:]

    def close(self) -> None:
        """Close all sessions and free resources."""
        self._registry.clear()
        self._single_adapter = None
        self._single_session_id = None

    def __enter__(self) -> "SessionManager":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# --------------------------------------------------------------------------- #
#  MCP JSON-RPC helpers (stdio transport)                                     #
# --------------------------------------------------------------------------- #
def _make_response(request_id: Any, result: dict[str, Any] | str) -> str:
    """Build a JSON-RPC 2.0 success response.

    Plain strings are wrapped in MCP content form.
    """
    if isinstance(result, str):
        result = {"content": [{"type": "text", "text": result}]}
    return json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    })


def _make_error(
    request_id: Any, code: int, message: str, data: str | None = None
) -> str:
    """Build a JSON-RPC 2.0 error response."""
    error: dict[str, Any] = {"code": code, "message": message}
    if data:
        error["data"] = data
    return json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error,
    })


def _write_stdout(line: str) -> None:
    """Write one line to stdout and flush (stdio MCP transport)."""
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _handle_mcp_request(
    request: dict[str, Any],
    manager: SessionManager,
) -> str:
    """Process a single MCP JSON-RPC request and return the response string.

    Handles:
      - "initialize" — server capabilities handshake
      - "tools/list" — return available tool definitions
      - "tools/call" — invoke a tool on the (single) stdio session
      - "prompts/list" / "resources/list" — (empty)
      - "initialized" / "notifications/progress" — notifications (no response)
    """
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    req_id = request.get("id")

    if method == "initialize":
        return _make_response(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "prompts": {},
                "resources": {},
            },
            "serverInfo": {
                "name": "lavender-debug-mcp",
                "version": "0.2.0",
                "description": (
                    "MCP server for debugging the Lavender game engine "
                    "(layered architecture)."
                ),
            },
        })

    if method == "tools/list":
        return _make_response(req_id, {"tools": manager.list_tools()})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        logger.info("Tool call: %s args=%s", tool_name, arguments)
        try:
            # session_id=None: single-session mode (the stdio session).
            result = manager.dispatch_tool(None, tool_name, arguments)
            return _make_response(req_id, result)
        except Exception as e:
            logger.exception("Tool call failed: %s", e)
            return _make_error(
                req_id, -32000, "Tool execution failed", str(e)
            )

    if method == "prompts/list":
        return _make_response(req_id, {"prompts": []})

    if method == "resources/list":
        return _make_response(req_id, {"resources": []})

    if method in ("initialized", "notifications/progress"):
        return ""  # notification — no response

    return _make_error(req_id, -32601, f"Method not found: {method}")


def run_stdio(manager: SessionManager) -> None:
    """Run the MCP server in stdio mode (JSON-RPC 2.0 over stdin/stdout).

    Reads one JSON-RPC request per line from stdin and writes one response
    per line to stdout.  All logging goes to stderr so stdout stays a clean
    protocol channel.
    """
    logger.info("MCP server (layered) running in stdio mode")
    while True:
        line = sys.stdin.readline()
        if not line:
            break  # EOF
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            _write_stdout(
                _make_error(None, -32700, "Parse error", "Invalid JSON")
            )
            continue

        # Handle batch requests (array of requests).
        if isinstance(request, list):
            responses = [
                resp
                for resp in (_handle_mcp_request(r, manager) for r in request)
                if resp
            ]
            if responses:
                _write_stdout(json.dumps(responses))
        else:
            response = _handle_mcp_request(request, manager)
            if response:
                _write_stdout(response)


# --------------------------------------------------------------------------- #
#  CLI entry point                                                            #
# --------------------------------------------------------------------------- #
def _resolve_stdio_log_file(log_arg: str | None) -> str | None:
    """Resolve a --log argument into a concrete file path (or None).

    If the argument is a directory (or has no file extension), a
    UUID-named log file is created inside it.  If it's a concrete file
    path, the parent directory is ensured and the path is used as-is.
    """
    if not log_arg:
        return None
    p = Path(log_arg).expanduser()
    if p.suffix == "" or p.is_dir():
        p.mkdir(parents=True, exist_ok=True)
        return str(p / f"{uuid.uuid4().hex}.jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def main() -> int:
    """CLI entry point: python3 -m mcp_layered.layer_lav_mcp_server [--stdio]."""
    parser = argparse.ArgumentParser(
        description=(
            "Lavender Layered MCP Server — debug the Lavender game engine "
            "via MCP (layered architecture)."
        ),
    )
    parser.add_argument(
        "--stdio", action="store_true",
        help="Run in stdio mode (JSON-RPC over stdin/stdout). "
             "This is the only supported transport.",
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to config.json (see layer_lav_config).",
    )
    parser.add_argument(
        "--executable", "-e", default=None,
        help="Override the game executable path (overwrites config). "
             "The executable may not exist at startup; commands that need "
             "it (session_start) fail with a clear error.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--log", default="/tmp/lav-log/",
        help="Enable MCP tool call/response logging (JSON lines format). "
             "If a directory is given, a UUID-named log file is created "
             "inside it. Default: /tmp/lav-log/ (always enabled).",
    )

    args = parser.parse_args()

    if not args.stdio:
        parser.error("only stdio mode is supported (use --stdio)")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # CLI executable override takes precedence over config.
    executable: str | None = None
    if args.executable:
        executable = os.path.expandvars(os.path.expanduser(args.executable))
        logger.info(
            "Executable overridden via CLI: %s -> %s", args.executable, executable
        )

    log_file = _resolve_stdio_log_file(args.log)

    # stdio mode: one shared session for the connection.
    manager = SessionManager(
        use_single_session=True,
        default_config_path=args.config,
        default_executable=executable,
        log_file=log_file,
    )
    try:
        run_stdio(manager)
    finally:
        manager.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
