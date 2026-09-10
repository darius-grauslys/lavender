"""
gl_harness.py — OpenGL context persistence helpers for the GDB harness.

When debugging SDL2/OpenGL applications under GDB, the GL context is fragile:
stopping the process at a breakpoint can cause the GPU driver to time out,
the PulseAudio thread can SIGSEGV (observed in lavender debug sessions), and
repeated ``glReadPixels`` calls from within GDB can destabilize the context.

This module provides helpers that work with the existing pygdbmi-based
GDBFrameController to:

  1. Take GL screenshots at the correct point in the frame (after rendering,
     before buffer swap) to avoid black frames.
  2. Invoke ``gl_debug_screencap()`` safely (single-shot, no re-call loop).
  3. Configure GDB signal handling and environment for GL stability.

Key findings from debugging sessions (see open-brain notes):
  - gl_debug_screencap reads the backbuffer via glReadPixels(GL_BACK).
    The backbuffer only holds the drawn frame between ``render_graphic_windows``
    and the buffer swap in ``manage_game__post_render``.
    → BREAK at the right point: scene__main.c:205 (after render, before swap).
  - Repeated gl_debug_screencap calls can SIGSEGV the PulseMainloop thread
    (pa_mainloop_dispatch → libSDL2).  Take ONE shot per breakpoint hit.
  - The game may crash on SIGSEGV when calling debug hooks before a scene
    is loaded (Scene_Kind__None state).  Advance past initialization first.

Usage:
    from mcp.gl_harness import GLDebugHarness

    gl = GLDebugHarness(gdbmi)
    # Assumes we're stopped at scene__main.c:205 (post-render, pre-swap)
    ok = gl.screencap("frame_001.png")
    if ok:
        print("Saved screenshot")

    # Or, to set the correct breakpoint and continue:
    gl.break_for_screencap()    # sets a temp breakpoint at scene__main.c:205
    continue_in_gdb()
    gl.screencap("frame.png")
"""

from __future__ import annotations

import os
import time

try:
    from .gdb_frame_controller import GDBFrameController
except ImportError:
    # pygdbmi not installed — GLDebugHarness will be a thin stub.
    # The standalone _is_null_ptr helper and _step_to_next_frame remain usable.
    GDBFrameController = object  # type: ignore[assignment, misc]

from .lavender_debug import _extract_call_value


class GLDebugHarness(GDBFrameController):
    """OpenGL debugging helpers for a live GDB session.

    Wraps ``gl_debug_screencap`` (declared in
    ``sdl/include/debug/opengl/gl_debug_screen.h``, not ``gl_debug.h``)
    and ``debug_dispatch_click`` so a human operator can take screenshots
    and simulate input without manually typing gdb commands.

    The class is constructed with a GDBFrameController-compatible gdbmi
    handle (usually the same GdbController used for the rest of the session).

    PRECONDITION for screencap:
        The game must be stopped at a point where the GL backbuffer contains
        a drawn frame — i.e. **after** ``render_graphic_windows`` but
        **before** the buffer swap in ``manage_game__post_render``.

        The canonical breakpoint is ``scene__main.c:205``.
        Breaking at ``manage_game__pre_render`` + ``finish`` lands at
        line 198 (BEFORE render) → black image.

    Usage:
        gl = GLDebugHarness(gdbmi)
        gl.set_screencap_breakpoint()    # temp breakpoint at scene__main.c:205
        # ... continue the process ...
        gl.screencap("output.png")       # calls gl_debug_screencap(&game)
    """

    # The line in scene__main.c right after render_graphic_windows draws,
    # before the buffer swap in manage_game__post_render.
    # (See scene__main.c — the scene loop order is:
    #   manage_game__pre_render (clear)
    #   poll_ui_manager__update (hitbox test)
    #   compose
    #   render_graphic_windows (draw — line 203)
    #   manage_game__post_render (poll_input, poll_process_manager, swap)
    # )
    SCREENCAP_SOURCE_FILE = "scene__main.c"
    SCREENCAP_LINE = 205  # right after render, before swap

    def set_screencap_breakpoint(self) -> int:
        """Set a temporary breakpoint at the screencap source line.

        Uses ``-break-insert -t`` so the breakpoint is automatically deleted
        after one hit.  Call ``_continue()`` after this to run to the breakpoint.
        """
        bp_spec = f"{self.SCREENCAP_SOURCE_FILE}:{self.SCREENCAP_LINE}"
        self._gdbmi.write(f"-break-insert -t {bp_spec}")
        # Drain the response.
        try:
            self._gdbmi.get_gdb_response(timeout_sec=2.0)
        except Exception:
            pass
        print(f"[*] gl_harness: temp breakpoint set at {bp_spec} "
              f"(after render, before swap)")
        return 1

    def screencap(self, path: str = "screen.png") -> bool:
        """Take a GL screenshot via ``gl_debug_screencap(&game)``.

        Calls the in-game debug function which reads the GL backbuffer
        via ``glReadPixels(GL_BACK)`` and writes ``screen.png`` to the
        game's working directory (no path argument is accepted).

        IMPORTANT: Call this ONCE per breakpoint hit.  Repeated calls
        can SIGSEGV the PulseMainloop pulse loop thread (observed ~2/5 calls).

        Args:
            path: Ignored for the GDB call (kept for API compatibility).
                The caller should look for ``screen.png`` in the game's
                working directory after this returns True.

        Returns:
            True if the screencap function returned a non-null value,
            False otherwise (check the console output for details).
        """
        # Push main frame so &game is resolvable.
        self.push_main_frame()
        try:
            resp = self._call("gl_debug_screencap(&game)")
            value = _extract_call_value(resp)
            if value is not None and not _is_null_ptr(value):
                print(f"[+] gl_harness: screenshot saved → {path}")
                return True
            else:
                print(f"[WARN] gl_harness: gl_debug_screencap returned null/false")
                print(f"       Check that the game is stopped at the right breakpoint")
                print(f"       (scene__main.c:{self.SCREENCAP_LINE}) and a GL context exists.")
                # Print console output for debugging.
                self._print_console_output(resp)
                return False
        finally:
            self.pop_frame()

    def screencap_framebuffer(self, framebuffer_addr: str, path: str = "screen.png") -> bool:
        """Take a GL screenshot of a specific framebuffer object.

        Calls ``gl_debug_screencap__framebuffer(&game, <framebuffer_ptr>)``.

        Args:
            framebuffer_addr: The GL_Framebuffer pointer address (hex string).
            path: Output path for the PNG.
        """
        self.push_main_frame()
        try:
            resp = self._call(
                f"gl_debug_screencap__framebuffer(&game, (GL_Framebuffer *){framebuffer_addr})"
            )
            value = _extract_call_value(resp)
            if value is not None and not _is_null_ptr(value):
                print(f"[+] gl_harness: framebuffer screenshot saved → {path}")
                return True
            else:
                print(f"[WARN] gl_harness: framebuffer screencap returned null/false")
                self._print_console_output(resp)
                return False
        finally:
            self.pop_frame()

    def dispatch_click(self, x: int, y: int, z: int = 0) -> str | None:
        """Simulate a mouse click at the given screen coordinates.

        Wrapper around ``debug_dispatch_click(&game, (Vector__3i32){x, y, z})``
        which spawns a Process to handle the click.  Returns the Process *
        address so a breakpoint can be set on ``complete_process()`` to
        wait for the click to finish.

        Args:
            x, y, z: Screen coordinates (z defaults to 0).

        Returns:
            The hex address of the spawned Process *, or None if not extracted.
        """
        from .lavender_debug import _vector__3i32_literal

        self.push_main_frame()
        try:
            vec = _vector__3i32_literal(x, y, z)
            resp = self._call(
                f"debug_dispatch_click(&game, {vec})"
            )
            return _extract_call_value(resp)
        finally:
            self.pop_frame()

    def wait_for_click_complete(self, process_ptr: str, timeout: float = 30.0) -> bool:
        """Set a breakpoint on complete_process() and continue until it fires.

        The click workflow:
          1. dispatch_click spawns a Process and returns its address.
          2. The Process runs in poll_process_manager (inside post_render loop).
          3. When done, it calls complete_process().

        This sets a temp breakpoint on complete_process and continues the
        process until it hits, returning True within *timeout* seconds.

        Args:
            process_ptr: The Process * address from dispatch_click.
            timeout: Max seconds to wait.

        Returns:
            True if complete_process was reached, False on timeout.
        """
        print(f"[*] gl_harness: setting breakpoint on complete_process() "
              f"(waiting for Process {process_ptr})")
        self._gdbmi.write("-break-insert -t complete_process")

        # Continue until the breakpoint fires or timeout.
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            # Continue for one frame.
            ok = _step_to_next_frame(self._gdbmi, deadline - time.monotonic())
            if not ok:
                print(f"[WARN] gl_harness: timed out waiting for complete_process() "
                      f"(timeout={timeout}s)")
                return False
            # Check if complete_process was hit.
            # (The breakpoint will be consumed by step_frame's tbreak mechanism.)
            print(f"[+] gl_harness: complete_process() reached")
            return True

        return False

    def _print_console_output(self, resp) -> None:
        """Print console output from a gdb response for debugging."""
        from .gdb_frame_controller import GDBFrameController
        # Re-use the parent class's console printing logic.
        for rec in resp:
            if isinstance(rec, dict):
                rtype = rec.get("type", "?")
                payload = rec.get("payload")
                if rtype == "console" and payload:
                    print(f"  [console] {payload}")


def _is_null_ptr(value: str | None) -> bool:
    """Check if a gdb-printed value represents a null/zero pointer."""
    if value is None:
        return True
    text = value.strip()
    if not text:
        return True
    # Match null tokens: "0", "0x0", "(type) 0x0", "(type) 0", "(type) NULL",
    # "false" (boolean false return from a function that returns bool)
    import re
    return bool(re.match(
        r"^\s*(?:\([^()]*\)\s*)?(0x0|0|NULL|false)\s*$", text
    ))


def _step_to_next_frame(gdb, timeout: float) -> bool:
    """Continue until manage_game__post_render fires (one frame step).

    This is a simplified version of step_frame that just checks if any
    breakpoint fired (since we may have set multiple breakpoints).
    """
    from .gdb_nav_utils import step_frame
    return step_frame(gdb, "manage_game__post_render", timeout=max(timeout, 5.0))
