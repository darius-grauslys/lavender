#!/usr/bin/env python3
"""
harness_container.py — Run the harness inside a container with SYS_PTRACE.

This script is designed to run **inside** the lav-sandbox container where:
  - GDB and pygdbmi are installed
  - Xvfb is running on DISPLAY=:99.0
  - The container was started with --cap-add=SYS_PTRACE and
    --security-opt seccomp=unconfined

Instead of having GDB launch the inferior (which can cause SDL2/GLX
issues because the inferior lacks a controlling terminal), this script:

  1. Launches the Lavender SDL binary as a child process (using subprocess.Popen
     but with proper stdin/stdout/stderr inherited from the container's PTY)
  2. Waits for the process to start and reach initialization
  3. Attaches GDB to the running process via ``-target-attach``
  4. Sets a breakpoint at manage_game__post_render
  5. Continues execution and monitors the process

Because the container has SYS_PTRACE and seccomp=unconfined, GDB can attach
to any process in the container without ptrace_scope issues.

The key difference from the old harness_qa.py: the program runs natively
(not through a pipe-only subprocess), so SDL2 gets a proper terminal and
display. GDB attaches AFTER the program has established its GL context.

Usage (inside the container):
    python3 harness/harness_container.py \\
        --program /work/lavender/build/sdl/Lavender_Dev

    # Optional: break at a specific function
    python3 harness/harness_container.py \\
        --program /work/lavender/build/sdl/Lavender_Dev \\
        --breakpoint manage_game__post_render

    # Verbose: print all gdbmi output
    python3 harness/harness_container.py --program ... --verbose
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
import time

from pygdbmi.gdbcontroller import GdbController

# GDB command base — use --nx (ignore .gdbinit) and --interpreter=mi3
GDB_CMD_BASE = ["gdb", "--nx", "--quiet", "--interpreter=mi3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Lavender harness inside a Docker container with SYS_PTRACE."
    )
    parser.add_argument(
        "--program",
        required=True,
        help="Path to the Lavender SDL executable.",
    )
    parser.add_argument(
        "--breakpoint",
        default="manage_game__post_render",
        help="Breakpoint function to set after attaching (default: "
             "manage_game__post_render).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout in seconds for the attach + breakpoint phase (default: 30).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print all gdbmi output records.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enter an interactive gdbmi read-loop after attaching.",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory for the program (default: program's directory).",
    )
    return parser.parse_args()


def launch_program(program: str, cwd: str | None = None) -> subprocess.Popen:
    """Launch the target executable as a child process.

    Unlike the old harness_qa.py, we inherit stdin/stdout/stderr from
    the parent process (which in the container has a proper PTY).
    This ensures SDL2 gets a controlling terminal and proper display.

    Args:
        program: Path to the executable.
        cwd: Working directory for the program. If None, defaults to
             the directory containing the executable (Lavender binaries
             often expect to be run from their build directory).
    """
    if not os.path.isfile(program):
        raise FileNotFoundError(f"Program not found: {program}")
    if not os.access(program, os.X_OK):
        raise PermissionError(f"Program is not executable: {program}")

    env = os.environ.copy()

    # Default working directory: the directory containing the executable.
    # This matches how the game is typically run (from build/sdl/).
    if cwd is None:
        cwd = str(os.path.dirname(os.path.abspath(program)))

    proc = subprocess.Popen(
        [str(program)],
        stdin=None,           # inherit parent's stdin (container's PTY)
        stdout=None,          # inherit parent's stdout
        stderr=None,          # inherit parent's stderr
        env=env,
        cwd=cwd,              # run from the program's directory
        # Don't use start_new_session — we want the child to share the
        # process group so signals propagate correctly.
    )
    print(f"[*] Launched program (pid={proc.pid}, cwd={cwd})")
    return proc


def attach_gdb(gdbmi: GdbController, pid: int) -> bool:
    """Attach GDB to the running process via -target-attach.

    Returns True on success, False on failure.
    """
    print(f"[*] Attaching gdb to pid {pid}...")

    # Send the attach command.
    response = gdbmi.write(f"-target-attach {pid}")
    print(f"[*] gdb attach response: {response}")

    for rec in response:
        if rec.get("type") == "result" and rec.get("message") == "error":
            print(f"[FAIL] GDB failed to attach to pid {pid}: {rec}")
            return False

    # Drain the async "stopped" notification so the process is in a
    # deterministic stopped state before we set breakpoints.
    try:
        gdbmi.get_gdb_response(timeout_sec=3, raise_error_on_timeout=False)
    except Exception:
        pass

    print(f"[*] Attached gdb to pid {pid}")
    return True


def configure_gdb_signals(gdbmi: GdbController) -> None:
    """Configure GDB signal handling for SDL/multithreaded apps.

    Pass through signals that SDL/PulseAudio/GLX use so they don't
    cause the debugger to stop the process:
      - SIGUSR1, SIGUSR2 (SDL/PulseAudio)
      - SIGALRM (GLX/timer)
      - SIGPIPE (multimedia apps)
      - SIGSEGV (let the program's own handler manage it)
    """
    signals = [
        ("SIGUSR1", "SDL/PulseAudio"),
        ("SIGUSR2", "SDL/PulseAudio"),
        ("SIGALRM", "GLX/timer"),
        ("SIGPIPE", "multimedia"),
    ]
    for sig, desc in signals:
        try:
            gdbmi.write(f"handle {sig} pass nostop noprint")
        except Exception as e:
            print(f"[WARN] Could not configure signal {sig}: {e}")

    # Let SIGSEGV pass through but still stop to inspect.
    try:
        gdbmi.write("handle SIGSEGV nostop noprint pass")
    except Exception:
        pass


def set_breakpoint(gdbmi: GdbController, func_name: str) -> bool:
    """Set a breakpoint at the given function name via MI3."""
    print(f"[*] Setting breakpoint at '{func_name}'...")
    response = gdbmi.write(f"-break-insert {func_name}")

    for rec in response:
        if rec.get("type") == "result" and rec.get("message") == "done":
            payload = rec.get("payload") or {}
            bkpt = payload.get("bkpt")
            if bkpt:
                if isinstance(bkpt, list):
                    bkpt = bkpt[0]
                number = bkpt.get("number")
                print(f"[+] Breakpoint set: ID={number}")
                return True
        elif rec.get("type") == "result" and rec.get("message") == "error":
            print(f"[FAIL] Could not set breakpoint: {rec}")
            return False

    # Some GDB versions don't return a "done" for -break-insert.
    # Assume success if no error.
    print(f"[+] Breakpoint set (no explicit confirmation from gdb)")
    return True


def wait_for_breakpoint(gdbmi: GdbController, timeout: float = 30.0, verbose: bool = False) -> bool:
    """Wait for a breakpoint hit or process exit.

    Polls gdbmi for 'stopped' notify events with reason 'breakpoint-hit'.
    Returns True if the breakpoint was hit, False on timeout or exit.
    """
    deadline = time.monotonic() + timeout
    poll_interval = min(timeout, 0.5)
    started = time.monotonic()

    while time.monotonic() < deadline:
        try:
            resp = gdbmi.get_gdb_response(timeout_sec=poll_interval)
        except Exception:
            continue

        if resp is None:
            # gdb exited or no response available.
            return False

        records = resp if isinstance(resp, list) else [resp]
        for rec in records:
            if not isinstance(rec, dict):
                continue

            if verbose:
                print(f"  [gdbmi] {rec}")

            if rec.get("type") == "notify" and rec.get("message") == "stopped":
                payload = rec.get("payload") or {}
                reason = payload.get("reason", "")

                if reason == "breakpoint-hit":
                    bkptno = payload.get("bkptno")
                    print(f"[+] Breakpoint hit! (bkptno={bkptno}) "
                          f"at {time.monotonic() - started:.1f}s")
                    return True

                elif reason == "exited-normally":
                    print(f"[+] Process exited normally at {time.monotonic() - started:.1f}s")
                    return False

                elif reason in ("signal-segv", "signal-sigsegv"):
                    print(f"[+] Process received SIGSEGV at {time.monotonic() - started:.1f}s")
                    return False

                else:
                    if verbose or reason not in ("running", "library-loaded"):
                        print(f"  [stopped] reason={reason}")

            elif rec.get("type") == "notify" and rec.get("message") == "running":
                if verbose:
                    print(f"  [running] at {time.monotonic() - started:.1f}s")

    print(f"[WARN] Timeout waiting for breakpoint (timeout={timeout}s)")
    return False


def run_interactive_loop(gdbmi: GdbController) -> None:
    """Enter an interactive gdbmi read-loop."""
    print("[*] Entering gdbmi read-loop.  Press Ctrl-C to detach & exit.")

    stop_event = threading.Event()

    def _sigint_handler(signum, frame):
        stop_event.set()

    old_handler = signal.signal(signal.SIGINT, _sigint_handler)
    try:
        while not stop_event.is_set():
            responses = gdbmi.get_gdb_response(
                timeout_sec=0.5, raise_error_on_timeout=False
            )
            for rec in responses:
                print(rec)
    finally:
        signal.signal(signal.SIGINT, old_handler)


def main() -> int:
    args = parse_args()
    program = os.path.abspath(args.program)
    print(f"=== harness_container — target: {program} ===")
    print(f"[*] DISPLAY={os.environ.get('DISPLAY', '(unset)')}")
    print()

    child: subprocess.Popen | None = None
    gdbmi: GdbController | None = None

    try:
        # --- Step 1: Launch the program natively. ----------------------- #
        print("[1/4] Launching program (native, inherits container PTY)...")
        child = launch_program(program, cwd=args.cwd)

        # Give the program time to initialize SDL2, X11, and the GL context.
        # We wait a bit so the GL context is established BEFORE we attach
        # GDB — this avoids the "context not formed" issue that happened
        # when gdb.attach() intercepted process startup.
        print(f"[*] Waiting {2.0}s for program initialization (GL context setup)...")
        time.sleep(2.0)

        # Check if the process is still running.
        if child.poll() is not None:
            print(f"[FAIL] Program exited immediately (status={child.returncode})")
            print("       Common causes:")
            print("       - DISPLAY not set or Xvfb not running")
            print("       - Missing GL libraries (check LIBGL_ALWAYS_SOFTWARE=1)")
            print("       - SDL_VIDEODRIVER must be 'x11' for GLX")
            print("       - Missing libcglm, libpulse, or audio libraries")
            print("       - Binary compiled for a different glibc version")
            print()
            print("       Try running the program directly to see the error:")
            print(f"       $ cd {os.path.dirname(program)}")
            print(f"       $ LD_DEBUG=libs SDL_VIDEODRIVER=x11 LIBGL_ALWAYS_SOFTWARE=1 ./$(basename program)")
            return 1
        print(f"[+] Program is running (pid={child.pid})")

        # --- Step 2: Attach GDB to the running process. ----------------- #
        print("[2/4] Starting gdb controller and attaching...")
        gdbmi = GdbController(command=GDB_CMD_BASE)

        if not attach_gdb(gdbmi, child.pid):
            print("[FAIL] Could not attach gdb to the process.")
            print("       This usually means:")
            print("       - The container wasn't started with --cap-add=SYS_PTRACE")
            print("       - The container wasn't started with --security-opt seccomp=unconfined")
            print("       - The host kernel has ptrace_scope > 1")
            print("       Fix: docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined ...")
            print("       And on the host: sudo sysctl -w kernel.yama.ptrace_scope=0")
            return 1

        # Configure signals for SDL/PulseAudio/GL stability.
        print("[*] Configuring GDB signal handling...")
        configure_gdb_signals(gdbmi)

        # --- Step 3: Set breakpoint and continue. ----------------------- #
        print("[3/4] Setting breakpoint and continuing...")
        if not set_breakpoint(gdbmi, args.breakpoint):
            print(f"[FAIL] Could not set breakpoint at '{args.breakpoint}'")
            print("       Make sure the binary is a debug build with symbols.")
            return 1

        # Continue the process — it should run until the breakpoint.
        gdbmi.write("-exec-continue")
        # Drain the "running" notification.
        try:
            gdbmi.get_gdb_response(timeout_sec=1, raise_error_on_timeout=False)
        except Exception:
            pass

        # --- Step 4: Wait for the breakpoint to hit. ------------------ #
        print(f"[4/4] Waiting for breakpoint '{args.breakpoint}' (timeout={args.timeout}s)...")
        hit = wait_for_breakpoint(
            gdbmi, timeout=args.timeout, verbose=args.verbose
        )

        if hit:
            print()
            print("[+] SUCCESS: Program reached the breakpoint!")
            print(f"    The OpenGL context has been formed and the program is")
            print(f"    now stopped at '{args.breakpoint}'.")
            print()
            print("[*] You can now use gdbmi commands to inspect the program:")
            print("    - -data-evaluate-expression &game  # Get the Game pointer")
            print("    - -stack-list-frames               # Show call stack")
            print("    - -stack-list-variables --all-values  # List local variables")
            print("    - call gl_debug_screencap(&game)   # Take a screenshot")
        else:
            print()
            print("[WARN] The breakpoint was not hit within the timeout.")
            print("       This could mean:")
            print("       - The program crashed during GL initialization")
            print("       - The GL context wasn't formed (check DISPLAY/Xvfb)")
            print("       - The breakpoint symbol doesn't exist in this binary")

        # --- Enter interactive mode if requested. ------------------ #
        if args.interactive or args.verbose:
            print()
            run_interactive_loop(gdbmi)

        print()
        print("=== DONE ===")
        return 0 if hit else 1

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
        return 0
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # --- Cleanup --- #
        if gdbmi is not None:
            print("[*] Detaching / exiting gdb.")
            try:
                gdbmi.exit()
            except Exception:
                pass
        if child is not None:
            print(f"[*] Terminating child process (pid={child.pid}).")
            try:
                os.killpg(os.getpgid(child.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                try:
                    child.kill()
                except Exception:
                    pass
            try:
                child.wait(timeout=5)
            except Exception:
                try:
                    child.kill()
                except Exception:
                    pass


if __name__ == "__main__":
    sys.exit(main())
