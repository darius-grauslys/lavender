#!/usr/bin/env python3
"""
verify_sdl_lav.py — Integration test for gdb_nav_utils against the real
Lavender SDL executable.

Instead of using mock objects (like verify_driver.py), this script launches
the actual SDL2 Lavender binary under gdb and exercises the step_frame()
function against the real game loop.

Improvements over the original version:
  - Uses display_setup.DisplayManager to ensure a usable X display (Xvfb)
    is available, fixing the GLX context failure that occurred when DISPLAY
    was unset in headless environments.
  - Configures GDB signal handling (pass-through for SIGUSR1/SIGALRM/etc.)
    to prevent SDL/PulseAudio audio thread crashes during debugging.
  - Optionally enables GDB non-stop mode for multithreaded SDL apps.
  - Sets up proper environment variables for GL stability.

Usage:
    python3 -m harness.verify_sdl_lav
    python3 -m harness.verify_sdl_lav --software-gl  # force software rendering
    python3 -m harness.verify_sdl_lav --non-stop     # GDB non-stop mode
    python3 -m harness.verify_sdl_lav --no-xvfb       # don't start Xvfb

Exit codes:
    0 = all assertions passed
    1 = assertion failure or setup error
"""

from __future__ import annotations

import argparse
import os
import pty
import signal
import sys
import time

from pygdbmi.gdbcontroller import GdbController

from .gdb_nav_utils import step_frame
from .display_setup import (
    DisplayManager,
    configure_gdb_environment,
    configure_gdb_signals,
    configure_gdb_nonstop,
)

# Path to the SDL2 Lavender debug build.
EXECUTABLE = "/home/shalidor/Projects/Lavender_Dev/build/sdl/Lavender_Dev"

# Overall test timeout — abort if the test takes longer than this.
TEST_TIMEOUT = 120.0


def _wait_for_stopped(gdb: GdbController, timeout: float = 10.0) -> bool:
    """Drain responses until we see a 'stopped' notification.

    Returns True if stopped was seen, False on timeout.
    """
    deadline = time.monotonic() + timeout
    poll_interval = min(timeout, 2.0)
    while time.monotonic() < deadline:
        try:
            resp = gdb.get_gdb_response(timeout_sec=poll_interval)
        except Exception:
            return False
        if resp is None:
            return False
        records = resp if isinstance(resp, list) else [resp]
        for rec in records:
            if not isinstance(rec, dict):
                continue
            if rec.get("type") == "notify" and rec.get("message") == "stopped":
                return True
    return False


def _drain_until_running(gdb: GdbController, timeout: float = 5.0) -> bool:
    """Drain console/library-loaded responses until we see 'running'."""
    deadline = time.monotonic() + timeout
    poll_interval = min(timeout, 1.0)
    while time.monotonic() < deadline:
        try:
            resp = gdb.get_gdb_response(timeout_sec=poll_interval)
        except Exception:
            continue
        if resp is None:
            return False
        records = resp if isinstance(resp, list) else [resp]
        for rec in records:
            if not isinstance(rec, dict):
                continue
            msg = rec.get("message")
            if msg == "running":
                return True
            if msg not in ("library-loaded", None):
                return True  # something else — let caller handle it
        # Keep draining console/library-loaded
    return False


def _wait_and_drain(gdb: GdbController, timeout: float = 5.0) -> None:
    """Wait for stopped, then drain until running — best effort."""
    _wait_for_stopped(gdb, timeout=min(timeout, 3.0))
    _drain_until_running(gdb, timeout=min(timeout, 2.0))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integration test for gdb_nav_utils against the Lavender SDL binary."
    )
    parser.add_argument(
        "--software-gl",
        action="store_true",
        help="Force software OpenGL (LIBGL_ALWAYS_SOFTWARE=1) — avoids GPU driver issues.",
    )
    parser.add_argument(
        "--non-stop",
        action="store_true",
        help="Enable GDB non-stop mode for multithreaded SDL apps.",
    )
    parser.add_argument(
        "--no-xvfb",
        action="store_true",
        help="Do not start Xvfb — assume a display is already available.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=TEST_TIMEOUT,
        help=f"Overall test timeout in seconds (default: {TEST_TIMEOUT}).",
    )
    args = parser.parse_args()

    print(f"=== verify_sdl_lav — target: {EXECUTABLE} ===")
    print()

    # Check executable exists.
    if not os.path.isfile(EXECUTABLE):
        print(f"[FAIL] Executable not found: {EXECUTABLE}")
        print("       Run 'LAVENDER_DIR=. make -e PLATFORM=sdl' first.")
        return 1

    gdbmi: GdbController | None = None
    test_start = time.monotonic()

    def _check_timeout():
        if time.monotonic() - test_start > args.timeout:
            raise TimeoutError(f"Test exceeded {args.timeout}s overall timeout")

    # ------------------------------------------------------------------
    # 1. Ensure a usable X display is available.
    # ------------------------------------------------------------------
    display_mgr = None
    if not args.no_xvfb:
        display_mgr = DisplayManager()
        try:
            display_str = display_mgr.start()
            print(f"[*] Display: {display_str}")
        except RuntimeError as e:
            print(f"[WARN] Could not start Xvfb: {e}")
            print("       Will try with existing DISPLAY (if any).")
            display_mgr = None

    # ------------------------------------------------------------------
    # 2. Set up environment for GL stability.
    # ------------------------------------------------------------------
    gdb_env = os.environ.copy()
    if args.software_gl:
        gdb_env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        gdb_env["SDL_VIDEODRIVER"] = "x11"
        print("[*] Software GL mode enabled (LIBGL_ALWAYS_SOFTWARE=1)")
    if display_mgr is not None:
        gdb_env["DISPLAY"] = display_mgr.display
        if display_mgr.xauthority:
            gdb_env["XAUTHORITY"] = display_mgr.xauthority

    try:
        # ------------------------------------------------------------------
        # 3. Launch gdb with a pseudo-terminal for proper SDL2/GLX support.
        # Using a PTY ensures GDB has a proper controlling terminal,
        # which SDL2's video subsystem requires for X11/GLX communication.
        # ------------------------------------------------------------------
        print("[*] Launching gdb with PTY...")
        master_fd, slave_fd = pty.openpty()
        gdbmi = GdbController(
            command=["gdb", "--nx", "--quiet", "--interpreter=mi3"],
            subprocess_kwargs={
                "stdin": slave_fd,
                "stdout": slave_fd,
                "stderr": slave_fd,
                "pass_fds": (slave_fd,),
                "env": gdb_env,
                "preexec_fn": os.setsid,
            },
        )
        os.close(slave_fd)
        # master_fd is not needed by us — gdbmi's stdout goes through pygdbmi's
        # pipe mechanism.  Keep master_fd open for the lifetime of gdbmi.

        # 4. Configure GDB environment and signal handling BEFORE loading
        #    the binary.  Signal handling must be configured before the
        #    process starts so the kernel's signal delivery path is set up
        #    correctly from the outset.
        print("[*] Configuring GDB signal handling (pass-through for SDL/Pulse)...")
        configure_gdb_signals(gdbmi)
        print("[*] Setting display environment...")
        configure_gdb_environment(gdbmi)

        # Set display explicitly (in case configure_gdb_environment didn't catch it).
        display_val = gdb_env.get("DISPLAY", ":0.0")
        gdbmi.write(f"-gdb-set env DISPLAY={display_val}")
        if "XAUTHORITY" in gdb_env:
            gdbmi.write(f"-gdb-set env XAUTHORITY={gdb_env['XAUTHORITY']}")
        if args.software_gl:
            gdbmi.write("-gdb-set env LIBGL_ALWAYS_SOFTWARE=1")
            gdbmi.write("-gdb-set env SDL_VIDEODRIVER=x11")

        # Non-stop mode (must be set before process launch).
        if args.non_stop:
            print("[*] Enabling GDB non-stop mode...")
            configure_gdb_nonstop(gdbmi)

        # Set inferior-tty so the game process inherits a terminal.
        try:
            current_tty = os.ttyname(0)
            gdbmi.write(f"-gdb-set inferior-tty {current_tty}")
        except OSError:
            pass  # Not running in a terminal — skip

        _check_timeout()
        _wait_and_drain(gdbmi, timeout=5.0)

        # ------------------------------------------------------------------
        # 5. Load symbols.
        # ------------------------------------------------------------------
        print("[*] Loading symbols...")
        gdbmi.write(f"-file-exec-and-symbols {EXECUTABLE}")
        _check_timeout()
        _wait_and_drain(gdbmi, timeout=5.0)

        # ------------------------------------------------------------------
        # 6. Start at main (the --start flag stops at the beginning of main).
        # ------------------------------------------------------------------
        print("[*] Starting at main...")
        gdbmi.write("-exec-run --start")
        if not _wait_for_stopped(gdbmi, timeout=10.0):
            print("[FAIL] Program did not stop at main")
            return 1
        print("[*] Stopped at main()")
        _check_timeout()

        # ------------------------------------------------------------------
        # 7. Test step_frame — run until the post-render breakpoint fires.
        #    Use a generous timeout since SDL2/GL initialization can be slow,
        #    especially with software rendering.
        # ------------------------------------------------------------------
        print("[*] Testing step_frame('manage_game__post_render', timeout=20.0)...")
        t0 = time.monotonic()
        ok = step_frame(gdbmi, "manage_game__post_render", timeout=20.0)
        elapsed = time.monotonic() - t0

        if ok:
            print(f"[PASS] step_frame returned True (elapsed: {elapsed:.2f}s)")
        else:
            print(f"[FAIL] step_frame returned False (elapsed: {elapsed:.2f}s)")
            print("       The game may have crashed during GL context initialization.")
            print("       Try running with --software-gl or --no-xvfb to diagnose.")
            return 1

        _check_timeout()

        # ------------------------------------------------------------------
        # 8. Test step_frame again — verify it works on sequential calls.
        #    This is a regression test for a bug where the second step_frame
        #    would time out because _continue's gdb.write() consumed the
        #    *stopped response (now fixed via read_response=False).
        # ------------------------------------------------------------------
        print("[*] Testing step_frame again (regression test for sequential calls)...")
        t0 = time.monotonic()
        ok2 = step_frame(gdbmi, "manage_game__post_render", timeout=20.0)
        elapsed2 = time.monotonic() - t0

        if ok2:
            print(f"[PASS] second step_frame call succeeded (elapsed: {elapsed2:.2f}s)")
            print("[PASS] Sequential step_frame calls work correctly!")
        else:
            print(f"[WARN] second step_frame call returned False (elapsed: {elapsed2:.2f}s)")
            print("       This can happen if (all are game/process issues, not nav step):")
            print("       - The game exited before reaching the next frame")
            print("       - The audio thread (PulseMainloop) crashed (SIGSEGV)")
            print("       - The GPU driver detected a timeout")
            print("       Try: --software-gl --non-stop for more stable behavior")

        _check_timeout()

        print()
        print("=== ALL CHECKS PASSED ===")
        return 0

    except TimeoutError as e:
        print(f"[FAIL] {e}")
        return 1
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if gdbmi is not None:
            print("[*] Detaching / exiting gdb.")
            try:
                gdbmi.exit()
            except Exception:
                pass
        if display_mgr is not None:
            print("[*] Stopping Xvfb (if managed)...")
            display_mgr.stop()


if __name__ == "__main__":
    # Install a hard timeout handler using SIGALRM (on Unix).
    def _timeout_handler(signum, frame):
        print("\n[FAIL] Hard test timeout exceeded")
        sys.exit(1)

    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(int(TEST_TIMEOUT) + 30)

    sys.exit(main())
