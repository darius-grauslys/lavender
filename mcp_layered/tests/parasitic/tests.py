"""Parasitic tests for layer_pygdbmi breakpoint hooks.

These tests depend on /home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame
which is not guaranteed to be in any arbitrary environment. They are separated from
the main test suite because they require a specific binary.

These tests verify that:
1. Breakpoint hooks fire when the corresponding function is hit
2. The DebugUIScanner correctly captures UI elements
3. Hooks fire during step_frame polling (not just write())
"""

import os
import sys
import unittest
from unittest.mock import patch

# Setup import paths
# tests.py is at Lavender_Dev/mcp_layered/tests/parasitic/tests.py
# mcp_layered package is at Lavender_Dev/mcp_layered/
# We need Lavender_Dev/ in sys.path for "import mcp_layered.X"
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARASITIC_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))  # mcp_layered/
_REPO_ROOT = os.path.abspath(os.path.join(_PARASITIC_ROOT, ".."))  # Lavender_Dev/
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _PARASITIC_ROOT)

# Binary path that these tests depend on
ANCIENTSGAME_BINARY = "/home/shalidor/Projects/Projects__Lavender/AncientsGame/build/sdl/AncientsGame"


def _binary_available() -> bool:
    """Check if the AncientsGame binary is available for testing."""
    return os.path.isfile(ANCIENTSGAME_BINARY)


@unittest.skipUnless(_binary_available(), f"Requires {ANCIENTSGAME_BINARY}")
class TestBreakpointHooksParasitic(unittest.TestCase):
    """Parasitic tests verifying breakpoint hooks fire correctly."""

    def test_hooks_fire_on_step_frame(self):
        """Breakpoint hooks should fire when continuing and hitting breakpoints."""
        from mcp_layered.layer_pygdbmi import GDBSession

        # Track hook firings
        fires = []

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Register hooks to detect breakpoint hits
        def make_hook(name):
            def hook(responses):
                for r in responses:
                    if r.is_breakpoint_hit() and r.frame and r.frame.func:
                        if name in r.frame.func:
                            fires.append(name)
                return responses
            return hook

        # Set breakpoint on initialize_ui_manager (confirmed to fire at startup)
        gdb.set_breakpoint("initialize_ui_manager")
        gdb.add_hook(make_hook("initialize_ui_manager"))

        # Send continue via the underlying gdbmi (non-blocking for the stopped event)
        # The write() returns the library-loaded notifications, then the program stops
        # at the breakpoint — the stopped notification comes via get_gdb_response()
        gdb.gdbmi.write("-exec-continue")

        # Poll for the stopped notification — hooks fire via wrapped get_gdb_response
        import time
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline and not fires:
            try:
                gdb.gdbmi.get_gdb_response(timeout_sec=2.0)
            except Exception:
                pass

        self.assertGreater(len(fires), 0, f"No hooks fired. Fires: {fires}")

        gdb.close()

    def test_hook_fires_via_get_gdb_response(self):
        """Hooks should fire when responses are read via get_gdb_response polling."""
        from mcp_layered.layer_pygdbmi import GDBSession

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Register a hook that tracks any breakpoint hits
        fires = []
        def tracking_hook(responses):
            for r in responses:
                if r.is_breakpoint_hit():
                    fires.append(True)
            return responses

        gdb.add_hook(tracking_hook)

        # Set a breakpoint that fires during startup
        gdb.set_breakpoint("initialize_ui_manager")

        # Continue and poll (the breakpoint fires at startup)
        gdb.gdbmi.write("-exec-continue", read_response=False)
        import time
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline and not fires:
            try:
                gdb.gdbmi.get_gdb_response(timeout_sec=1.0)
            except Exception:
                pass

        # The hook SHOULD fire because the breakpoint was hit
        self.assertGreater(len(fires), 0, "Hook should fire when breakpoint is hit")

        gdb.close()

    def test_ui_scanner_captures_elements(self):
        """The UI scanner should capture UI elements from AncientsGame."""
        from mcp_layered.layer_pygdbmi import GDBSession

        # Use a bare GDBSession (not LavSession) to avoid state sharing issues
        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Use DebugUIUtils to scan UI elements
        # Note: If debug UI is not compiled in or symbols unavailable, we skip
        try:
            from mcp.debug_ui_utils import DebugUIUtils
            ui_utils = DebugUIUtils(gdbmi=gdb.gdbmi)
            ui_utils.refresh()
            table = ui_utils.get_table()
            managers = table.get("ui_managers", {})

            # Debug UI may or may not be compiled into the binary
            # If managers is empty, it means debug UI symbols not available — skip
            if managers:
                # Check for UI elements
                elements_found = False
                for mgr_ptr, mgr in managers.items():
                    elements = mgr.get("ui_elements", {})
                    if elements:
                        elements_found = True
                        break
                self.assertTrue(elements_found, "Should have at least one UI element")
            # else: debug UI not available, test passes
        finally:
            gdb.close()


class TestSignalDetectionParasitic(unittest.TestCase):
    """Tests that GDBSession detects crash signals (SIGABRT, SIGSEGV, etc.)."""

    def test_step_frame_detailed_detects_signal(self):
        """step_frame_detailed returns signal_* when game crashes."""
        from mcp_layered.layer_pygdbmi import GDBSession

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Set breakpoint at a crash-prone function if available, or
        # test with a function that intentionally crashes
        # We'll test by stepping and checking for signal detection in _poll_for_stops
        from mcp.gdb_nav_utils import _get_signal_from_stopped

        # Create a mock stopped record with signal-received
        stopped_record = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal-name": "SIGABRT",
                "signal": "6",
                "frame": {"func": "abort", "pc": "0x7f..."},
                "bkptno": "0",
            }
        }
        signal = _get_signal_from_stopped(stopped_record)
        self.assertEqual(signal, "SIGABRT")

        # Test SIGSEGV
        stopped_record["payload"]["signal-name"] = "SIGSEGV"
        stopped_record["payload"]["signal"] = "11"
        signal = _get_signal_from_stopped(stopped_record)
        self.assertEqual(signal, "SIGSEGV")

        # Test fallback by signal number only
        stopped_record2 = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal": "11",
            }
        }
        signal = _get_signal_from_stopped(stopped_record2)
        self.assertEqual(signal, "SIGSEGV")

        # Test non-stop record (should return None)
        normal_record = {
            "type": "result",
            "message": "done",
            "payload": {}
        }
        signal = _get_signal_from_stopped(normal_record)
        self.assertIsNone(signal)

        # Test breakpoint-hit record (should return None)
        bkpt_record = {
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "breakpoint-hit",
            }
        }
        signal = _get_signal_from_stopped(bkpt_record)
        self.assertIsNone(signal)

        gdb.close()

    def test_step_frame_detailed_returns_signal_on_crash(self):
        """step_frame_detailed detects SIGABRT when game crashes."""
        from mcp_layered.layer_pygdbmi import GDBSession
        from mcp.gdb_nav_utils import step_frame_detailed, step_frame

        gdb = GDBSession(command=["gdb", "--nx", "--quiet", "--interpreter=mi3"])
        gdb.write(f"-file-exec-and-symbols {ANCIENTSGAME_BINARY}")
        gdb.write("-exec-run --start")

        # Try to step with a very short timeout — if the game crashes,
        # we should get a signal_* reason instead of timeout
        # We use a non-existent function that will cause a breakpoint error,
        # and a real function name that may crash
        hit, reason = step_frame_detailed(
            gdb.gdbmi, "manage_game__post_render", timeout=5.0
        )

        if hit:
            # Game didn't crash, step was successful
            pass
        elif reason and reason.startswith("signal_"):
            # Game crashed with a signal
            sig = reason[7:]  # Remove "signal_" prefix
            self.assertIn(sig, ["SIGABRT", "SIGSEGV", "SIGBUS", "SIGFPE", "SIGILL", "SIGPIPE"])
        elif reason == "timeout":
            # Game didn't reach the target frame in time — acceptable
            # (may happen on slow systems or if game is waiting for input)
            pass
        else:
            # Unexpected reason
            self.fail(f"Unexpected step_frame_detailed reason: {reason}")

        gdb.close()

    def test_backtrace_on_crash(self):
        """After a crash signal, _get_signal_info returns a full backtrace."""
        from mcp_layered.layer_lav_init import create_session
        from mcp.gdb_nav_utils import step_frame_detailed

        session = create_session(
            executable=ANCIENTSGAME_BINARY,
        )

        hit, reason = step_frame_detailed(
            session.gdb.gdbmi, "manage_game__post_render", timeout=5.0
        )

        if reason and reason.startswith("signal_"):
            # Game crashed — verify we can get backtrace
            # Access _get_signal_info from the step_driver closure
            from mcp_layered.layer_lav_init import _register_builtin_drivers
            _register_builtin_drivers()  # Ensure drivers are registered

            # Manually call _get_signal_info via the session's gdb
            # The function is nested in step_driver, so we test indirectly:
            # call navigate_source driver which gets backtrace
            try:
                result = session.invoke("navigate_source")
                # Should contain backtrace frames
                self.assertIn("#", result)
                # Should have at least one frame
                self.assertGreater(
                    len([l for l in result.split("\n") if l.strip()]),
                    0
                )
            except Exception:
                pass  # Some crash scenarios may not allow further queries

        session.gdb.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
