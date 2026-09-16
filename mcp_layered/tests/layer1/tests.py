"""Tests for Layer 1a (debug_response.py) and Layer 1b (layer_pygdbmi.py).

Run from repo root: python3 -m pytest mcp_layered/tests/layer1/tests.py -v
Or:  python3 mcp_layered/tests/layer1/tests.py
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure we can import the layer modules
# tests.py is at mcp_layered/tests/layer1/tests.py
# mcp_layered is at /home/shalidor/Projects/Lavender_Dev/mcp_layered/
# We need the parent of mcp_layered in sys.path for "from mcp_layered.X import Y"
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_REPOS_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPOS_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.debug_response import (
    DebugResponse,
    Frame,
    Breakpoint,
    ResponseType,
    StoppedReason,
    parse,
    parse_stream,
)


# --------------------------------------------------------------------------- #
# Layer 1a Tests: debug_response.py
# --------------------------------------------------------------------------- #


class TestDebugResponseParsing(unittest.TestCase):
    """Test parsing of pygdbmi JSON into DebugResponse objects."""

    def test_parse_notify_breakpoint_hit(self):
        """A breakpoint-hit stopped notification parses correctly."""
        raw = [{
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "breakpoint-hit",
                "bkptno": "1",
                "frame": {
                    "pc": "0x55555555513d",
                    "func": "my_func",
                    "args": [],
                    "file": "/tmp/test_bp.c",
                    "line": "2",
                },
                "thread-id": "1",
            },
            "token": None,
            "stream": "stdout",
        }]
        results = parse(raw)
        self.assertEqual(len(results), 1)
        r = results[0]

        self.assertEqual(r.type, ResponseType.NOTIFY)
        self.assertEqual(r.reason, "breakpoint-hit")
        self.assertTrue(r.is_breakpoint_hit())
        self.assertEqual(r.bkpt_num, "1")
        self.assertIsNotNone(r.frame)
        self.assertEqual(r.frame.func, "my_func")
        self.assertEqual(r.frame.pc, "0x55555555513d")
        self.assertEqual(r.frame.line, 2)
        self.assertEqual(r.frame.file, "/tmp/test_bp.c")

    def test_parse_notify_signal_received(self):
        """A signal-received stopped notification parses correctly."""
        raw = [{
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal": "SIGSEGV",
                "signal-name": "SIGSEGV",
                "signal-code": "0",
                "frame": {
                    "pc": "0x7fff",
                    "func": "crashing_func",
                    "file": "crash.c",
                    "line": "10",
                },
            },
            "token": None,
            "stream": "stdout",
        }]
        results = parse(raw)
        r = results[0]

        self.assertTrue(r.is_signal())
        self.assertEqual(r.signal, "SIGSEGV")
        self.assertEqual(r.signal_name, "SIGSEGV")
        self.assertEqual(r.signal_code, "0")
        self.assertEqual(r.frame.func, "crashing_func")

    def test_parse_notify_single_step(self):
        """A single-step stopped notification parses correctly."""
        raw = [{
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "single-step",
                "frame": {
                    "pc": "0x1000",
                    "func": "main",
                    "file": "test.c",
                    "line": "5",
                },
            },
        }]
        results = parse(raw)
        r = results[0]
        self.assertEqual(r.reason, "single-step")
        self.assertTrue(r.is_stopped())
        self.assertEqual(r.frame.func, "main")

    def test_parse_notify_stop_with_unknown_reason(self):
        """A stop with reason not in our known list still triggers is_stopped."""
        # 'exited' is the GDB reason for a process exit
        raw = [{
            "type": "notify",
            "message": "stopped",
            "payload": {"reason": "exited-normally"},
        }]
        results = parse(raw)
        r = results[0]
        self.assertTrue(r.is_stopped())
        self.assertFalse(r.is_breakpoint_hit())

    def test_parse_result_done(self):
        """A ^done result parses correctly."""
        raw = [{"type": "result", "message": "done", "payload": {"num": "1"}}]
        results = parse(raw)
        r = results[0]

        self.assertEqual(r.type, ResponseType.RESULT)
        self.assertTrue(r.is_success())
        self.assertFalse(r.is_error())

    def test_parse_result_error(self):
        """A ^error result parses correctly."""
        raw = [{
            "type": "result",
            "message": "error",
            "payload": {"msg": "No symbol for main."},
        }]
        results = parse(raw)
        r = results[0]

        self.assertTrue(r.is_error())
        self.assertEqual(r.reason, "No symbol for main.")

    def test_parse_result_running(self):
        """A ^running result parses correctly."""
        raw = [{"type": "result", "message": "running", "payload": None}]
        results = parse(raw)
        r = results[0]
        self.assertTrue(r.is_success())

    def test_parse_console_output(self):
        """Console output types parse as TARGET."""
        for rtype in ("console", "log", "output"):
            raw = [{"type": rtype, "message": None, "payload": "hello"}]
            results = parse(raw)
            self.assertEqual(results[0].type, ResponseType.TARGET,
                             f"Failed for type={rtype}")

    def test_parse_empty_dict(self):
        """Empty dict {} is classified as PROMPT."""
        raw = [{}]
        results = parse(raw)
        self.assertEqual(len(results), 0)  # filtered out

    def test_parse_none_payload(self):
        """A None payload doesn't crash."""
        raw = [{"type": "result", "message": "done", "payload": None}]
        results = parse(raw)
        r = results[0]
        self.assertEqual(r.type, ResponseType.RESULT)
        self.assertEqual(r.payload, {})

    def test_parse_none_message(self):
        """A null message doesn't crash."""
        raw = [{"type": "notify", "message": None, "payload": {"reason": "stopped"}}]
        results = parse(raw)
        r = results[0]
        self.assertEqual(r.reason, "stopped")

    def test_parse_mixed_list(self):
        """A mixed list of all response types parses in order."""
        raw = [
            {},
            {"type": "notify", "message": "stopped", "payload": {"reason": "breakpoint-hit", "bkptno": "1"}},
            {"type": "console", "message": None, "payload": "output"},
            {"type": "result", "message": "done", "payload": {"num": "1"}},
        ]
        results = parse(raw)
        types = [r.type for r in results]
        # Empty dict filtered, 3 remain
        self.assertEqual(len(results), 3)
        self.assertEqual(types[0], ResponseType.NOTIFY)
        self.assertEqual(types[1], ResponseType.TARGET)
        self.assertEqual(types[2], ResponseType.RESULT)

    def test_parse_stream_alias(self):
        """parse_stream is an alias for parse."""
        raw = [{"type": "result", "message": "done", "payload": {"num": "1"}}]
        results1 = parse(raw)
        results2 = parse_stream(raw)
        self.assertEqual(len(results1), len(results2))


class TestDebugResponsePredicates(unittest.TestCase):
    """Test the convenience predicates on DebugResponse."""

    def test_is_stopped_for_stop_reasons(self):
        """is_stopped() returns True for all stopped reasons."""
        for reason in [
            "breakpoint-hit", "signal-received", "function-finished",
            "single-step", "watchpoint-triggered", "exited", "exited-normally",
            "exited-signalled", "exited-with-signal",
        ]:
            raw = [{"type": "notify", "message": "stopped", "payload": {"reason": reason}}]
            r = parse(raw)[0]
            self.assertTrue(r.is_stopped(), f"Failed for reason={reason}")

    def test_is_stopped_false_for_non_stop(self):
        """is_stopped() returns False for non-stop notifications."""
        raw = [{"type": "notify", "message": "library-loaded", "payload": {}}]
        r = parse(raw)[0]
        self.assertFalse(r.is_stopped())

    def test_is_breakpoint_hit_specificity(self):
        """is_breakpoint_hit() only True for breakpoint-hit."""
        raw_bp = [{"type": "notify", "message": "stopped", "payload": {"reason": "breakpoint-hit", "bkptno": "1"}}]
        r = parse(raw_bp)[0]
        self.assertTrue(r.is_breakpoint_hit())

        raw_sig = [{"type": "notify", "message": "stopped", "payload": {"reason": "signal-received"}}]
        r = parse(raw_sig)[0]
        self.assertFalse(r.is_breakpoint_hit())


# --------------------------------------------------------------------------- #
# Layer 1b Tests: layer_pygdbmi.py
# --------------------------------------------------------------------------- #


class TestGDBSessionHooks(unittest.TestCase):
    """Test the hook system in GDBSession using a mock GDBController."""

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_add_and_remove_hook(self, mock_gdb_controller_cls):
        """Hooks can be added and removed."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [{"type": "result", "message": "done", "payload": {"num": "1"}}]
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        hook_calls = []
        def my_hook(responses):
            hook_calls.append(len(responses))
            return responses

        gdb.add_hook(my_hook)
        gdb.write("-gdb-version")
        self.assertEqual(len(hook_calls), 1)

        gdb.remove_hook(my_hook)
        gdb.write("-gdb-version")
        self.assertEqual(len(hook_calls), 1)  # still 1, hook was removed

        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_clear_hooks(self, mock_gdb_controller_cls):
        """clear_hooks removes all hooks."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = []
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        calls = []
        gdb.add_hook(lambda r: calls.append("a") or r)
        gdb.add_hook(lambda r: calls.append("b") or r)

        gdb.clear_hooks()
        gdb.write("test")
        self.assertEqual(len(calls), 0)

        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_hooks_called_in_order(self, mock_gdb_controller_cls):
        """Hooks are called in registration order."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [{"type": "result", "message": "done"}]
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        order = []
        gdb.add_hook(lambda r: order.append(1) or r)
        gdb.add_hook(lambda r: order.append(2) or r)
        gdb.add_hook(lambda r: order.append(3) or r)

        gdb.write("test")
        self.assertEqual(order, [1, 2, 3])

        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_hook_can_modify_responses(self, mock_gdb_controller_cls):
        """A hook can filter out responses before returning to caller."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [
            {"type": "result", "message": "done"},
            {"type": "console", "message": None, "payload": "noise"},
        ]
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        def filter_response(responses):
            return [r for r in responses if r.type != ResponseType.TARGET]

        gdb.add_hook(filter_response)
        result = gdb.write("test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, ResponseType.RESULT)

        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_write_returns_parsed_responses(self, mock_gdb_controller_cls):
        """write() returns DebugResponse objects, not raw dicts."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [{"type": "result", "message": "done", "payload": {"num": "1"}}]
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        result = gdb.write("-gdb-version")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], DebugResponse)

        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_write_after_close_raises(self, mock_gdb_controller_cls):
        """write() raises after close()."""
        mock_gdb = MagicMock()
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()
        gdb.close()

        with self.assertRaises(RuntimeError):
            gdb.write("test")

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_gdb_path_property(self, mock_gdb_controller_cls):
        """gdb_path returns the configured GDB executable."""
        mock_gdb = MagicMock()
        mock_gdb.command = ["/usr/bin/gdb"]
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()
        self.assertEqual(gdb.gdb_path, "/usr/bin/gdb")
        gdb.close()


class TestGDBSessionHookFactories(unittest.TestCase):
    """Test the hook factory functions."""

    def test_logging_hook_factory(self):
        """logging_hook_factory creates a hook that calls callback."""
        from mcp_layered.layer_pygdbmi import logging_hook_factory

        calls = []
        hook = logging_hook_factory(lambda res: calls.append(len(res)))

        responses = [{"type": "result", "message": "done"}]
        parsed = parse(responses)

        result = hook(parsed)
        self.assertEqual(len(calls), 1)
        self.assertIs(result, parsed)  # returns same list

    def test_on_breakpoint_hook_factory(self):
        """on_breakpoint_hook_factory only fires on breakpoint-hit."""
        from mcp_layered.layer_pygdbmi import on_breakpoint_hook_factory

        calls = []
        hook = on_breakpoint_hook_factory(lambda res: calls.append("fired"))

        # Non-breakpoint response
        non_bp = parse([{"type": "result", "message": "done"}])
        hook(non_bp)
        self.assertEqual(len(calls), 0)

        # Breakpoint-hit response
        bp_hit = parse([{
            "type": "notify",
            "message": "stopped",
            "payload": {"reason": "breakpoint-hit", "bkptno": "1"},
        }])
        hook(bp_hit)
        self.assertEqual(len(calls), 1)


# --------------------------------------------------------------------------- #
# delete_breakpoint + BreakpointHook (encapsulated, toggleable breakpoint)
#
# Note: GDBSession.__init__ runs patch_gdbmi_timeouts(), which reassigns
# mock_gdb.write to a thin wrapper (capturing the original MagicMock). So we
# capture `orig_write = mock_gdb.write` BEFORE constructing the session, and
# assert on that original mock's call list (the wrapper forwards to it).
# --------------------------------------------------------------------------- #


def _bp_done(bp_number="3"):
    return [{"type": "result", "message": "done",
             "payload": {"bkpt": {"number": bp_number}}}]


def _cmds(orig_write):
    """First positional arg (the MI command) of each recorded write() call."""
    return [c[0][0] for c in orig_write.call_args_list if c[0]]


class TestGDBSessionDeleteBreakpoint(unittest.TestCase):
    """Test GDBSession.delete_breakpoint (the inverse of set_breakpoint)."""

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_delete_sends_break_delete(self, mock_cls):
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [{"type": "result", "message": "done",
                                        "payload": {}}]
        orig_write = mock_gdb.write
        mock_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()
        self.assertTrue(gdb.delete_breakpoint(3))
        self.assertIn("-break-delete 3", _cmds(orig_write))
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_delete_none_is_noop(self, mock_cls):
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = []
        orig_write = mock_gdb.write
        mock_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()
        self.assertFalse(gdb.delete_breakpoint(None))
        orig_write.assert_not_called()
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_delete_error_returns_false(self, mock_cls):
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [
            {"type": "result", "message": "error",
             "payload": {"msg": "No such breakpoint"}}
        ]
        mock_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()
        self.assertFalse(gdb.delete_breakpoint(99))
        gdb.close()


class TestBreakpointHook(unittest.TestCase):
    """Test the encapsulated BreakpointHook (enable/disable toggles the bp)."""

    def _gdb(self, mock_cls, bp_number="3"):
        """Build a GDBSession over a mock controller whose write ^done carries
        a bkpt number. ``mock_cls`` is the GdbController mock supplied by the
        caller's @patch decorator. Returns (gdb, orig_write) where orig_write
        is the original mock write (captured before the session patched it)."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = _bp_done(bp_number)
        orig_write = mock_gdb.write
        mock_cls.return_value = mock_gdb
        from mcp_layered.layer_pygdbmi import GDBSession
        return GDBSession(), orig_write

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_enable_sets_bp_and_registers_hook(self, mock_cls):
        gdb, orig_write = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "test", "my_func", lambda r: r)
        self.assertFalse(hook.enabled)
        self.assertTrue(hook.enable())
        self.assertTrue(hook.enabled)
        self.assertEqual(hook.bp_number, "3")
        self.assertIn("-break-insert my_func", _cmds(orig_write))
        self.assertEqual(len(gdb._hooks), 1)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_disable_deletes_bp_and_removes_hook(self, mock_cls):
        gdb, orig_write = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "test", "my_func", lambda r: r)
        hook.enable()
        orig_write.call_args_list.clear()
        hook.disable()
        self.assertFalse(hook.enabled)
        self.assertIsNone(hook.bp_number)
        self.assertIn("-break-delete 3", _cmds(orig_write))
        self.assertEqual(len(gdb._hooks), 0)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_enable_idempotent(self, mock_cls):
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "test", "my_func", lambda r: r)
        hook.enable()
        n = len(gdb._hooks)
        hook.enable()
        self.assertEqual(len(gdb._hooks), n)
        self.assertTrue(hook.enabled)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_disable_idempotent_when_never_enabled(self, mock_cls):
        gdb, orig_write = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "test", "my_func", lambda r: r)
        hook.disable()
        self.assertFalse(hook.enabled)
        self.assertIsNone(hook.bp_number)
        orig_write.assert_not_called()
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_enable_failure_stays_disabled(self, mock_cls):
        """If the symbol can't be broken on, enable() returns False, no hook."""
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = [
            {"type": "result", "message": "error", "payload": {"msg": "No symbol"}}
        ]
        mock_cls.return_value = mock_gdb
        from mcp_layered.layer_pygdbmi import GDBSession, BreakpointHook
        gdb = GDBSession()
        hook = BreakpointHook(gdb, "test", "no_such_func", lambda r: r)
        self.assertFalse(hook.enable())
        self.assertFalse(hook.enabled)
        self.assertEqual(len(gdb._hooks), 0)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_hook_fires_on_matching_function(self, mock_cls):
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        fired = []
        hook = BreakpointHook(
            gdb, "process.add", "add_process_to__process_table",
            lambda r: fired.append(1) or r)
        hook.enable()
        bp_hit = parse([{
            "type": "notify", "message": "stopped",
            "payload": {"reason": "breakpoint-hit", "bkptno": "3",
                        "frame": {"func": "add_process_to__process_table",
                                  "file": "x.c", "line": "50"}},
        }])
        for h in gdb._hooks:
            h(bp_hit)
        self.assertEqual(len(fired), 1)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_hook_ignores_other_function(self, mock_cls):
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        fired = []
        hook = BreakpointHook(
            gdb, "process.add", "add_process_to__process_table",
            lambda r: fired.append(1) or r)
        hook.enable()
        other = parse([{
            "type": "notify", "message": "stopped",
            "payload": {"reason": "breakpoint-hit", "bkptno": "7",
                        "frame": {"func": "some_other_func",
                                  "file": "y.c", "line": "9"}},
        }])
        for h in gdb._hooks:
            h(other)
        self.assertEqual(len(fired), 0)
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_line_target_hook_fires_on_file_line(self, mock_cls):
        """A file:line target matches on frame file:line, not function name."""
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        fired = []
        hook = BreakpointHook(gdb, "line", "game.c:702",
                              lambda r: fired.append(1) or r)
        hook.enable()
        hit = parse([{
            "type": "notify", "message": "stopped",
            "payload": {"reason": "breakpoint-hit", "bkptno": "3",
                        "frame": {"func": "manage_game",
                                  "file": "/path/game.c", "line": "702"}},
        }])
        for h in gdb._hooks:
            h(hit)
        self.assertEqual(len(fired), 1)
        gdb.close()


class TestBreakpointHookCapture(unittest.TestCase):
    """Test the gated capture: GDB-I/O runs only in a safe, non-nested context,
    accumulates in captured_events, and is drained by consume_events()."""

    def _gdb(self, mock_cls):
        mock_gdb = MagicMock()
        mock_gdb.write.return_value = _bp_done("3")
        orig_write = mock_gdb.write
        mock_cls.return_value = mock_gdb
        from mcp_layered.layer_pygdbmi import GDBSession
        return GDBSession(), orig_write

    def _bp_hit(self, func="add_process_to__process_table"):
        return parse([{
            "type": "notify", "message": "stopped",
            "payload": {"reason": "breakpoint-hit", "bkptno": "3",
                        "frame": {"func": func, "file": "x.c", "line": "50"}},
        }])

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_capture_runs_in_safe_context(self, mock_cls):
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "p", "add_process_to__process_table",
                              capture=lambda g, r: {"func": r[0].frame.func})
        hook.enable()
        gdb._in_nested_read = False  # safe (stopped) context
        for h in gdb._hooks:
            h(self._bp_hit())
        self.assertEqual(len(hook.captured_events), 1)
        evts = hook.consume_events()
        self.assertEqual(evts, [{"func": "add_process_to__process_table"}])
        self.assertEqual(hook.captured_events, [])  # drained
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_capture_skipped_in_nested_context(self, mock_cls):
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        calls = []
        hook = BreakpointHook(gdb, "p", "add_process_to__process_table",
                              capture=lambda g, r: calls.append(1) or {"func": "x"})
        hook.enable()
        gdb._in_nested_read = True  # nested (deadlock) context
        for h in gdb._hooks:
            h(self._bp_hit())
        self.assertEqual(calls, [])  # capture must NOT run
        self.assertEqual(hook.captured_events, [])
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_capture_failure_is_contained(self, mock_cls):
        """A capture exception is swallowed; the driver is not broken, no event."""
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        def bad(g, r):
            raise RuntimeError("boom")
        hook = BreakpointHook(gdb, "p", "add_process_to__process_table",
                              capture=bad)
        hook.enable()
        gdb._in_nested_read = False
        for h in gdb._hooks:
            h(self._bp_hit())  # must not raise
        self.assertEqual(hook.captured_events, [])
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_handler_fires_even_when_capture_gated(self, mock_cls):
        """The lightweight handler fires in any context; only the capture is gated."""
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        fired, calls = [], []
        hook = BreakpointHook(
            gdb, "p", "add_process_to__process_table",
            handler=lambda r: fired.append(1) or r,
            capture=lambda g, r: calls.append(1) or {"x": 1})
        hook.enable()
        gdb._in_nested_read = True  # nested
        for h in gdb._hooks:
            h(self._bp_hit())
        self.assertEqual(fired, [1])  # handler fired
        self.assertEqual(calls, [])  # capture skipped
        gdb.close()

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_multiple_events_accumulate(self, mock_cls):
        """Multiple hits accumulate; consume_events returns all and clears."""
        gdb, _ = self._gdb(mock_cls)
        from mcp_layered.layer_pygdbmi import BreakpointHook
        hook = BreakpointHook(gdb, "p", "add_process_to__process_table",
                              capture=lambda g, r: {"func": r[0].frame.func})
        hook.enable()
        gdb._in_nested_read = False
        for _ in range(3):
            for h in gdb._hooks:
                h(self._bp_hit())
        self.assertEqual(len(hook.captured_events), 3)
        evts = hook.consume_events()
        self.assertEqual(len(evts), 3)
        self.assertEqual(hook.consume_events(), [])  # second drain is empty
        gdb.close()


# --------------------------------------------------------------------------- #
# Activity Timeout Tests
# --------------------------------------------------------------------------- #


class TestSignalDetection(unittest.TestCase):
    """Tests for unified signal detection in layer_pygdbmi."""

    def test_detect_signal_from_debug_response(self):
        """detect_signal returns signal name from DebugResponse.is_signal()."""
        from mcp_layered.layer_pygdbmi import detect_signal
        from mcp_layered.debug_response import DebugResponse

        # Create a signal-received DebugResponse
        resp = DebugResponse.from_dict({
            "type": "notify",
            "message": "stopped",
            "payload": {
                "reason": "signal-received",
                "signal-name": "SIGABRT",
                "frame": {"func": "abort"},
            }
        })

        sig = detect_signal([resp])
        self.assertEqual(sig, "SIGABRT")

    def test_detect_signal_no_signal(self):
        """detect_signal returns None when no signal in responses."""
        from mcp_layered.layer_pygdbmi import detect_signal
        from mcp_layered.debug_response import DebugResponse

        resp = DebugResponse.from_dict({
            "type": "result",
            "message": "done",
            "payload": {}
        })

        sig = detect_signal([resp])
        self.assertIsNone(sig)

    def test_detect_signal_mixed_responses(self):
        """detect_signal finds signal in mixed response list."""
        from mcp_layered.layer_pygdbmi import detect_signal
        from mcp_layered.debug_response import DebugResponse

        normal = DebugResponse.from_dict({
            "type": "result", "message": "done", "payload": {}
        })
        signal_resp = DebugResponse.from_dict({
            "type": "notify", "message": "stopped",
            "payload": {"reason": "signal-received", "signal-name": "SIGSEGV"}
        })

        sig = detect_signal([normal, signal_resp])
        self.assertEqual(sig, "SIGSEGV")


class TestActivityTimeout(unittest.TestCase):
    """Tests for activity-based timeout logic in GDBSession."""

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_poll_returns_none_on_idle_timeout(self, mock_gdb_controller_cls):
        """poll_with_activity_timeout returns None when no response arrives."""
        mock_gdb = MagicMock()
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession(timeout_sec=1, activity_timeout=False)
        gdb._orig_get_response = MagicMock(return_value=None)

        result = gdb.poll_with_activity_timeout(
            overall_timeout=0.5, idle_timeout=0.5, call_timeout=0.1
        )
        self.assertIsNone(result)

    @patch("mcp_layered.layer_pygdbmi.GdbController")
    def test_poll_resets_idle_on_response(self, mock_gdb_controller_cls):
        """poll_with_activity_timeout resets idle timer on each response."""
        mock_gdb = MagicMock()
        mock_gdb_controller_cls.return_value = mock_gdb

        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession(timeout_sec=1, activity_timeout=False)
        # First returns None, second returns a response
        gdb._orig_get_response = MagicMock(side_effect=[
            None, [{"type": "notify", "message": "stopped"}]
        ])

        result = gdb.poll_with_activity_timeout(
            overall_timeout=5.0, idle_timeout=1.0, call_timeout=0.1
        )
        self.assertIsNotNone(result)


# --------------------------------------------------------------------------- #
# Integration Tests (require GDB)
# --------------------------------------------------------------------------- #


class TestIntegrationLavenderDev(unittest.TestCase):
    """Integration tests against ./build/sdl/Lavender_Dev.

    These tests require:
    - pygdbmi installed
    - GDB installed
    - The Lavender_Dev binary at ./build/sdl/Lavender_Dev

    They are skipped if any of these are missing.
    """

    LAVENDER_BIN = os.path.join(os.getcwd(), "build", "sdl", "Lavender_Dev")

    @classmethod
    def setUpClass(cls):
        try:
            from pygdbmi.gdbcontroller import GdbController
            cls._has_pygdbmi = True
        except ImportError:
            cls._has_pygdbmi = False

        cls._has_gdb = os.system("which gdb > /dev/null 2>&1") == 0
        cls._has_binary = os.path.isfile(cls.LAVENDER_BIN)

        if cls._has_pygdbmi and cls._has_gdb and cls._has_binary:
            cls._skip = False
        else:
            cls._skip = True

    def setUp(self):
        if self._skip:
            self.skipTest("Missing pygdbmi, gdb, or ./build/sdl/Lavender_Dev")
        from mcp_layered.layer_pygdbmi import GDBSession
        self._gdb = GDBSession()

    def tearDown(self):
        self._gdb.close()

    def test_file_command(self):
        """Loading the Lavender_Dev binary works."""
        responses = self._gdb.write(f"file {self.LAVENDER_BIN}")
        results = [r for r in responses if r.type == ResponseType.RESULT]
        self.assertTrue(any(r.is_success() for r in results),
                        "file command should succeed")

    def test_response_count_and_types(self):
        """We get responses with expected types."""
        responses = self._gdb.write(f"info file")
        # May be cached by GDB, so just check we get something
        self.assertGreaterEqual(len(responses), 1)

        types = set(r.type for r in responses)
        # Should have at least RESULT
        self.assertIn(ResponseType.RESULT, types)

    def test_hook_fired_on_file_command(self):
        """A hook is called when executing file command."""
        from mcp_layered.layer_pygdbmi import GDBSession
        gdb = GDBSession()

        hook_calls = []
        def my_hook(responses):
            hook_calls.append(len(responses))
            return responses

        gdb.add_hook(my_hook)
        gdb.write(f"file {self.LAVENDER_BIN}")
        gdb.remove_hook(my_hook)
        gdb.close()

        self.assertEqual(len(hook_calls), 1)
        self.assertGreater(hook_calls[0], 0)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


if __name__ == "__main__":
    unittest.main(verbosity=2)
