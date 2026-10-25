"""
lav_mcp_server.py — MCP server middleware router for the Lavender debugger.

The MCP Server is a middleware router that listens on a port (HTTP mode) or
stdin (stdio mode) and routes incoming MCP JSON-RPC 2.0 requests to the
appropriate ``LavMcpSession`` based on the session ID.

Protocol flow (DESIGN.md §"MCP Server"):
  1. Look at the MCP-protocol equivalent for a session ID.
  2. Look for an existing session ID in the active session registry.
  3. If missing, make a new session and route the request.

This supports multiple agents communicating to a singular server.

Usage:
  # HTTP mode (default):
  python3 -m mcp.lav_mcp_server --port 8890 \\
      --config /path/to/config.json

  # stdio mode (for Claude Desktop / Cursor):
  python3 -m mcp.lav_mcp_server --stdio \\
      --config /path/to/config.json

   # Override the executable from config with a CLI argument:
   python3 -m mcp.lav_mcp_server --executable /path/to/game \\
       --stdio

   # Run a single session per HTTP connection (no session ID in URL):
   python3 -m mcp.lav_mcp_server --port 8890 --no-session-routing

Executable resolution order (highest precedence first):
   1. session_start(executable=...)  — per-session tool argument
   2. --executable / -e              — CLI argument
   3. config.json "session.executable"
   4. built-in fallback

A missing executable is accepted at server/session init time; commands that
need it (session_start, core_load) fail with a clear "executable not found"
error.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .lav_mcp import LavMcpSession, TOOL_DEFINITIONS

logger = logging.getLogger("lav_mcp_server")

# --------------------------------------------------------------------------- #
#  Session registry                                                           #
# --------------------------------------------------------------------------- #
class SessionRegistry:
    """Thread-safe registry of active LavMcpSession instances.

    Maps session IDs (arbitrary strings) to LavMcpSession objects.
    Creates new sessions on demand using a factory closure.
    """

    def __init__(self, session_factory: Any) -> None:
        self._sessions: dict[str, LavMcpSession] = {}
        self._lock = threading.Lock()
        self._factory = session_factory

    def get_or_create(self, session_id: str) -> LavMcpSession:
        """Return the session for *session_id*, creating it if absent."""
        with self._lock:
            if session_id not in self._sessions:
                logger.info("Creating new session: %s", session_id)
                self._sessions[session_id] = self._factory()
            return self._sessions[session_id]

    def get(self, session_id: str) -> LavMcpSession | None:
        """Return the session for *session_id*, or None if not found."""
        with self._lock:
            return self._sessions.get(session_id)

    def remove(self, session_id: str) -> None:
        """Remove and stop the session for *session_id*."""
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if session is not None:
            try:
                session.session_stop()
            except Exception:
                pass

    def list_sessions(self) -> list[str]:
        """Return a list of all active session IDs."""
        with self._lock:
            return list(self._sessions.keys())

    def clear(self) -> None:
        """Stop and remove all sessions."""
        with self._lock:
            to_stop = list(self._sessions.values())
            self._sessions.clear()
        for session in to_stop:
            try:
                session.session_stop()
            except Exception:
                pass


# --------------------------------------------------------------------------- #
#  MCP JSON-RPC helpers                                                       #
# --------------------------------------------------------------------------- #
def _make_response(request_id: Any, result: dict[str, Any] | str) -> str:
    """Build a JSON-RPC 2.0 success response."""
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


def _handle_mcp_request(
    request: dict[str, Any],
    session: LavMcpSession,
) -> str:
    """Process a single MCP JSON-RPC request and return the response string.

    Handles:
      - "initialize" — server capabilities handshake
      - "tools/list" — return available tool definitions
      - "tools/call" — invoke a tool on the session
      - "prompts/list" — (empty)
      - "resources/list" — (empty)
    """
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    req_id = request.get("id")

    # -- initialize ---------------------------------------------------------- #
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
                "version": "0.1.0",
                "description": "MCP server for debugging the Lavender game engine.",
            },
        })

    # -- tools/list ---------------------------------------------------------- #
    if method == "tools/list":
        return _make_response(req_id, {"tools": TOOL_DEFINITIONS})

    # -- tools/call ---------------------------------------------------------- #
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        logger.info("Tool call: %s args=%s", tool_name, arguments)
        try:
            result = session.dispatch_tool(tool_name, arguments)
            return _make_response(req_id, result)
        except Exception as e:
            logger.exception("Tool call failed: %s", e)
            return _make_error(
                req_id, -32000, f"Tool execution failed", str(e)
            )

    # -- prompts/list (empty) ---------------------------------------------- #
    if method == "prompts/list":
        return _make_response(req_id, {"prompts": []})

    # -- resources/list (empty) -------------------------------------------- #
    if method == "resources/list":
        return _make_response(req_id, {"resources": []})

    # -- notifications (no response needed) -------------------------------- #
    if method in ("initialized", "notifications/progress"):
        return ""  # notification — no response

    # -- unknown method ---------------------------------------------------- #
    return _make_error(req_id, -32601, f"Method not found: {method}")


# --------------------------------------------------------------------------- #
#  HTTP transport (DESIGN.md: "listens on a port")                            #
# --------------------------------------------------------------------------- #
class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the MCP protocol.

    Session ID is extracted from the URL path:
      /mcp/{session_id}/          — route to the session
      /mcp/{session_id}/tools     — legacy alias
      /mcp/                       — default/unnamed session
    """

    # Class-level attributes set by the server factory.
    registry: SessionRegistry | None = None
    session_factory: Any = None
    no_session_routing: bool = False
    config: dict[str, Any] | None = None

    # Suppress default logging to keep stderr clean.
    def log_message(self, format: str, *args: Any) -> None:
        logger.debug("HTTP %s: %s", self.address_string(), format % args)

    def _get_session(self) -> LavMcpSession:
        """Extract the session from the URL path."""
        if self.registry is None or self.session_factory is None:
            raise RuntimeError("SessionRegistry not configured.")

        if self.no_session_routing:
            # Single session — always use the same one.
            return self.registry.get_or_create("default")

        # Extract session ID from path: /mcp/{session_id}/...
        path_parts = self.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0] == "mcp":
            session_id = path_parts[1]
            if session_id:
                return self.registry.get_or_create(session_id)

        # Fallback: default session.
        return self.registry.get_or_create("default")

    def do_POST(self) -> None:
        """Handle MCP JSON-RPC POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_response(
                _make_error(None, -32700, "Parse error", "Invalid JSON")
            )
            return

        # Handle both single requests and batches.
        if isinstance(request, list):
            responses = [
                resp
                for resp in (
                    self._process_request(r) for r in request
                )
                if resp
            ]
            self._send_response(json.dumps(responses))
        elif isinstance(request, dict):
            self._send_response(self._process_request(request))

    def _process_request(self, request: dict[str, Any]) -> str:
        """Process a single JSON-RPC request, returning the response string."""
        try:
            session = self._get_session()
        except Exception as e:
            req_id = request.get("id")
            return _make_error(req_id, -32000, "Session error", str(e))

        return _handle_mcp_request(request, session)

    def do_GET(self) -> None:
        """Handle health check and session listing."""
        # Health check.
        if self.path in ("/", "/health", "/status"):
            self._send_response(
                json.dumps({
                    "status": "ok",
                    "server": "lavender-debug-mcp",
                    "version": "0.1.0",
                })
            )
            return

        # Session listing.
        if self.path in ("/sessions", "/mcp/sessions"):
            if self.registry:
                self._send_response(
                    json.dumps({
                        "sessions": self.registry.list_sessions(),
                    })
                )
            else:
                self._send_response(json.dumps({"sessions": []}))
            return

        # Tool definitions (for introspection without MCP handshake).
        if self.path in ("/tools", "/mcp/tools"):
            self._send_response(json.dumps({"tools": TOOL_DEFINITIONS}))
            return

        # Unknown path.
        self._send_response(
            _make_error(None, -32601, "Not found:", self.path)
        )

    def _send_response(self, body: str) -> None:
        """Send a JSON response with appropriate headers."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def make_http_handler(
    session_factory: Any,
    no_session_routing: bool = False,
    config: dict[str, Any] | None = None,
) -> type[MCPRequestHandler]:
    """Create a configured MCPRequestHandler subclass."""

    registry = SessionRegistry(session_factory)

    class _Handler(MCPRequestHandler):
        pass

    _Handler.registry = registry  # type: ignore[assignment]
    _Handler.session_factory = session_factory  # type: ignore[assignment]
    _Handler.no_session_routing = no_session_routing  # type: ignore[assignment]
    _Handler.config = config  # type: ignore[assignment]

    return _Handler


# --------------------------------------------------------------------------- #
#  stdio transport (for Claude Desktop / Cursor)                              #
# --------------------------------------------------------------------------- #
def run_stdio(
    session_factory: Any,
    config: dict[str, Any] | None = None,
) -> None:
    """Run the MCP server in stdio mode (JSON-RPC over stdin/stdout).

    Standard MCP transport for desktop AI assistants.  A default session is
    created on the first ``initialize`` request.
    """
    registry = SessionRegistry(session_factory)
    # Pre-create a default session.
    session = registry.get_or_create("default")

    logger.info("MCP server running in stdio mode (session: default)")

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
            sys.stdout.write(
                _make_error(None, -32700, "Parse error", "Invalid JSON") + "\n"
            )
            sys.stdout.flush()
            continue

        # Handle batch requests (array of requests).
        if isinstance(request, list):
            responses = [
                resp
                for resp in (
                    _handle_mcp_request(r, session) for r in request
                )
                if resp
            ]
            if responses:
                sys.stdout.write(json.dumps(responses) + "\n")
                sys.stdout.flush()
        elif isinstance(request, dict):
            response = _handle_mcp_request(request, session)
            if response:
                sys.stdout.write(response + "\n")
                sys.stdout.flush()


# --------------------------------------------------------------------------- #
#  Configuration                                                               #
# --------------------------------------------------------------------------- #
def _resolve_executable(raw: str | None) -> str:
    """Resolve an executable path with env var expansion and fallbacks.

    Supports ``${LAVENDER_DIR}`` / ``$LAVENDER_DIR`` syntax via
    ``os.path.expandvars``.  Fallback logic:

    1. Plain path (no env var syntax) — returned as-is, even if it does
       not yet exist (the user may be testing config parsing).
    2. Path with env var syntax where the expanded result exists — use it.
    3. Path with env var syntax but expansion didn't yield a valid path —
       try ``$LAVENDER_DIR/build/sdl/Lavender_Dev``, then fall back to
       the hardcoded default.
    4. Empty/None — try ``$LAVENDER_DIR/build/sdl/Lavender_Dev``, then fall
       back to the hardcoded default.
    """
    _FALLBACK = "/home/shalidor/Projects/Lavender_Dev/build/sdl/Lavender_Dev"
    _VAR = "LAVENDER_DIR"

    if not raw:
        lavender_dir = os.environ.get(_VAR, "")
        if lavender_dir:
            return os.path.join(lavender_dir, "build/sdl/Lavender_Dev")
        return _FALLBACK

    # Expand env vars (e.g. ${LAVENDER_DIR}/build/sdl/Lavender_Dev).
    # Note: on Python 3.14, os.path.expandvars leaves *unset* variables
    # unchanged (e.g. "${LAVENDER_DIR}" stays as-is if the env var is not set).
    # We detect env var syntax by checking for ${VAR} or $VAR patterns.
    expanded = os.path.expandvars(raw)

    # If the expanded path exists, use it (covers both plain paths and
    # env-var-expanded paths where the var was set).
    if os.path.exists(expanded):
        return expanded

    # If env var syntax was present in the original, try LAVENDER_DIR fallback.
    _has_env = ("${" + _VAR) in raw or ("$" + _VAR) in raw
    if _has_env:
        lavender_dir = os.environ.get(_VAR, "")
        if lavender_dir:
            candidate = os.path.join(lavender_dir, "build/sdl/Lavender_Dev")
            if os.path.exists(candidate):
                return candidate
        return _FALLBACK

    # Plain path that doesn't exist — return as-is (let the caller deal with it).
    return expanded


def load_config(config_path: str | None) -> dict[str, Any]:
    """Load configuration from a JSON file.

    Expected structure (DESIGN.md §Config)::

        {
            "config": {
                "session": {
                    "executable": "/path/to/lavender_game"
                },
                "core": {
                    "dump-location": "/tmp/lav-core-dump/"
                }
            }
        }

    Supports ``${LAVENDER_DIR}`` / ``$LAVENDER_DIR`` env var expansion
    in the ``executable`` field.
    """
    # Default config.
    config: dict[str, Any] = {
        "config": {
            "session": {
                "executable": "${LAVENDER_DIR}/build/sdl/Lavender_Dev"
            },
            "core": {
                "dump-location": "/tmp/lav-core-dump/"
            }
        }
    }

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path) as f:
                loaded = json.load(f)
            if "config" in loaded:
                # Merge loaded config over defaults.
                config["config"].update(loaded["config"])
            else:
                config["config"].update(loaded)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load config from %s: %s", config_path, e)

    # Resolve env vars in the executable path.
    session_cfg = config.get("config", {}).get("session", {})
    if "executable" in session_cfg:
        session_cfg["executable"] = _resolve_executable(session_cfg["executable"])

    return config


def _resolve_log_file(log_arg: str | None) -> str | None:
    """Resolve a --log argument into a concrete file path (or None).

    If the argument is a directory (or has no file extension), a per-session
    UUID-named log file is created inside that directory at factory call time.

    If it's a concrete path, we just ensure the parent dir exists and return it.
    """
    if log_arg is None:
        return None
    p = Path(log_arg).expanduser()
    if p.suffix == "" or p.is_dir():
        # Defer UUID generation to factory call time — each session gets its own file.
        p.mkdir(parents=True, exist_ok=True)
        return None  # signal to factory to generate a UUID file
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def make_session_factory(config: dict[str, Any] | None, log_arg: str | None = None) -> Any:
    """Create a factory closure that produces LavMcpSession instances.

    If *log_arg* is provided, tool call/response logging is enabled.  If it's
    a directory path (or no extension), each session gets its own UUID-named
    log file inside that directory.
    """
    cfg = (config or {}).get("config", {})
    session_cfg = cfg.get("session", {})
    core_cfg = cfg.get("core", {})

    executable = _resolve_executable(session_cfg.get("executable"))
    dump_location = core_cfg.get("dump-location", "/tmp/lav-core-dump/")

    # Pre-resolve the log path.  If it's a directory, we'll generate a UUID per session.
    log_path = _resolve_log_file(log_arg) if log_arg else None
    log_dir = Path(log_arg).expanduser() if log_arg and (log_path is None) else None

    def factory() -> LavMcpSession:
        if log_path is not None:
            session_log = log_path
        elif log_dir is not None:
            import uuid as _uuid
            session_log = str(log_dir / f"{_uuid.uuid4().hex}.jsonl")
        else:
            session_log = None
        return LavMcpSession(
            executable=executable, dump_location=dump_location, log_file=session_log
        )

    return factory


# --------------------------------------------------------------------------- #
#  Main entry point                                                           #
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lavender MCP Server — debug the Lavender game engine via MCP."
    )
    parser.add_argument(
        "--port", type=int, default=8890,
        help="Port to listen on (HTTP mode). Default: 8890"
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Host to bind to. Default: 0.0.0.0"
    )
    parser.add_argument(
        "--stdio", action="store_true",
        help="Run in stdio mode (for Claude Desktop / Cursor)."
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to config.json."
    )
    parser.add_argument(
        "--no-session-routing", action="store_true",
        help="Use a single shared session (no per-connection session IDs)."
    )
    parser.add_argument(
        "--executable", "-e", default=None,
        help="Override the game executable path (overwrites config)."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging."
    )
    parser.add_argument(
        "--log", default="/tmp/lav-log/",
        help="Enable MCP tool call/response logging (JSON lines format). "
             "If a directory is given, per-session UUID-named log files are "
             "created inside it. Default: /tmp/lav-log/ (always enabled)."
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    config = load_config(args.config)

    # CLI executable override takes precedence over config.
    if args.executable:
        resolved = _resolve_executable(args.executable)
        session_cfg = config.setdefault("config", {}).setdefault("session", {})
        session_cfg["executable"] = resolved
        logger.info("Executable overridden via CLI: %s -> %s",
                     args.executable, resolved)

    session_factory = make_session_factory(config, args.log)

    if args.stdio:
        logger.info("Starting MCP server in stdio mode")
        run_stdio(session_factory, config)
        return 0

    # HTTP mode.
    handler_cls = make_http_handler(
        session_factory,
        no_session_routing=args.no_session_routing,
        config=config,
    )

    server = ThreadingHTTPServer((args.host, args.port), handler_cls)
    logger.info(
        "MCP server listening on %s:%d (HTTP mode, session routing: %s)",
        args.host, args.port, "off" if args.no_session_routing else "on",
    )
    logger.info("  Health check: http://%s:%d/health", args.host, args.port)
    logger.info("  Sessions:     http://%s:%d/sessions", args.host, args.port)
    logger.info("  Tools:        http://%s:%d/tools", args.host, args.port)
    logger.info("  Endpoints:")
    logger.info("    POST /mcp/{session_id}/  — JSON-RPC tool call")
    logger.info("    POST /mcp/              — default session")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
    finally:
        registry: SessionRegistry | None = handler_cls.registry
        if registry:
            registry.clear()

    return 0


if __name__ == "__main__":
    sys.exit(main())
