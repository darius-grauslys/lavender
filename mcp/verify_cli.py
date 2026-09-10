#!/usr/bin/env python3
"""
verify_cli.py — Thin MCP protocol shell for interactive verification.

This is the MCP-package equivalent of ``harness/verify_cli.py``, refactored
to operate **through the MCP protocol** rather than instantiating
``GDBController`` / scanner / driver objects directly.

Usage:
    # Local mode — uses an in-process LavMcpSession (no separate server):
    python3 -m mcp.verify_cli --program /path/to/executable

    # Remote mode — attach to a running MCP server:
    python3 -m mcp.lav_mcp_server --port 8890 --config mcp/config.json &
    python3 -m mcp.verify_cli --attach http://localhost:8890/mcp/my-session

Architecture:
    VerifyCLI (shell) → McpClient → LavMcpSession (local) or HTTP (remote)

    In local mode, the McpClient wraps a LavMcpSession and calls its
    dispatch_tool() method directly (in-process).  The GDBController is
    accessible via client.session._gdbmi for raw gdb commands.

    In remote mode (--attach), the McpClient sends JSON-RPC 2.0 requests
    to the MCP server's HTTP endpoint.  Raw gdb commands are unavailable
    because the server only exposes the higher-level MCP tools.

REPL commands (all map to MCP tools):
    start              → session_start  (launch game under GDB)
    status             → session_status (check running/halted/crashed)
    stop               → session_stop   (exit GDB)

    step               → navigate_step  (one game frame)
    bt                 → navigate_source (backtrace + source)

    core dump          → core_dump      (extract coredump)
    core load <uuid>   → core_load      (load coredump by UUID)
    core reset         → core_reset     (reload last coredump)

    processes          → process_list   (list all processes)
    process watch <ptr> → process_watch (breakpoint on a process)

    input read         → input_read     (current input state)
    input write <flag> [drive|drop]
                       → input_write    (set/clear input flag)

    ui managers        → ui_manager     (list UI managers)
    ui select <ptr>    → ui_manager_select (select a manager)
    ui list            → ui_list        (list elements under manager)
    ui invoke <handler> <element> [args...]
                       → ui_invoke      (invoke a handler)

    screenshot [path]  → graphics_screenshot
    audio list         → audio_list     (unsupported)
    audio listen       → audio_listen   (unsupported)

Raw gdb commands (local mode only):
    gdb <cmd>          → session._gdbmi.write(cmd)
    break <loc>        → -break-insert
    delete <n>         → -break-delete
    watch <expr>       → -break-watch
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any
from pathlib import Path

from .lav_mcp import LavMcpSession, TOOL_DEFINITIONS
from .lavender_debug import Input_Flags__u32


# --------------------------------------------------------------------------- #
#  MCP client                                                                  #
# --------------------------------------------------------------------------- #

class McpClient:
    """MCP client — wraps either a local ``LavMcpSession`` or a remote HTTP endpoint.

    Local mode:
        Calls ``session.dispatch_tool()`` directly (in-process, no HTTP).
        The GDBController is accessible via ``client.session._gdbmi``.

    Remote mode:
        Sends JSON-RPC 2.0 ``tools/call`` requests to the MCP server's
        HTTP endpoint (set with ``--attach``).
    """

    def __init__(self, session: LavMcpSession | None = None, url: str | None = None):
        if session is not None:
            self._local = True
            self._session = session
            self._url = None
        elif url is not None:
            self._local = False
            self._session = None
            self._url = url.rstrip("/")
        else:
            raise ValueError("Either session or url must be provided")

        self._req_id = 0

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        """Call an MCP tool and return the result text.

        Handles MCP multi-content results (text + image).  When an image
        content item is present, the base64-decoded PNG is written to
        ``screen.png`` (or the path embedded in the text message) so the
        CLI user can inspect it with an image viewer.
        """
        import base64

        arguments = arguments or {}

        if self._local:
            raw = self._session.dispatch_tool(name, arguments)
            # dispatch_tool may return a dict (structured result with content)
            # or a plain string (error message).
            if isinstance(raw, dict):
                return self._format_content(raw.get("content", []))
            return raw

        # Remote: JSON-RPC 2.0 POST
        self._req_id += 1
        body = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        try:
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                self._url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            return f"ERROR: connection failed: {e}"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

        if "error" in result:
            err = result["error"]
            return f"ERROR: {err.get('message', 'unknown error')}"

        content = result.get("result", {}).get("content", [])
        return self._format_content(content)

    def _format_content(self, content: list[dict[str, Any]]) -> str:
        """Format MCP content items, writing images to disk as needed.

        Returns the text from the first text content item, or a summary
        string if no text is present.
        """
        import base64

        text_parts = []
        for item in content:
            ctype = item.get("type", "")
            if ctype == "text":
                text_parts.append(item.get("text", ""))
            elif ctype == "image":
                data = item.get("data", "")
                if data:
                    try:
                        raw = base64.b64decode(data)
                    except Exception as e:
                        print(f"  [!] Failed to decode image: {e}")
                        continue
                    # Determine output path from text message, or default.
                    out_path = self._extract_image_path(text_parts)
                    try:
                        with open(out_path, "wb") as f:
                            f.write(raw)
                        print(f"  [image] Saved {len(raw)} bytes to {out_path}")
                    except OSError as e:
                        print(f"  [!] Failed to write image: {e}")
        if text_parts:
            return "\n".join(text_parts)
        return "(no text output)"

    @staticmethod
    def _extract_image_path(text_parts: list[str]) -> str:
        """Try to extract an image path from text message, default screen.png."""
        for text in reversed(text_parts):
            if ".png" in text:
                # Extract the path from the text message.
                import re
                match = re.search(r"([/\w\-]+\.png)", text)
                if match:
                    return match.group(1)
        return "screen.png"

    def list_tools(self) -> list[str]:
        """List available MCP tool names."""
        if self._local:
            return [t["name"] for t in TOOL_DEFINITIONS]

        # Remote: tools/list
        self._req_id += 1
        body = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": "tools/list",
        }
        try:
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                self._url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  [!] Failed to list tools: {e}")
            return []

        tools = result.get("result", {}).get("tools", [])
        return [t["name"] for t in tools]

    @property
    def is_local(self) -> bool:
        return self._local

    @property
    def session(self) -> LavMcpSession | None:
        """The local LavMcpSession (None in remote mode)."""
        return self._session


# --------------------------------------------------------------------------- #
#  CLI session                                                                  #
# --------------------------------------------------------------------------- #

class VerifyCLI:
    """Interactive MCP protocol shell."""

    def __init__(self, client: McpClient) -> None:
        self._client = client

    # -- helpers -------------------------------------------------------------- #

    def _call(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        """Call an MCP tool via the client and return the text result."""
        result = self._client.call_tool(name, arguments)
        print(result)
        return result

    def _raw_gdb(self, cmd: str) -> None:
        """Send a raw MI command to gdb (local mode only)."""
        if not self._client.is_local:
            print("  [!] Raw gdb commands are not available in remote (--attach) mode.")
            return

        session = self._client.session
        gdbmi = session._gdbmi if session else None
        if gdbmi is None:
            print("  [!] GDB is not started. Run 'start' first.")
            return

        print(f">>> gdb: {cmd}")
        try:
            resp = gdbmi.write(cmd)
            self._print_mi_response(resp)
        except Exception as e:
            print(f"  [error] {type(e).__name__}: {e}")

    @staticmethod
    def _print_mi_response(resp) -> None:
        """Pretty-print a pygdbmi response list."""
        for rec in resp:
            if isinstance(rec, dict):
                rtype = rec.get("type", "?")
                msg = rec.get("message", "")
                payload = rec.get("payload")
                if rtype in ("console", "target"):
                    print(f"  [console] {payload}")
                elif payload is not None:
                    print(f"  [{rtype}] {msg}: {payload}")
                else:
                    print(f"  [{rtype}] {msg}")

    # -- MCP command dispatch -------------------------------------------------- #

    def do_input_write(self, args: list[str]) -> None:
        """Call input_write MCP tool."""
        if not args:
            print("  usage: input write <FLAG> [drive|drop]")
            if Input_Flags__u32:
                print(f"    flags: {[f.name for f in Input_Flags__u32]}")
            else:
                print("    (flag names not available)")
            return

        flag = args[0]
        action = args[1] if len(args) > 1 else "drive"
        if action not in ("drive", "drop"):
            print(f"  unknown action: {action!r} (use 'drive' or 'drop')")
            return

        self._call("input_write", {"flag": flag, "action": action})

    def do_ui_invoke(self, args: list[str]) -> None:
        """Call ui_invoke MCP tool."""
        if len(args) < 2:
            print("  usage: ui invoke <handler> <element_ptr> [extra_args...]")
            print("    handlers: clicked, dragged, dropped, receive_drop, held, "
                  "typed, compose, dispose")
            return

        handler = args[0]
        element_ptr = args[1]
        rest = args[2:]

        tool_args: dict[str, Any] = {"element_ptr": element_ptr, "handler": handler}

        if handler == "receive_drop":
            if not rest:
                print("  usage: ui invoke receive_drop <target_ptr> <dropped_ptr>")
                return
            tool_args["dropped_ptr"] = rest[0]
        elif handler == "typed":
            if not rest:
                print("  usage: ui invoke typed <element_ptr> <symbol>")
                # (handler-first: ui invoke typed <element_ptr> <symbol>)
                return
            tool_args["symbol"] = rest[0]

        self._call("ui_invoke", tool_args)

    def do_core_load(self, args: list[str]) -> None:
        """Call core_load MCP tool."""
        if not args:
            # Fall back to core_load_last (loads the most recent dump).
            self._call("core_reset")
            return
        self._call("core_load", {"uuid": args[0]})

    # -- REPL ------------------------------------------------------------------ #

    def print_help(self) -> None:
        mode = "local" if self._client.is_local else "remote (attached)"
        print(f"""
Commands (mode: {mode}):
  start              Launch game under GDB (session_start)
  status             Check session status (session_status)
  stop               Stop game and exit GDB (session_stop)

  step               Advance one game frame (navigate_step)
  bt                 Backtrace + source (navigate_source)

  core dump          Extract core dump (core_dump)
  core load <uuid>   Load core dump by UUID (core_load)
  core reset         Reload last core dump (core_reset)

  processes          List all processes (process_list)
  process watch <ptr> Watch a process (process_watch)

  input read         Read current input state (input_read)
  input write <flag> [drive|drop]
                     Set/clear input flag (input_write)

  ui managers        List UI managers (ui_manager)
  ui select <ptr>    Select a UI manager (ui_manager_select)
  ui list            List elements under manager (ui_list)
    ui invoke <handler> <element_ptr> [args...]
                     Invoke a handler (ui_invoke)

  screenshot [path]  Take screenshot (graphics_screenshot)
  audio list         List audio (audio_list)
  audio listen       Listen to audio (audio_listen)

Raw gdb (local mode only):
  gdb <cmd>          Send a raw MI command to gdb
  break <loc>        Set a breakpoint (-break-insert)
  delete <n>         Delete a breakpoint (-break-delete)
  watch <expr>       Set a watchpoint (-break-watch)

  help               Show this help
  quit               Stop and exit
""")

    def run_loop(self) -> None:
        mode_str = f"local: {self._client.session._executable}" if self._client.is_local else f"attached: {self._client._url}"
        print(f"\n=== verify_cli (MCP protocol) -- {mode_str} ===")
        print("Type 'help' for commands.\n")

        while True:
            try:
                raw = input("mcp> ").strip()
            except EOFError:
                print()
                break

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]

            # -- exit -- #
            if cmd in ("quit", "exit", "q"):
                self._call("session_stop")
                break

            # -- help -- #
            elif cmd in ("help", "?"):
                self.print_help()

            # -- session tools -- #
            elif cmd == "start":
                self._call("session_start")

            elif cmd == "status":
                self._call("session_status")

            elif cmd == "stop":
                self._call("session_stop")

            # -- navigate tools -- #
            elif cmd == "step":
                self._call("navigate_step")

            elif cmd == "bt":
                self._call("navigate_source")

            # -- core tools -- #
            elif cmd == "core":
                if not args:
                    print("  usage: core dump|load <uuid>|reset")
                    continue
                sub = args[0].lower()
                if sub == "dump":
                    self._call("core_dump")
                elif sub == "load":
                    self.do_core_load(args[1:])
                elif sub == "reset":
                    self._call("core_reset")
                else:
                    print(f"  unknown core subcommand: {sub!r}")

            # -- process tools -- #
            elif cmd == "processes":
                self._call("process_list")

            elif cmd == "process":
                if not args:
                    print("  usage: process watch <ptr>")
                    continue
                if args[0].lower() == "watch":
                    if len(args) < 2:
                        print("  usage: process watch <ptr>")
                        continue
                    self._call("process_watch", {"process_ptr": args[1]})
                else:
                    print(f"  unknown process subcommand: {args[0]!r}")

            # -- input tools -- #
            elif cmd == "input":
                if not args:
                    print("  usage: input read|write <flag> [drive|drop]")
                    continue
                sub = args[0].lower()
                if sub == "read":
                    self._call("input_read")
                elif sub == "write":
                    self.do_input_write(args[1:])
                else:
                    print(f"  unknown input subcommand: {sub!r}")

            # -- ui tools -- #
            elif cmd == "ui":
                if not args:
                    print("  usage: ui managers|select <ptr>|list|invoke ...")
                    continue
                sub = args[0].lower()
                rest = args[1:]
                if sub == "managers":
                    self._call("ui_manager")
                elif sub == "select":
                    if not rest:
                        print("  usage: ui select <ptr>")
                        continue
                    self._call("ui_manager_select", {"manager_ptr": rest[0]})
                elif sub == "list":
                    self._call("ui_list")
                elif sub == "invoke":
                    self.do_ui_invoke(rest)
                else:
                    print(f"  unknown ui subcommand: {sub!r}")

            # -- graphics tools -- #
            elif cmd == "screenshot":
                path = args[0] if args else "screen.png"
                self._call("graphics_screenshot", {"output_path": path})

            # -- audio tools (unsupported) -- #
            elif cmd == "audio":
                if not args:
                    print("  usage: audio list|listen")
                    continue
                sub = args[0].lower()
                if sub == "list":
                    self._call("audio_list")
                elif sub == "listen":
                    self._call("audio_listen")
                else:
                    print(f"  unknown audio subcommand: {sub!r}")

            # -- raw gdb commands (local mode only) -- #
            elif cmd == "gdb":
                self._raw_gdb(" ".join(args))

            elif cmd == "break":
                if not args:
                    print("  usage: break <loc>")
                    continue
                self._raw_gdb(f"-break-insert {args[0]}")

            elif cmd == "delete":
                if not args:
                    print("  usage: delete <n>")
                    continue
                self._raw_gdb(f"-break-delete {args[0]}")

            elif cmd == "watch":
                if not args:
                    print("  usage: watch <expr>")
                    continue
                self._raw_gdb(f"-break-watch {args[0]}")

            else:
                print(f"  unknown command: {cmd!r} (type 'help')")


# --------------------------------------------------------------------------- #
#  Entry point                                                                  #
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Interactive MCP protocol shell for verifying the Lavender MCP "
            "tooling against a real GDB-attached binary."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--program",
        type=Path,
        default=None,
        help="Path to the executable to debug (local mode). "
             "If omitted, the executable is loaded from config.json.",
    )
    mode.add_argument(
        "--attach",
        type=str,
        default=None,
        help="URL of a remote MCP server (e.g. http://localhost:8890/mcp/my-session). "
             "In this mode, raw gdb commands are unavailable.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json for local mode (specifies executable + dump location).",
    )
    return parser.parse_args()


def _load_config(config_path: Path | None) -> dict:
    """Load config.json if present."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {"config": {"session": {"executable": ""}, "core": {"dump-location": "/tmp/lav-core-dump/"}}}


def main() -> int:
    args = parse_args()

    # -- Mode: remote (attach) -- #
    if args.attach:
        print(f"=== verify_cli (MCP remote) -- {args.attach} ===")
        client = McpClient(url=args.attach)
        # Quick connectivity check
        tools = client.list_tools()
        if tools:
            print(f"[*] Remote MCP server has {len(tools)} tools: {', '.join(tools)}")
        else:
            print("[!] No tools found on remote MCP server. Is it running?")
            return 1

        cli = VerifyCLI(client)
        try:
            cli.run_loop()
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user.")
        return 0

    # -- Mode: local -- #
    config = _load_config(args.config)
    if args.program:
        executable = str(args.program.resolve())
    else:
        raw_exe = config.get("config", {}).get("session", {}).get("executable", "")
        # Expand env vars (e.g. ${LAVENDER_DIR}) and fall back.
        executable = os.path.expandvars(raw_exe) if raw_exe else ""
        if not executable or not os.path.exists(executable):
            lavender_dir = os.environ.get("LAVENDER_DIR", "")
            if lavender_dir:
                candidate = os.path.join(lavender_dir, "build/sdl/Lavender_Dev")
                if os.path.exists(candidate):
                    executable = candidate
    dump_location = config.get("config", {}).get("core", {}).get("dump-location", "/tmp/lav-core-dump/")

    if not executable:
        print("[!] No executable specified. Use --program <path> or set config.json.")
        return 1

    print(f"=== verify_cli (MCP local) -- {executable} ===")
    session = LavMcpSession(executable=executable, dump_location=dump_location)
    client = McpClient(session=session)
    cli = VerifyCLI(client)

    try:
        cli.run_loop()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
        client.call_tool("session_stop")

    return 0


if __name__ == "__main__":
    sys.exit(main())
