#!/usr/bin/env python3
"""
verify_cli.py — CLI client for the layered Lavender MCP system.

This mirrors the intent of mcp/verify_cli.py but uses the mcp_layered/
architecture (Layers 4-6) instead of the monolithic LavMcpSession.

Usage:
    python3 mcp_layered/verify_cli.py [options]

Options:
    --executable, -e   Game executable path
    --config           Path to config JSON file
    --log              Log file/directory for MCP tool calls
    --no-session-routing  Use single shared session
    --help, -h         Show this help message

REPL commands (type 'help' for list).
"""

import argparse
import os
import sys
import uuid

# Setup import paths
# verify_cli.py is at Projects/Lavender_Dev/mcp_layered/verify_cli.py
# mcp_layered package is at Projects/Lavender_Dev/mcp_layered/
# We need Projects/Lavender_Dev/ in sys.path for "import mcp_layered.X"
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))  # Projects/Lavender_Dev/
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))  # Projects/
sys.path.insert(0, _LAYERED_ROOT)
sys.path.insert(0, _REPO_ROOT)

from mcp_layered.layer_lav_init import create_session
from mcp_layered.layer_lav_mcp import TOOL_DEFINITIONS
from mcp_layered.layer_lav_mcp_server import SessionManager
from mcp_layered.layer_lav_cmd import get_command_alias, CommandError


# -- CLI helpers -- #

def make_tool_client(session_manager):
    """Create a callable that dispatches tools via the session manager."""
    adapter = None

    def call_tool(name, arguments=None):
        nonlocal adapter
        if adapter is None:
            adapter = session_manager.create_session()
        return adapter.dispatch_tool(name, arguments)
    return call_tool


# -- CLI commands -- #

def parse_args():
    parser = argparse.ArgumentParser(
        description="Lavender MCP CLI (layered architecture)",
        add_help=False
    )
    parser.add_argument("--executable", "-e", default=None,
                        help="Game executable path")
    parser.add_argument("--config", default=None,
                        help="Path to config JSON file")
    parser.add_argument("--log", default="/tmp/lav-log/",
                        help="Log file/directory for MCP tool calls")
    parser.add_argument("--no-session-routing", action="store_true",
                        help="Use single shared session")
    parser.add_argument("-h", "--help", action="store_true",
                        help="Show help")
    return parser.parse_args()


def show_help():
    """Show available REPL commands."""
    print("""
Lavender MCP CLI (Layered Architecture)
Commands:
  start              → session_start  (launch game under GDB)
  status             → session_status (check running/halted/crashed)
  stop               → session_stop   (exit GDB)

  step [count]       → navigate_step  (advance one or more game frames)
  bt                 → navigate_source (backtrace + source)

  core dump          → core_dump      (extract coredump)
  core load <uuid>   → core_load      (load coredump by UUID)
  core reset         → core_reset     (reload last coredump)

  processes          → process_list   (list all processes)
  process watch <ptr>→ process_watch  (breakpoint on a process)

  input read         → input_read     (dump input state)
  input write <flag> <drive|drop> → input_write (drive/drop input flag)

  ui list            → ui_list        (list all UI elements across managers)
  ui invoke <handler> <ptr> [extra_args...] → ui_invoke (invoke UI element handler)

  screenshot [path]  → graphics_screenshot (capture screenshot)

  help               Show this help
  quit               Exit
""")


def resolve_log_file(args):
    """Resolve log file path from --log argument."""
    if args.log is None:
        return None
    from pathlib import Path
    p = Path(args.log).expanduser()
    if p.suffix == "" or p.is_dir():
        p.mkdir(parents=True, exist_ok=True)
        return str(p / f"{uuid.uuid4().hex}.jsonl")
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p)


def run_repl(args, session_manager, call_tool):
    """Run the interactive REPL loop."""
    print(f"=== verify_cli (Layered MCP) ===")
    if args.executable:
        print(f"Executable: {args.executable}")
    if args.config:
        print(f"Config: {args.config}")
    print(f"Single session: {args.no_session_routing}")
    print("Type 'help' for commands.")

    while True:
        try:
            cmdline = input("mcp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nquit")
            break

        if not cmdline:
            continue

        parts = cmdline.split()
        cmd = parts[0].lower()
        args_list = parts[1:]

        if cmd == "quit" or cmd == "exit":
            break
        elif cmd == "help":
            show_help()
        elif cmd == "start":
            _call_and_print("session_start", call_tool)
        elif cmd == "status":
            _call_and_print("session_status", call_tool)
        elif cmd == "stop":
            _call_and_print("session_stop", call_tool)
        elif cmd == "step":
            count = int(args_list[0]) if args_list else 1
            _call_and_print("navigate_step", call_tool, {"count": count})
        elif cmd == "bt":
            _call_and_print("navigate_source", call_tool)
        elif cmd == "core":
            if len(args_list) < 1:
                print("  usage: core dump|load <uuid>|reset")
                continue
            sub = args_list[0]
            if sub == "dump":
                _call_and_print("core_dump", call_tool)
            elif sub == "load" and len(args_list) >= 2:
                _call_and_print("core_load", call_tool, {"uuid": args_list[1]})
            elif sub == "reset":
                _call_and_print("core_reset", call_tool)
            else:
                print(f"  unknown core subcommand: {sub}")
        elif cmd == "processes":
            _call_and_print("process_list", call_tool)
        elif cmd == "process" and len(args_list) >= 2:
            if args_list[0] == "watch":
                _call_and_print("process_watch", call_tool, {"process_ptr": args_list[1]})
        elif cmd == "input":
            if len(args_list) < 1:
                print("  usage: input read|write <flag> <drive|drop>")
                continue
            sub = args_list[0]
            if sub == "read":
                _call_and_print("input_read", call_tool)
            elif sub == "write" and len(args_list) >= 3:
                _call_and_print("input_write", call_tool,
                                {"flag": args_list[1], "action": args_list[2]})
        elif cmd == "ui":
            if len(args_list) < 1:
                print("  usage: ui list|invoke <handler> <ptr> [extra_args]")
                continue
            sub = args_list[0]
            if sub == "list":
                _call_and_print("ui_list", call_tool)
            elif sub == "invoke" and len(args_list) >= 3:
                # ui invoke <handler> <element_ptr> [extra_args...]
                handler = args_list[1]
                element_ptr = args_list[2]
                kwargs = {"element_ptr": element_ptr, "handler": handler}
                # Handle extra args for receive_drop and typed
                if handler == "receive_drop" and len(args_list) >= 4:
                    kwargs["dropped_ptr"] = args_list[3]
                elif handler == "typed" and len(args_list) >= 4:
                    kwargs["symbol"] = args_list[3]
                _call_and_print("ui_invoke", call_tool, kwargs)
        elif cmd == "screenshot":
            path = args_list[0] if args_list else None
            _call_and_print("graphics_screenshot", call_tool,
                            {"output_path": path} if path else None)
        else:
            print(f"  unknown command: '{cmd}' (type 'help')")

    # Cleanup
    session_manager.close()


def _call_and_print(name, call_tool, arguments=None):
    """Call a tool and print the result."""
    try:
        result = call_tool(name, arguments)
        print(result)
    except CommandError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


def main():
    args = parse_args()

    if args.help:
        show_help()
        return 0

    log_file = resolve_log_file(args)
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        print(f"Logging MCP tool calls to: {log_file}")

    # Create session manager via the layered architecture
    session_manager = SessionManager(
        use_single_session=args.no_session_routing,
        default_config_path=args.config,
        default_executable=args.executable,
        log_file=log_file,
    )

    # Create the tool client (wrapping dispatch_tool)
    call_tool = make_tool_client(session_manager)

    # Run the REPL
    try:
        run_repl(args, session_manager, call_tool)
    except KeyboardInterrupt:
        session_manager.close()
        print("\nInterrupted.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
