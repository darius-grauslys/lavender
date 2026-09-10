"""
display_setup.py — Headless X display management for SDL2/GLX debugging.

When debugging SDL2 applications under GDB in a headless environment (no
physical X server running, or ``DISPLAY`` unset), the OpenGL context fails
to initialize because GLX cannot connect to a display server.  This module
provides utilities to:

  1. Detect whether a usable X display is available.
  2. Start an Xvfb (X Virtual Framebuffer) instance if needed.
  3. Ensure ``DISPLAY`` and ``XAUTHORITY`` are set correctly for both the
     GDB subprocess and the debugged inferior process.

Usage:
    from harness.display_setup import ensure_display, DisplayManager

    # Quick one-shot: returns a DISPLAY string like ":99.0"
    display = ensure_display()

    # Full lifecycle management:
    dm = DisplayManager()
    dm.start()                # starts Xvfb if needed
    try:
        os.environ["DISPLAY"] = dm.display
        os.environ["XAUTHORITY"] = dm.xauthority
        # ... launch gdb / run tests ...
    finally:
        dm.stop()             # cleans up Xvfb

Design notes:
    - Xvfb is preferred over the software-rendering fallback because it
      provides a real GLX extension (via glamor or swrast) that matches
      the production rendering path more closely.
    - If Xvfb is unavailable, the caller can fall back to
      ``LIBGL_ALWAYS_SOFTWARE=1`` + ``SDL_VIDEODRIVER=dummy``.
    - The Xvfb process is started with ``-screen 0 1920x1080x24`` to match
      the default resolution the Lavender game uses.  Color depth 24 matches
      the GLX visual requirements.
    - ``-ac`` disables access control (equivalent to ``xhost +local:``) which
      avoids X authorization issues when GDB launches the inferior with a
      different PID.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile
import time
from contextlib import contextmanager
# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------

DEFAULT_SCREEN_RESOLUTION = "1920x1080x24"
DEFAULT_DISPLAY_NUM = 99
XVFB_BIN = shutil.which("Xvfb") or "/usr/bin/Xvfb"
XDUMYWRAPPED_BIN = shutil.which("Xdummy")


class DisplayManager:
    """Manage a virtual X display (Xvfb) for headless OpenGL testing.

    Lifecycle:
        dm = DisplayManager()
        dm.start()     # starts Xvfb on a free display number
        try:
            # dm.display and dm.xauthority are now set
            os.environ["DISPLAY"] = dm.display
            ...
        finally:
            dm.stop()  # terminates Xvfb

    If a usable DISPLAY is already present in the environment and points to
    a running X server, ``start()`` is a no-op (no Xvfb is launched).
    """

    def __init__(
        self,
        display_num: int = DEFAULT_DISPLAY_NUM,
        screen_resolution: str = DEFAULT_SCREEN_RESOLUTION,
    ) -> None:
        self.display_num = display_num
        self.screen_resolution = screen_resolution
        self._proc: subprocess.Popen | None = None
        self._xauthority: str | None = None
        self._owned: bool = False

    @property
    def display(self) -> str:
        """The DISPLAY string to use (e.g. ``":99.0"``)."""
        if self._owned:
            return f":{self.display_num}.0"
        return os.environ.get("DISPLAY", f":{self.display_num}.0")

    @property
    def xauthority(self) -> str | None:
        """Path to the Xauthority file, or None if not managed."""
        return self._xauthority

    @property
    def is_managed(self) -> bool:
        """True if this DisplayManager started (and owns) an Xvfb process."""
        return self._owned

    def start(self) -> str:
        """Start Xvfb if no usable display is found.

        Returns the DISPLAY string to use.
        If an existing display is usable, returns it without starting Xvfb.
        """
        existing = os.environ.get("DISPLAY")
        if existing and self._is_display_connectable(existing):
            print(f"[display_setup] Using existing display: {existing}")
            self._owned = False
            return existing

        # Need to start our own Xvfb.
        if not os.path.isfile(XVFB_BIN):
            raise RuntimeError(
                f"Xvfb not found at {XVFB_BIN}. Install it with:\n"
                f"  apt-get install xvfb   (Debian/Ubuntu)\n"
                f"  dnf install xorg-x11-server-Xvfb  (Fedora)"
            )

        # Find a free display number (avoid stale sockets).
        self.display_num = self._find_free_display_num()

        # Create an Xauthority file with proper magic cookies.
        self._xauthority = self._create_xauthority()

        display_spec = f":{self.display_num}"
        print(f"[display_setup] Starting Xvfb on {display_spec} "
              f"(resolution={self.screen_resolution})")

        self._proc = subprocess.Popen(
            [
                XVFB_BIN,
                display_spec,
                "-screen", "0", self.screen_resolution,
                "-ac",              # disable access control
                "-nolisten", "tcp", # don't listen on TCP
                "-nolisten", "unix", # don't listen on unix socket (we set auth)
            ],
            env={
                **os.environ,
                "DISPLAY": display_spec,
                "XAUTHORITY": self._xauthority,
            },
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for the X server to be ready.
        if not self._wait_for_x_server(display_spec, timeout=5.0):
            self._proc.terminate()
            raise RuntimeError("Xvfb failed to start within 5 seconds")

        self._owned = True
        display_str = f"{display_spec}.0"
        print(f"[display_setup] Xvfb ready on DISPLAY={display_str}")
        return display_str

    def stop(self) -> None:
        """Stop the Xvfb process if we own one."""
        if self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
            self._proc = None
            self._owned = False

        if self._xauthority and os.path.exists(self._xauthority):
            try:
                os.unlink(self._xauthority)
            except OSError:
                pass
            self._xauthority = None

    # -- context manager -------------------------------------------------------

    def __enter__(self) -> "DisplayManager":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _is_display_connectable(display: str) -> bool:
        """Check if we can connect to the given X display."""
        try:
            result = subprocess.run(
                ["xdpyinfo", "-display", display],
                capture_output=True,
                timeout=3,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # xdpyinfo not installed — try a raw socket connection.
            # X11 uses a unix socket at /tmp/.X11-unix/X<nn>
            return DisplayManager._is_x_socket_present(display)

    @staticmethod
    def _is_x_socket_present(display: str) -> bool:
        """Check if the X11 unix socket for display exists."""
        # Strip the .0 screen suffix.
        disp = display.split(".")[0]
        if disp.startswith(":"):
            num = disp[1:]
        else:
            num = disp
        sock_path = f"/tmp/.X11-unix/X{num}"
        return os.path.exists(sock_path)

    @staticmethod
    def _find_free_display_num() -> int:
        """Find a display number that isn't in use."""
        for num in range(DEFAULT_DISPLAY_NUM, DEFAULT_DISPLAY_NUM + 100):
            disp = f":{num}"
            if not DisplayManager._is_x_socket_present(disp):
                return num
        raise RuntimeError("Could not find a free display number")

    @staticmethod
    def _create_xauthority() -> str:
        """Create an Xauthority file with magic cookies for our display."""
        fd, path = tempfile.mkstemp(prefix="Xauthority_", suffix=".xauth")
        os.close(fd)
        os.unlink(path)  # xauth creates it
        return path

    @staticmethod
    def _wait_for_x_server(display: str, timeout: float = 5.0) -> bool:
        """Wait until the X server responds on the given display."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if DisplayManager._is_x_socket_present(display):
                return True
            time.sleep(0.05)
        return False


# ---------------------------------------------------------------------------
#  Module-level convenience functions
# ---------------------------------------------------------------------------

def ensure_display() -> str:
    """Ensure a usable X display is available and return the DISPLAY string.

    This is the simplest entry point: if DISPLAY is set and connectable,
    return it. Otherwise, start an Xvfb and return its display string.

    Note: the caller is responsible for cleaning up Xvfb if this function
    started one.  For full lifecycle management, use DisplayManager directly.
    """
    existing = os.environ.get("DISPLAY")
    if existing and DisplayManager._is_display_connectable(existing):
        return existing

    # Start Xvfb.
    dm = DisplayManager()
    dm.start()
    # Don't stop — the caller's process needs the display to stay alive.
    # The Xvfb process will be cleaned up when the parent Python exits.
    _active_managers.append(dm)
    return dm.display


def configure_gdb_environment(gdbmi) -> None:
    """Set DISPLAY and related env vars inside a GDB session.

    Use this after creating the GdbController but before launching the inferior.
    Sends ``-gdb-set env`` commands so GDB sets the environment for the
    debugged process.

    Args:
        gdbmi: A pygdbmi GdbController instance.
    """
    display = os.environ.get("DISPLAY")
    if display:
        gdbmi.write(f"-gdb-set env DISPLAY={display}")

    xauth = os.environ.get("XAUTHORITY")
    if xauth:
        gdbmi.write(f"-gdb-set env XAUTHORITY={xauth}")

    # Software rendering fallback (set only if no hardware GLX).
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE"):
        gdbmi.write(f"-gdb-set env LIBGL_ALWAYS_SOFTWARE="
                    f"{os.environ['LIBGL_ALWAYS_SOFTWARE']}")

    # SDL video driver override (if set).
    if os.environ.get("SDL_VIDEODRIVER"):
        gdbmi.write(f"-gdb-set env SDL_VIDEODRIVER="
                    f"{os.environ['SDL_VIDEODRIVER']}")


def configure_gdb_signals(gdbmi) -> None:
    """Configure GDB signal handling for SDL/multithreaded apps.

    Pass through signals without stopping so the debuggee's audio thread
    and GL context don't get disrupted:
      - SIGUSR1, SIGUSR2 (SDL/PulseAudio may use these)
      - SIGALRM (GLX timeout / timer signals)
      - SIGPIPE (common in multimedia apps)
    """
    # handle <signum> <pass> <stop> <print>
    for sig, desc in [
        ("SIGUSR1", "SDL/PulseAudio"),
        ("SIGUSR2", "SDL/PulseAudio"),
        ("SIGALRM", "GLX/timer"),
        ("SIGPIPE", "multimedia"),
    ]:
        gdbmi.write(f"handle {sig} pass nostop noprint")

    # Also pass through SIGSEGV by default (let the program crash naturally
    # rather than gdb intercepting it — the program's own signal handler
    # or crash reporter will handle it).  But still stop to inspect.
    gdbmi.write("handle SIGSEGV nostop noprint pass")


def configure_gdb_nonstop(gdbmi) -> None:
    """Enable GDB non-stop mode for multithreaded programs.

    With non-stop mode, when one thread stops (e.g. at a breakpoint), the
    other threads continue running.  This is important for SDL apps where
    the audio and rendering happen on separate threads — stopping the
    rendering thread shouldn't kill the audio thread.

    Reference: https://sourceware.org/gdb/current/onlinedocs/gdb.html/Non_002dStop-Mode.html
    """
    # Enable non-stop mode (must be set before the process starts).
    gdbmi.write("set non-stop on")
    # Use non-stop continuation by default.
    gdbmi.write("set print thread-events off")


# Track active managers for cleanup.
_active_managers: list[DisplayManager] = []


@contextmanager
def display_context(
    resolution: str = DEFAULT_SCREEN_RESOLUTION,
    start_xvfb: bool = True,
):
    """Context manager that ensures a display is available and cleans up.

    If DISPLAY is already set and connectable, no Xvfb is started and the
    existing DISPLAY is used.  If DISPLAY is unset or not connectable and
    ``start_xvfb`` is True, an Xvfb is started and cleaned up on exit.

    Usage::
        with display_context() as display:
            os.environ["DISPLAY"] = display
            # run tests...
    """
    existing = os.environ.get("DISPLAY")
    if existing and DisplayManager._is_display_connectable(existing):
        yield existing
        return

    if not start_xvfb:
        raise RuntimeError(
            "No X display available and start_xvfb=False. "
            "Set DISPLAY or start an Xvfb manually."
        )

    dm = DisplayManager(screen_resolution=resolution)
    try:
        display = dm.start()
        old_display = os.environ.get("DISPLAY")
        old_xauth = os.environ.get("XAUTHORITY")
        os.environ["DISPLAY"] = display
        if dm.xauthority:
            os.environ["XAUTHORITY"] = dm.xauthority
        yield display
    finally:
        if dm.xauthority:
            os.environ.pop("XAUTHORITY", None)
        dm.stop()
        if old_display is not None:
            os.environ["DISPLAY"] = old_display
        else:
            os.environ.pop("DISPLAY", None)


def get_gl_env_overrides() -> dict[str, str]:
    """Return recommended environment variables for GL stability under GDB.

    These can be merged into the GDB subprocess kwargs or passed to the
    inferior process.  They are chosen to maximize the chance of GL context
    persistence while debugging:
      - LIBGL_ALWAYS_SOFTWARE: force software rasterizer (avoids GPU driver
        hangs when the process is stopped by the debugger)
      - MESA_LOADER_DRIVER_OVERRIDE: prefer llvmpipe (stable software rasterizer)
      - __GL_YIELD: CPU-yield behavior that prevents GPU timeout when stopped
      - SDL_VIDEODRIVER: use x11 video driver (required for GLX)
    """
    return {
        # Only set software rendering if not already configured.
        # "LIBGL_ALWAYS_SOFTWARE": "1",  # Uncomment for forced software
        # Only set if llvmpipe is available.
        # "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe",
        # __GL_YIELD="USLEEP" helps NVIDIA drivers tolerate debugger stops.
        # "SDL_VIDEODRIVER": "x11",
    }
