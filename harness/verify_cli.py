#!/usr/bin/env python3
"""
verify_cli.py — Interactive CLI for a human operator to drive the harness.

This launches a program inside GDB (via pygdbmi), stops at ``main``, and
hands you a REPL where you can exercise the harness tooling as if you were
an agent:

    python3 -m harness.verify_cli --program /path/to/executable

REPL commands:
    load <path>        load a binary (file-exec-and-symbols) [initial load]
    start              start the program (--start, stops at main)
    run                continue execution
    step               step one instruction
    continue           continue from a breakpoint / signal
    bt                 print backtrace
    info args          gdb ``info args``
    break <loc>        set a breakpoint (e.g. ``break main``)
    delete <n>         delete breakpoint n
    watch <expr>       set a watchpoint
    gdb <cmd>          send a raw MI command (e.g. ``gdb -data-evaluate-expression $pc``)
    help               show all commands
    quit               detach and exit

Harness tooling shortcuts:
    input driver <method> [args...]
        Drive the input driver. Examples:
            input driver drive_input__flag CLICK
            input driver drop_input__flag CLICK
            input driver drive_input__mouse_pos 10 20 5
            input driver dispatch_click 7 8

    scanner ui
        Create / reuse the DebugUIScanner and print its table.

    scanner entity
        Create / reuse the DebugEntityScanner and print its table.

    scanner scene
        Create / reuse the DebugSceneScanner and print its table.

    ui utils <subcommand> [args...]
        Drive UI element handler fields (requires frame: poll_ui_manager__update).
        Examples:
            ui utils refresh
            ui utils list
            ui utils clicked 0x2000
            ui utils typed 0x2000 A
            ui utils receive_drop 0x2000 0x2100
            ui utils transformed 0x2000  (stub — not implemented)
        Precondition: the current gdb frame MUST be poll_ui_manager__update,
        where p_game and p_gfx_window are local variables.

    demeters <substring>
        Run find_demeters on the last-used scanner table.

    nav step [func] [timeout]
        Step to the end of a frame by setting a temporary breakpoint
        at `func` (default: manage_game__post_render) and running until
        it fires. Default timeout is 5 seconds (use 10-15s for SDL2 builds
        that need GL context initialization). Returns OK if the breakpoint
        was hit, or TIMEOUT if the target wasn't reached (catches infinite
        loops / breakpoint storms / game exit).

The scanner subcommands print a JSON table and the demeter paths; the
``input driver`` subcommand lets you try the input helpers against the live
target.  This is designed for human-operator verification of the harness
against a real (NDEBUG-disabled) Lavender binary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from pathlib import Path

from pygdbmi.gdbcontroller import GdbController

from .gdb_frame_controller import GDBFrameController
from .debug_input_driver import DebugInputDriver
from .debug_scanner_ui import DebugUIScanner
from .debug_scanner_entity import DebugEntityScanner
from .debug_scanner_scene import DebugSceneScanner
from .debug_ui_utils import DebugUIUtils
from .gdb_nav_utils import step_frame
from .lavender_debug import Input_Flags__u32

# --- gdb launch flags --------------------------------------------------------- #
GDB_CMD_BASE = ["gdb", "--nx", "--quiet", "--interpreter=mi3"]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive CLI for verifying the harness against a "
                    "real GDB-attached binary.",
    )
    parser.add_argument(
        "--program",
        type=Path,
        required=True,
        help="Path to the executable to launch and debug.",
    )
    return parser.parse_args()


# --- response helpers -------------------------------------------------------- #

def _resp_messages(resp):
    """Yield (type, message) tuples from a pygdbmi response list."""
    for rec in resp:
        if isinstance(rec, dict):
            yield rec.get("type", "?"), rec.get("message", "")


def _first_value(resp):
    """Return payload['value'] from the first done result, or None."""
    for rec in resp:
        if isinstance(rec, dict) and rec.get("type") == "result" and rec.get("message") == "done":
            payload = rec.get("payload") or {}
            return payload.get("value")
    return None


def _print_resp(resp):
    """Pretty-print a pygdbmi response."""
    for rec in resp:
        if isinstance(rec, dict):
            rtype = rec.get("type", "?")
            msg = rec.get("message", "")
            payload = rec.get("payload")
            if rtype == "console" or rtype == "target":
                print(f"  [console] {payload}")
            elif payload is not None:
                print(f"  [{rtype}] {msg}: {payload}")
            else:
                print(f"  [{rtype}] {msg}")


# --- session ----------------------------------------------------------------- #

class VerifyCLI:
    """Interactive CLI session wrapping a GDBController and harness objects."""

    def __init__(self, gdbmi: GdbController, program: Path) -> None:
        self._gdbmi = gdbmi
        # The GDBFrameController is just frame management + primitives; the
        # harness drivers subclass it, so we hand them the same gdbmi handle.
        self._fc = GDBFrameController(gdbmi)
        self._input_driver: DebugInputDriver | None = None
        self._current_scanner = None
        self._ui_utils: DebugUIUtils | None = None
        self._program = program

    # -- gdb plumbing --------------------------------------------------------- #

    def send(self, cmd: str):
        """Send a raw write() to gdb and return the response."""
        return self._gdbmi.write(cmd)

    def safe_gdb(self, cmd: str) -> None:
        """Send a raw MI command, printing the result."""
        print(f">>> gdb: {cmd}")
        resp = self._gdbmi.write(cmd)
        _print_resp(resp)

    # -- input driver --------------------------------------------------------- #

    def get_input_driver(self) -> DebugInputDriver:
        if self._input_driver is None:
            self._input_driver = DebugInputDriver(self._gdbmi)
        return self._input_driver

    # -- scanner selection ---------------------------------------------------- #

    def make_scanner(self, name: str):
        """Instantiate the named scanner subclass."""
        if name == "ui":
            cls = DebugUIScanner
        elif name == "entity":
            cls = DebugEntityScanner
        elif name == "scene":
            cls = DebugSceneScanner
        else:
            print(f"  unknown scanner name: {name!r} (use ui|entity|scene)")
            return None

        scanner = cls(self._gdbmi)
        # Capture the scanner struct by value first.
        repr_str = scanner.get_scanner()
        if repr_str is None:
            print("  get_scanner() returned None — check the debug symbols.")
            return None
        print(f"  scanner captured: {repr_str[:200]}")
        self._current_scanner = scanner
        return scanner

    # -- command dispatch ----------------------------------------------------- #

    def do_input_driver(self, args: list[str]) -> None:
        """Run an input-driver method with parsed args."""
        if not args:
            print("  usage: input driver <method> [args...]")
            print("    methods: drive_input__flag, drop_input__flag, "
                  "drive_input__mouse_pos, dispatch_click")
            return

        method_name = args[0]
        rest = args[1:]
        driver = self.get_input_driver()

        method = getattr(driver, method_name, None)
        if method is None or not callable(method):
            print(f"  no such method: {method_name!r}")
            return

        try:
            if method_name in ("drive_input__flag", "drop_input__flag"):
                if not rest:
                    print("  usage: input driver <method> <FLAG_NAME>")
                    print(f"    flags: {[f.name for f in Input_Flags__u32]}")
                    return
                flag_name = rest[0]
                flag = getattr(Input_Flags__u32, flag_name, None)
                if flag is None:
                    print(f"  unknown flag: {flag_name!r}")
                    print(f"    flags: {[f.name for f in Input_Flags__u32]}")
                    return
                method(flag)
                print("  OK")

            elif method_name == "drive_input__mouse_pos":
                if len(rest) < 2:
                    print("  usage: input driver drive_input__mouse_pos <x> <y> [z]")
                else:
                    x, y = int(rest[0]), int(rest[1])
                    z = int(rest[2]) if len(rest) > 2 else 0
                    method(x, y, z)
                    print("  OK")

            elif method_name == "dispatch_click":
                if len(rest) < 2:
                    print("  usage: input driver dispatch_click <x> <y> [z]")
                else:
                    x, y = int(rest[0]), int(rest[1])
                    z = int(rest[2]) if len(rest) > 2 else 0
                    result = method(x, y, z)
                    if result is not None:
                        print(f"  spawned Process *: {result}")
                    else:
                        print("  dispatch_click returned None (no return value found)")

            else:
                print(f"  unhandled method: {method_name!r}")
        except Exception:
            import traceback
            traceback.print_exc()

    def do_scanner(self, args: list[str]) -> None:
        """Create / reuse a scanner and print its JSON table."""
        if not args:
            print("  usage: scanner <ui|entity|scene>")
            return
        name = args[0].lower()
        scanner = self.make_scanner(name)
        if scanner is None:
            return
        try:
            table = scanner.get_table()
            print(json.dumps(table, indent=2, sort_keys=False))
            print(f"  fields: {scanner.get_fields()}")
        except Exception:
            import traceback
            traceback.print_exc()

    def do_demeters(self, args: list[str]) -> None:
        """Run find_demeters on the current scanner's table."""
        if self._current_scanner is None:
            print("  no scanner active — run 'scanner ui' (or entity/scene) first.")
            return
        substring = args[0] if args else ""
        try:
            results = self._current_scanner.find_demeters(substring)
            if results:
                for d in results:
                    print(f"  {d}")
            else:
                print("  (no matches)")
        except Exception:
            import traceback
            traceback.print_exc()

    def do_ui_utils(self, args: list[str]) -> None:
        """Drive UI element handler fields via DebugUIUtils."""
        if self._ui_utils is None:
            self._ui_utils = DebugUIUtils(self._gdbmi)
        try:
            handled = self._ui_utils.do_command(args)
            if not handled:
                print(f"  unknown ui utils subcommand: {args[0]!r}")
        except RuntimeError as e:
            print(f"  [error] {e}")
        except ValueError as e:
            print(f"  [error] {e}")
        except Exception:
            import traceback
            traceback.print_exc()

    def do_get_field(self, args: list[str]) -> None:
        """Get a field by demeter dot-path from the current scanner."""
        if self._current_scanner is None:
            print("  no scanner active — run 'scanner ui' (or entity/scene) first.")
            return
        if not args:
            print("  usage: getfield <demeter>")
            return
        demeter = args[0]
        try:
            value = self._current_scanner.get_field(demeter)
            if isinstance(value, (dict, list)):
                print(json.dumps(value, indent=2, sort_keys=False))
            else:
                print(f"  {value!r}")
        except KeyError as e:
            print(f"  KeyError: {e}")

    # -- REPL ------------------------------------------------------------------ #

    def print_help(self) -> None:
        print("""
Commands:
  load <path>              Load a binary (file-exec-and-symbols)
  start                    Start the program (--start, stops at main)
  run                      Continue execution from a stop
  step                     Step one (instruction)
  continue                 Continue from a breakpoint/signal
  bt                       Print backtrace
  info args                Print function arguments
  break <loc>              Set a breakpoint (e.g. 'break main')
  delete <n>               Delete breakpoint n
  watch <expr>             Set a watchpoint
  gdb <cmd>                Send a raw MI command
    input driver ...         Drive the input driver (see sub-commands)
    scanner <ui|entity|scene>  Create a scanner and print its table
    ui utils <subcommand> ...  Drive UI element handlers (see sub-commands)
    demeters <substring>       find_demeters on the current scanner
    nav step [func] [timeout]   Step to end of frame (default: manage_game__post_render)
    getfield <demeter>         get_field by dot-path on the current scanner
    help                     Show this help
    quit                     Detach and exit
""")

    def run_loop(self) -> None:
        """Interactive read-eval-print loop."""
        print(f"\n=== verify_cli — target: {self._program} ===")
        print("Type 'help' for commands.\n")

        # The program is already loaded and started by main(); this loop is
        # for interactive experimentation.
        while True:
            try:
                raw = input("harness> ").strip()
            except EOFError:
                print()
                break

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ("quit", "exit", "q"):
                break

            elif cmd == "help" or cmd == "?":
                self.print_help()

            elif cmd == "load":
                if not args:
                    print("  usage: load <path>")
                    continue
                path = args[0]
                print(f">>> load: {path}")
                resp = self._gdbmi.write(f"-file-exec-and-symbols {path}")
                _print_resp(resp)

            elif cmd == "start":
                print(">>> start")
                resp = self._gdbmi.write("-exec-run --start")
                _print_resp(resp)

            elif cmd == "run":
                print(">>> continue")
                resp = self._gdbmi.write("-exec-continue")
                _print_resp(resp)

            elif cmd == "continue":
                print(">>> continue")
                resp = self._gdbmi.write("-exec-continue")
                _print_resp(resp)

            elif cmd == "step":
                print(">>> step")
                resp = self._gdbmi.write("-exec-step")
                _print_resp(resp)

            elif cmd == "bt":
                print(">>> -stack-list-frames")
                resp = self._gdbmi.write("-stack-list-frames")
                _print_resp(resp)

            elif cmd == "info":
                # pass-thru to gdb console
                rest = " ".join(args)
                print(f">>> console: info {rest}")
                resp = self._gdbmi.write(f'-interpreter-exec console "info {rest}"')
                _print_resp(resp)

            elif cmd == "break":
                if not args:
                    print("  usage: break <loc>")
                    continue
                loc = args[0]
                print(f">>> break {loc}")
                resp = self._gdbmi.write(f"-break-insert {loc}")
                _print_resp(resp)

            elif cmd == "delete":
                if not args:
                    print("  usage: delete <n>")
                    continue
                bkpt = args[0]
                print(f">>> delete {bkpt}")
                resp = self._gdbmi.write(f"-break-delete {bkpt}")
                _print_resp(resp)

            elif cmd == "watch":
                if not args:
                    print("  usage: watch <expr>")
                    continue
                expr = args[0]
                print(f">>> watch {expr}")
                resp = self._gdbmi.write(f"-break-watch {expr}")
                _print_resp(resp)

            elif cmd == "gdb":
                rest = " ".join(args)
                if not rest:
                    print("  usage: gdb <mi-command>")
                    continue
                self.safe_gdb(rest)

            elif cmd == "input":
                # subcommand: driver ...
                if not args:
                    print("  usage: input driver <method> [args...]")
                    continue
                if args[0].lower() == "driver":
                    self.do_input_driver(args[1:])
                else:
                    print(f"  unknown input subcommand: {args[0]!r}")

            elif cmd == "ui":
                # subcommand: utils ...
                if not args:
                    print("  usage: ui utils <subcommand> [args...]")
                    continue
                if args[0].lower() == "utils":
                    self.do_ui_utils(args[1:])
                else:
                    print(f"  unknown ui subcommand: {args[0]!r}")

            elif cmd == "scanner":
                self.do_scanner(args)

            elif cmd == "demeters":
                self.do_demeters(args)

            elif cmd == "nav":
                if not args:
                    print("  usage: nav step [func] [timeout]")
                    print("    step <func> <timeout>  step to end-of-frame breakpoint")
                    continue
                subcmd = args[0].lower()
                if subcmd == "step":
                    func_name = args[1] if len(args) > 1 else "manage_game__post_render"
                    timeout = float(args[2]) if len(args) > 2 else 5.0
                    print(f">>> nav step: breakpoint at {func_name}, timeout {timeout}s")
                    try:
                        ok = step_frame(self._gdbmi, func_name, timeout)
                        if ok:
                            print(f"  OK — stopped at {func_name}")
                        else:
                            print(f"  TIMEOUT — did not reach {func_name} within {timeout}s")
                    except Exception:
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"  unknown nav subcommand: {subcmd!r}")

            elif cmd == "getfield":
                self.do_get_field(args)

            else:
                print(f"  unknown command: {cmd!r} (type 'help')")


# --- entry point ------------------------------------------------------------- #

def main() -> int:
    args = parse_args()
    program: Path = args.program.resolve()
    print(f"=== verify_cli — target: {program} ===")

    gdbmi: GdbController | None = None

    try:
        gdbmi = GdbController(command=GDB_CMD_BASE)

        # 1) Load the binary
        print("[*] Loading symbols...")
        resp = gdbmi.write(f"-file-exec-and-symbols {program}")
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result" and rec.get("message") == "error":
                print(f"[!] GDB failed to load symbols for {program}: {rec}")
                return 1
        print("[*] Symbols loaded.")

        # 2) Start at main (--start stops there)
        print("[*] Starting program (stopping at main)...")
        resp = gdbmi.write("-exec-run --start")
        for rec in resp:
            if isinstance(rec, dict) and rec.get("type") == "result" and rec.get("message") == "error":
                # Could be "Program is not being run" or similar; try just running
                print(f"  note: {rec}")
        print("[*] Program stopped at main().")

        # 3) Enter the interactive REPL
        cli = VerifyCLI(gdbmi, program)
        cli.run_loop()

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        if gdbmi is not None:
            print("[*] Detaching / exiting gdb.")
            gdbmi.exit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
