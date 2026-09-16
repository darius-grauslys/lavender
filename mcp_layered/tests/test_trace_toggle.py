"""Tests for the `trace` command / Game_Action + Process hook toggle."""

import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered import layer_lav_init as L
from mcp_layered.layer_lav_config import LavConfig
from mcp_layered.layer_lav_cmd import COMMAND_ALIASES
from mcp_layered.layer_lav_mcp import TOOL_DEFINITIONS
from mcp_layered.layer_pygdbmi import BreakpointHook


class _FakeGDB:
    """Minimal GDBSession double for breakpoint-hook registration/toggle tests."""

    def __init__(self):
        self.hooks: list = []
        self.breakpoints: dict[str, str] = {}
        self.writes: list[str] = []
        self.is_closed = False
        self._in_nested_read = False
        self._ui_cache = None
        self._next_bp = 1

    def set_breakpoint(self, function, temporary=False):
        number = str(self._next_bp)
        self._next_bp += 1
        self.breakpoints[number] = function
        return number

    def delete_breakpoint(self, number):
        if number in self.breakpoints:
            del self.breakpoints[number]
            return True
        return False

    def add_hook(self, hook):
        if hook not in self.hooks:
            self.hooks.append(hook)

    def remove_hook(self, hook):
        if hook in self.hooks:
            self.hooks.remove(hook)

    def register_breakpoint_hook(self, function, hook_fn):
        self.set_breakpoint(function)
        self.add_hook(hook_fn)

    def write(self, command, **kwargs):
        self.writes.append(command)
        return []

    def close(self):
        self.is_closed = True


class TestTraceToggle(unittest.TestCase):
    def setUp(self):
        L.reset_trace_state()

    def tearDown(self):
        L.reset_trace_state()

    def _register(self) -> _FakeGDB:
        gdb = _FakeGDB()
        L._register_breakpoint_hooks_for_gdb(gdb)
        return gdb

    def _all_trace_hooks(self):
        process_hooks, game_action_hooks = L.trace_hook_groups()
        return process_hooks + game_action_hooks

    def test_registration_creates_receive_marker_and_deep_dispatch_hook(self):
        """Registration creates the receive marker (ON by default) and the deep
        dispatch-trace hook (OFF by default — a gated capture, not a handler)."""
        gdb = self._register()

        receive = L._game_action_trace_state["receive_hook"]
        self.assertIsInstance(receive, BreakpointHook)
        self.assertTrue(receive.enabled)
        self.assertEqual(receive.target, "receive_game_action_for__client")

        dispatch = L._ga_dispatch_deep_trace_state["hook"]
        self.assertIsInstance(dispatch, BreakpointHook)
        self.assertFalse(dispatch.enabled)  # OFF by default (deep trace)
        self.assertEqual(dispatch.target, "dispatch_game_action_for__client")
        # The deep-trace hook uses a gated `capture` (GDB I/O), not a handler.
        self.assertIsNotNone(dispatch._capture)
        self.assertIsNone(dispatch._handler)

    def test_registration_creates_enabled_frame_heartbeat_hook(self):
        """The frame heartbeat (reset__game_tick_timer, once per frame) is
        always registered and enabled — it arms the step watchdog."""
        gdb = self._register()

        heartbeat = L._frame_heartbeat_state["hook"]
        self.assertIsInstance(heartbeat, BreakpointHook)
        self.assertEqual(heartbeat.name, "frame.heartbeat")
        self.assertEqual(heartbeat.target, L.FRAME_HEARTBEAT_FUNC)
        self.assertTrue(heartbeat.enabled)
        # No GDB I/O: it has neither a handler nor a capture.
        self.assertIsNone(heartbeat._handler)
        self.assertIsNone(heartbeat._capture)

    def test_trace_driver_toggles_off_then_on(self):
        gdb = self._register()
        config = LavConfig()

        initial_hook_count = len(gdb.hooks)
        # 3 process + 1 game_action receive (trace group) + debug_error
        # reporting + initialize_ui_manager + scene transition + frame
        # heartbeat = 8. The deep dispatch-trace hook is registered but OFF by
        # default, so it is not an active (enabled) hook in this count.
        self.assertEqual(initial_hook_count, 8)

        result = L.trace_driver(gdb, config, {})
        self.assertIn("trace OFF", result)
        self.assertFalse(L._process_trace_state["enabled"])
        self.assertFalse(L._game_action_trace_state["enabled"])
        for hook in self._all_trace_hooks():
            self.assertFalse(hook.enabled)
        # The deep dispatch trace is NOT part of the `trace` (no-arg) group —
        # it stays disabled (off by default).
        self.assertFalse(L._ga_dispatch_deep_trace_state["hook"].enabled)
        # The debug_error reporting hook is NOT part of the trace group —
        # it stays enabled (non-fatal error reporting must keep working).
        self.assertTrue(L._debug_error_report_state["hook"].enabled)
        # The frame heartbeat is NOT part of the trace group either — the
        # step watchdog depends on it.
        heartbeat = L._frame_heartbeat_state["hook"]
        self.assertTrue(heartbeat.enabled)
        self.assertEqual(heartbeat.target, L.FRAME_HEARTBEAT_FUNC)

        # The 4 trace-group hooks (3 process + 1 receive) are removed; the
        # debug_error reporting, UI, scene + frame-heartbeat hooks remain.
        self.assertEqual(len(gdb.hooks), initial_hook_count - 4)
        self.assertEqual(
            set(gdb.breakpoints.values()),
            {"initialize_ui_manager", "debug_error", "reset__game_tick_timer"},
        )

        result = L.trace_driver(gdb, config, {})
        self.assertIn("trace ON", result)
        self.assertTrue(L._process_trace_state["enabled"])
        self.assertTrue(L._game_action_trace_state["enabled"])
        for hook in self._all_trace_hooks():
            self.assertTrue(hook.enabled)
        # The deep dispatch trace stays disabled (`trace` no-arg does not touch
        # it); its breakpoint is not re-established.
        self.assertFalse(L._ga_dispatch_deep_trace_state["hook"].enabled)

        self.assertEqual(len(gdb.hooks), initial_hook_count)
        bp_targets = set(gdb.breakpoints.values())
        for expected in (
            "add_process_to__process_table",
            "remove_process_from__process_table",
            "debug_error",
            "receive_game_action_for__client",
            "initialize_ui_manager",
            "reset__game_tick_timer",
        ):
            self.assertIn(expected, bp_targets)
        # The deep dispatch-trace breakpoint is absent (still off by default).
        self.assertNotIn("dispatch_game_action_for__client", bp_targets)

    def test_trace_disabled_before_registration_is_applied_at_registration(self):
        gdb = _FakeGDB()
        config = LavConfig()

        result = L.trace_driver(gdb, config, {})
        self.assertIn("trace OFF", result)
        self.assertIn("not registered", result)
        self.assertFalse(L._process_trace_state["enabled"])
        self.assertFalse(L._game_action_trace_state["enabled"])

        L._register_breakpoint_hooks_for_gdb(gdb)
        for hook in self._all_trace_hooks():
            self.assertIsNotNone(hook)
            self.assertFalse(hook.enabled)

        result = L.trace_driver(gdb, config, {})
        self.assertIn("trace ON", result)
        for hook in self._all_trace_hooks():
            self.assertTrue(hook.enabled)

    def test_trace_exposes_command_and_tool(self):
        self.assertEqual(COMMAND_ALIASES["trace"], "trace")
        tool_names = {tool["name"] for tool in TOOL_DEFINITIONS}
        self.assertIn("trace", tool_names)
        # The MCP `trace` tool exposes the optional `target` argument.
        trace_tool = next(t for t in TOOL_DEFINITIONS if t["name"] == "trace")
        self.assertIn("target", trace_tool["inputSchema"]["properties"])

    def test_trace_ga_toggles_deep_dispatch_trace(self):
        """`trace ga` toggles the deep dispatch trace (default OFF -> ON -> OFF)."""
        gdb = self._register()
        config = LavConfig()
        dispatch = L._ga_dispatch_deep_trace_state["hook"]
        self.assertFalse(dispatch.enabled)  # off by default

        result = L.trace_driver(gdb, config, {"target": "ga"})
        self.assertIn("deep-trace ON", result)
        self.assertTrue(L._ga_dispatch_deep_trace_state["enabled"])
        self.assertTrue(dispatch.enabled)
        self.assertIn("dispatch_game_action_for__client",
                       set(gdb.breakpoints.values()))

        result = L.trace_driver(gdb, config, {"target": "ga"})
        self.assertIn("deep-trace OFF", result)
        self.assertFalse(L._ga_dispatch_deep_trace_state["enabled"])
        self.assertFalse(dispatch.enabled)
        self.assertNotIn("dispatch_game_action_for__client",
                         set(gdb.breakpoints.values()))
        # The plain `trace` group is unaffected by `trace ga`.
        self.assertTrue(L._game_action_trace_state["receive_hook"].enabled)

    def test_trace_ga_aliases(self):
        """`game_action` / `dispatch` / `game-action` are accepted aliases."""
        for alias in ("ga", "game_action", "game-action", "dispatch"):
            L.reset_trace_state()
            gdb = self._register()
            config = LavConfig()
            L.trace_driver(gdb, config, {"target": alias})
            self.assertTrue(L._ga_dispatch_deep_trace_state["enabled"],
                            f"alias {alias!r} should enable the deep trace")

    def test_trace_ga_before_registration_is_applied_at_registration(self):
        gdb = _FakeGDB()
        config = LavConfig()

        result = L.trace_driver(gdb, config, {"target": "ga"})
        self.assertIn("deep-trace ON", result)
        self.assertIn("not registered", result)
        self.assertTrue(L._ga_dispatch_deep_trace_state["enabled"])

        L._register_breakpoint_hooks_for_gdb(gdb)
        dispatch = L._ga_dispatch_deep_trace_state["hook"]
        self.assertIsNotNone(dispatch)
        self.assertTrue(dispatch.enabled)  # applied at registration

        result = L.trace_driver(gdb, config, {"target": "ga"})
        self.assertIn("deep-trace OFF", result)
        self.assertFalse(dispatch.enabled)


if __name__ == "__main__":
    unittest.main(verbosity=2)
