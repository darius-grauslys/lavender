#!/usr/bin/env python3
"""
FILE IS OBSOLETE.
harness_qa.py is obsolete. It is kept as a historic artifact of the current
harness.

harness_qa.py — Agentic QA harness for executing and interrogating programs.

Pipeline (skeleton):
    1. Parse --program <path-to-executable> from the CLI.
    2. Start the target executable with subprocess.Popen, obtaining its PID,
       then attach pygdbmi's GdbController to that PID via ``-target-attach``.
       If ptrace is restricted (common in sandboxed / container environments),
       fall back to loading the binary into gdb directly and running it via
       ``-exec-run --start`` so gdb controls the entire process lifecycle.
    3. [Future] Spin up a langchain agent (LLM + tools) that can step, read
       memory, inspect variables, and drive the debug session autonomously.

Usage:
    python3 harness_qa.py --program /path/to/executable
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
import threading
import time
from enum import IntEnum
from pathlib import Path

from pygdbmi.gdbcontroller import GdbController


# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #
GDB_CMD_BASE = ["gdb", "--nx", "--quiet", "--interpreter=mi3"]


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Agentic QA harness: launches a binary and attaches GDB "
                    "(via pygdbmi) for autonomous debugging with langchain.",
    )
    parser.add_argument(
        "--program",
        type=Path,
        required=True,
        help="Path to the executable to launch and debug.",
    )
    return parser.parse_args()


# --------------------------------------------------------------------------- #
#  Mode 2 — Run inside gdb   (fallback when ptrace is restricted)
# --------------------------------------------------------------------------- #
def run_inside_gdb(gdbmi: GdbController, program: Path) -> None:
    """
    Load *program* into *gdbmi* and start it with ``-exec-run --start``.

    The ``--start`` flag stops execution at the beginning of ``main`` so the
    agent has a deterministic initial state.
    """
    # Load symbols / set the executable.
    resp = gdbmi.write(f"-file-exec-and-symbols {program}")
    print(f"[*] file-exec-and-symbols: {resp}")
    for rec in resp:
        if rec.get("type") == "result" and rec.get("message") == "error":
            raise RuntimeError(
                f"GDB failed to load symbols for {program}: {rec}"
            )

    # Start the program; it will stop at the entry to main.
    resp = gdbmi.write("-exec-run --start")
    print(f"[*] exec-run --start response: {resp}")
    for rec in resp:
        if rec.get("type") == "result" and rec.get("message") == "error":
            raise RuntimeError(
                f"GDB failed to start program: {rec}"
            )
    print(f"[*] Program started under gdb, stopped at main()")


# --------------------------------------------------------------------------- #
#  Debug-input helpers
#
#  These mirror the gdb-callable signatures declared in
#  core/include/debug/drive_input.h. Each helper:
#    1. pushes the "main" (innermost) frame via push_main_frame(),
#    2. resolves &game as the Game *p_game argument,
#    3. issues the corresponding `call ...` through gdb,
#    4. pops back to the caller's frame via pop_frame().
#
#  The bit-flag definitions below intentionally duplicate (a DRY-violating
#  mirror of) the INPUT_* macros in core/include/platform_defaults.h so the
#  harness can build flag bitmasks without parsing the C headers.
# --------------------------------------------------------------------------- #


class Input_Flags__u32(IntEnum):
    NONE = 0
    FORWARD = 1 << 0
    LEFT = 1 << 1
    RIGHT = 1 << 2
    BACKWARD = 1 << 3
    GAME_SETTINGS = 1 << 4
    LOCKON = 1 << 5
    USE = 1 << 6
    USE_SECONDARY = 1 << 7
    EXAMINE = 1 << 8
    CONSUME = 1 << 9
    TURN_RIGHT = 1 << 10
    TURN_LEFT = 1 << 11
    CLICK = 1 << 12


def _vector__3i32_literal(x: int, y: int, z: int) -> str:
    """Render a (Vector__3i32){x, y, z} compound-literal for gdb."""
    return f"(Vector__3i32){{{x}, {y}, {z}}}"


_CALL_VALUE_RE = re.compile(
    r"=\s*(?:\([^)]*\)\s*)?(0x[0-9a-fA-F]+)"
)


def _extract_call_value(resp: list) -> str | None:
    """Pull a hex value out of a ``call`` console-stream response.

    pygdbmi's ``-interpreter-exec console "call ..."`` only reports a
    function's return value as console output (e.g.
    ``$1 = (Process *) 0x55558018 <f>``); the parsed MI result record's
    payload is ``None``. This scans the console stream records and returns
    the address, or ``None`` if nothing was found.
    """
    for rec in resp:
        payload = rec.get("payload")
        if rec.get("type") == "console" and payload:
            m = _CALL_VALUE_RE.search(payload)
            if m:
                return m.group(1)
    return None


class GDBFrameController:
    """
    Shared gdb plumbing for the debug-input / debug-ui helpers:

    * a small stack of saved gdb frame levels, plus push/pop helpers,
    * low-level wrappers over pygdbmi: ``_call`` (the CLI ``call``),
      ``_exec`` (arbitrary console statements such as ``set $x = ...``)
      and ``_eval`` (``-data-evaluate-expression``, the clean way to read a
      value because pygdbmi puts it in the result payload rather than a
      console stream record).
    """

    def __init__(self, gdbmi: GdbController) -> None:
        self._gdbmi = gdbmi
        self._frame_stack: list[int] = []

    # -- frame management --------------------------------------------------- #

    def _current_frame_level(self) -> int:
        resp = self._gdbmi.write("-stack-info-frame")
        for rec in resp:
            if rec.get("type") == "result" and rec.get("message") == "done":
                payload = rec.get("payload") or {}
                frame = payload.get("frame") or {}
                return int(frame.get("level", 0))
        return 0

    def push_frame(self, n: int) -> None:
        """Save the current frame and select frame *n*."""
        self._frame_stack.append(self._current_frame_level())
        self._gdbmi.write(f"-stack-select-frame {n}")

    def push_main_frame(self) -> None:
        """Select the innermost (main) frame after saving the current one."""
        self.push_frame(0)

    def pop_frame(self) -> None:
        """Restore the most recently saved frame."""
        if not self._frame_stack:
            return
        level = self._frame_stack.pop()
        self._gdbmi.write(f"-stack-select-frame {level}")

    # -- low level gdb primitives ------------------------------------------ #

    def _call(self, expr: str) -> list:
        """Invoke *expr* as a gdb ``call`` expression; return the response.

        Note: a ``call``'s return value is *not* placed in the parsed MI
        result payload (it shows up only as console output), so callers that
        need the value should use ``_eval`` instead.
        """
        return self._gdbmi.write(f'-interpreter-exec console "call {expr}"')

    def _exec(self, stmt: str) -> list:
        """Run an arbitrary gdb console statement (e.g. ``set $x = ...``)."""
        return self._gdbmi.write(f'-interpreter-exec console "{stmt}"')

    def _eval(self, expr: str) -> str | None:
        """Evaluate *expr* via ``-data-evaluate-expression``.

        Returns the printed value (in ``payload['value']``) or ``None``.
        This is the reliable way to read a value back from gdb as JSON.
        """
        resp = self._gdbmi.write(f"-data-evaluate-expression {expr}")
        for rec in resp:
            if rec.get("type") == "result" and rec.get("message") == "done":
                return (rec.get("payload") or {}).get("value")
        return None


# --------------------------------------------------------------------------- #
#  Debug-input helpers
# --------------------------------------------------------------------------- #


class DebugInputDriver(GDBFrameController):
    """
    Drives the in-game Input through gdb by invoking the
    debug_drive_* functions declared in drive_input.h.
    """

    # -- per-signature helpers (drive_input.h) ------------------------------ #

    def drive_input__flag(self, input_flag: Input_Flags__u32) -> None:
        """debug_drive_input__flag(&game, input_flag)"""
        self.push_main_frame()
        try:
            self._call(
                f"debug_drive_input__flag(&game, {int(input_flag)})"
            )
        finally:
            self.pop_frame()

    def drop_input__flag(self, input_flag: Input_Flags__u32) -> None:
        """debug_drop_input__flag(&game, input_flag)

        Clears a flag. Implemented in drive_input.c though not declared in
        drive_input.h; provided here so input can be toggled off again.
        """
        self.push_main_frame()
        try:
            self._call(
                f"debug_drop_input__flag(&game, {int(input_flag)})"
            )
        finally:
            self.pop_frame()

    def drive_input__mouse_pos(self, x: int, y: int, z: int = 0) -> None:
        """debug_drive_input__mouse_pos(&game, (Vector__3i32){x, y, z})"""
        self.push_main_frame()
        try:
            vec = _vector__3i32_literal(x, y, z)
            self._call(
                f"debug_drive_input__mouse_pos(&game, {vec})"
            )
        finally:
            self.pop_frame()

    def dispatch_click(self, x: int, y: int, z: int = 0) -> str | None:
        """debug_dispatch_click(&game, (Vector__3i32){x, y, z}) -> Process *

        Returns the hex address of the spawned Process * (e.g. ``0x5555...``)
        or ``None`` if it could not be extracted. The address lets you set a
        breakpoint on the spawned ``m_debug_process__click``; the documented
        workflow is to breakpoint ``complete_process()`` instead.

        Note: with the ``call`` CLI form the return value only appears in the
        console stream (``$N = (Process *) 0x...``), so it is parsed out here.
        """
        self.push_main_frame()
        try:
            vec = _vector__3i32_literal(x, y, z)
            resp = self._call(
                f"debug_dispatch_click(&game, {vec})"
            )
            return _extract_call_value(resp)
        finally:
            self.pop_frame()


# --------------------------------------------------------------------------- #
#  Debug-ui helpers
# --------------------------------------------------------------------------- #


# Field layout of DEBUG_UI_Scanner (see core/include/debug/debug_ui.h). We
# mirror the names so callers and the harness agree; the C side is the source
# of truth. Member access uses '.' because the scanner is captured by value
# into a gdb convenience variable (debug_get_ui_scanner returns a struct, not
# a pointer).
DEBUG_UI_SCANNER_FIELDS = (
    "p_ui_context",
    "p_ui_manager__current",
    "p_ptr_ui_element__current",
    "m_next_manager",
    "m_next_element",
)


_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")


def parse_hex(value: str | None) -> str | None:
    """Extract the leading hex address from a gdb value string.

    e.g. "0x5555555551c3 <adv_element>" -> "0x5555555551c3"
         "0x11223344"                     -> "0x11223344"
    """
    if not value:
        return None
    m = _HEX_RE.search(value)
    return m.group(0) if m else None


class DebugUIScannerExplorer(GDBFrameController):
    """
    Inspects UI state through debug_ui.h's ``debug_get_ui_scanner``.

    Typical loop (game halted under gdb, e.g. in the render loop):

        explorer = DebugUIScannerExplorer(gdbmi)
        explorer.get_ui_scanner()                 # captures $debug_ui_scanner
        explorer.read_field("p_ui_manager__current")
        explorer.read_fields()                    # all DEBUG_UI_Scanner fields
        explorer.next_element()                   # advance via m_next_element
        explorer.next_manager()                   # advance via m_next_manager

    The scanner is captured by value into the gdb convenience variable
    ``$debug_ui_scanner`` (debug_get_ui_scanner returns a struct). Fields are
    read with ``-data-evaluate-expression "$debug_ui_scanner.<field>"``, which
    is the reliable way to get a value back as JSON (a ``call`` would bury it
    in a console stream record).

    Note: debug_ui.h is guarded by ``#ifndef NDEBUG``; the symbols are absent
    in release builds, in which case these calls will error at the gdb prompt.
    """

    SCANNER_VAR = "$debug_ui_scanner"

    # m_DEBUG_UI_Scanner_Func, the type of m_next_manager / m_next_element.
    # Used to cast-and-call the function pointer (see next_element below).
    _FUNC_PTR_TYPE = "m_DEBUG_UI_Scanner_Func"

    def get_ui_scanner(self) -> str | None:
        """Call ``debug_get_ui_scanner(&game)`` and capture the struct.

        Executes (in the main frame) ``set $debug_ui_scanner =
        debug_get_ui_scanner(&game)`` and returns the captured struct's
        printed representation (or ``None`` on failure).
        """
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = debug_get_ui_scanner(&game)"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)

    def read_field(self, field: str) -> str | None:
        """Return the gdb-printed value of ``$debug_ui_scanner.<field>``.

        Use :func:`parse_hex` to reduce pointer-typed results to their address.
        """
        if field not in DEBUG_UI_SCANNER_FIELDS:
            raise ValueError(f"unknown DEBUG_UI_Scanner field: {field!r}")
        return self._eval(f"{self.SCANNER_VAR}.{field}")

    def read_fields(self) -> dict[str, str | None]:
        """Snapshot every DEBUG_UI_Scanner field into a dict."""
        return {f: self.read_field(f) for f in DEBUG_UI_SCANNER_FIELDS}

    def next_element(self) -> str | None:
        """Advance the scanner via ``m_next_element`` and return the new
        struct's printed representation.

        gdb cannot call a function pointer that lives inside a convenience
        variable (it errors: "Attempt to take address of value not located in
        memory"). We work around this by casting the pointer to its named type
        before calling, which makes it a standalone call expression::

            set $debug_ui_scanner =
                ((m_DEBUG_UI_Scanner_Func)$debug_ui_scanner.m_next_element)()
        """
        return self._advance("m_next_element")

    def next_manager(self) -> str | None:
        """Advance the scanner via ``m_next_manager``. See :meth:`next_element`."""
        return self._advance("m_next_manager")

    def _advance(self, field: str) -> str | None:
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = "
                f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.{field})()"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main() -> int:
    args = parse_args()
    program: Path = args.program.resolve()
    print(f"=== harness_qa — target: {program} ===")

    child: subprocess.Popen | None = None
    gdbmi: GdbController | None = None

    try:
        # --- Start gdb controller -------------------------------------------
        gdbmi = GdbController(command=GDB_CMD_BASE)

        # ---  run inside gdb ------------------------------------------------
        run_inside_gdb(gdbmi, program)
        print("[*] Mode: run-inside-gdb (ptrace restricted)")

        # --- The foundation is now in place. --------------------------------
        # Next steps (to be implemented):
        #   a. Build langchain tools wrapping gdb MI operations
        #      (step, continue, read memory, read registers, etc.)
        #   b. Instantiate an LLM agent with those tools.
        #   c. Feed the agent the program / binary info and let it drive
        #      the debug session toward a goal (e.g. "find the crash").
        #
        # For now we just keep the session alive so the user can experiment
        # interactively with the gdbmi stream.

        print("[*] Entering gdbmi read-loop.  Press Ctrl-C to detach & exit.")

        # We cannot rely on KeyboardInterrupt here because pygdbmi's
        # internal ``select.select()`` call swallows SIGINT (PEP 475 retries)
        # and then raises ``GdbTimeoutError`` before the signal can propagate.
        # Instead we install a flag-based handler and poll with a short timeout.
        stop_event = threading.Event()

        def _sigint_handler(signum, frame):
            stop_event.set()

        old_handler = signal.signal(signal.SIGINT, _sigint_handler)
        try:
            while not stop_event.is_set():
                # raise_error_on_timeout=False keeps the loop alive; we just get
                # an empty list when there's nothing new from gdb.
                responses = gdbmi.get_gdb_response(
                    timeout_sec=0.5, raise_error_on_timeout=False
                )
                for rec in responses:
                    print(rec)
        finally:
            signal.signal(signal.SIGINT, old_handler)

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        # --- Teardown ---
        if gdbmi is not None:
            print("[*] Detaching / exiting gdb.")
            gdbmi.exit()
        if child is not None:
            print(f"[*] Terminating child process (pid={child.pid}).")
            try:
                os.killpg(os.getpgid(child.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            child.wait(timeout=5)

    return 0


if __name__ == "__main__":
    sys.exit(main())
