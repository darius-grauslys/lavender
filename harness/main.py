"""
main.py — CLI entry point, session setup, and interactive read-loop.

Pipeline:
  1. Parse --program <path-to-executable> from the CLI.
  2. Start a pygdbmi GdbController, load the binary via ``-file-exec-and-symbols``
     and start it with ``-exec-run --start`` so gdb owns the process and
     stops at ``main``.
  3. Enter an interactive gdbmi read-loop so the user can experiment.
  4. On exit (Ctrl-C or error), detach / exit gdb cleanly.

Usage:
  python3 -m harness --program /path/to/executable
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

from pygdbmi.gdbcontroller import GdbController


GDB_CMD_BASE = ["gdb", "--nx", "--quiet", "--interpreter=mi3"]


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


def main() -> int:
    """Orchestrate the debug session: setup → read-loop → teardown."""
    args = parse_args()
    program: Path = args.program.resolve()
    print(f"=== harness_qa — target: {program} ===")

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
                # raise_error_on_timeout=False keeps the loop alive; we just
                # get an empty list when there's nothing new from gdb.
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
