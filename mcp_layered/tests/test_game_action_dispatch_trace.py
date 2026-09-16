"""Tests for the deep Game_Action dispatch trace in layer_lav_init.

Run from repo root: python3 -m unittest mcp_layered.tests.test_game_action_dispatch_trace -v
Or:                 python3 mcp_layered/tests/test_game_action_dispatch_trace.py

The deep trace captures, at the dispatch hit (a safe, non-nested context), a
callee backtrace + a client-scanner snapshot; the records are drained at a safe
point by resolve_game_action_dispatch_trace(). The capture (GDB I/O) is
exercised against a mocked GDBSession; the resolve against a real BreakpointHook
+ a temp log file. No live GDB is required.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPOS_ROOT = os.path.abspath(os.path.join(_LAYERED_ROOT, ".."))
sys.path.insert(0, _REPOS_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.debug_response import parse
from mcp_layered.layer_pygdbmi import GDBSession, BreakpointHook
import mcp_layered.layer_lav_init as L


def _result_done(payload):
    """A raw (pygdbmi-format) ^done record — what a mocked GdbController.write
    returns. GDBSession.write() runs parse() over it."""
    return [{"type": "result", "message": "done", "payload": payload}]


def _bp_hit(func="dispatch_game_action_for__client", args=None, bkpt="4"):
    payload = {"reason": "breakpoint-hit", "bkptno": bkpt,
               "frame": {"func": func, "file": "client.c", "line": "315",
                         "args": args or []}}
    return parse([{"type": "notify", "message": "stopped", "payload": payload}])


def _make_gdb(write_side_effect):
    """A GDBSession over a mock controller whose write() uses the given
    side_effect (command -> response list)."""
    with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
        mock_gdb = MagicMock()
        mock_gdb.write.side_effect = write_side_effect
        mock_cls.return_value = mock_gdb
        return GDBSession()


def _client_scanner_struct(kind="Game_Action_Kind__Global_Space__Store",
                           uuid=3601031185, client_uuid=536870912,
                           center=(0, 63, 2), flags=2, outbound_count=5):
    """A realistic ``-data-evaluate-expression $debug_client_scanner`` printout.

    Uses %-formatting (not f-strings) so the literal ``{``/``}`` braces in the
    gdb struct printout are not treated as format fields.
    """
    return (
        "$5 = {p_game = 0x5555556e3000 <game>, "
        "p_client__current = 0x5555556e3a00, "
        "p_game_action__inbound__current = 0x0, "
        "p_game_action__outbound__current = 0x5555556e4100, "
        "m_refresh = 0x555555557100 <__m_debug_client_scanner__refresh>, "
        "m_next_client = 0x555555557200 <__m_debug_client_scanner__next_client>, "
        "m_next_game_action__inbound = 0x555555557300 "
        "<__m_debug_client_scanner__next_game_action_inbound>, "
        "m_next_game_action__outbound = 0x555555557400 "
        "<__m_debug_client_scanner__next_game_action_outbound>, "
        "quantity_of__clients = 1, "
        "game_actions = {quantity_of__game_actions__inbound = 0, "
        "game_action_header__inbound__current = {_serialiation_header = "
        "{size_of__struct = 0, uuid = 4294967295}, "
        "the_kind_of_game_action__this_action_is = Game_Action_Kind__None}, "
        "game_action_logic_entry__inbound__current = {m_process = 0x0, "
        "m_process_kind = Process_Kind__None}, "
        "quantity_of__game_actions__outbound = %d, "
        "game_action_header__outbound__current = {_serialiation_header = "
        "{size_of__struct = 40, uuid = %d}, "
        "the_kind_of_game_action__this_action_is = %s}, "
        "game_action_logic_entry__outbound__current = {m_process = 0x555555559000 "
        "<m_process__store>, m_process_kind = Process_Kind__Timed}}, "
        "uuid_of__client__current = %d, "
        "current_client__local_space__center__3i32 = {x__i32 = %d, y__i32 = %d, "
        "z__i32 = %d}, "
        "current_client__client_flags__u16 = %d '\\%03o'}"
    ) % (outbound_count, uuid, kind, client_uuid,
         center[0], center[1], center[2], flags, flags)


def _client_scanner_gdb(struct_text, stack):
    """A GDBSession whose write() serves the dispatch capture's GDB I/O:
    -stack-list-frames -> *stack*, and the client-scanner set/eval -> *struct_text*."""
    def write(command, *a, **kw):
        if command == "-stack-list-frames":
            return _result_done({"stack": stack})
        if command.startswith("-interpreter-exec"):
            return _result_done({})
        if command == "-data-evaluate-expression $debug_client_scanner":
            return _result_done({"value": struct_text})
        return _result_done({})
    return _make_gdb(write)


class TestCaptureGameActionDispatch(unittest.TestCase):
    """Test _capture_game_action_dispatch (the GDB-I/O capture at the hit)."""

    def setUp(self):
        L.reset_ga_dispatch_deep_trace_state()

    def tearDown(self):
        L.reset_ga_dispatch_deep_trace_state()

    def test_capture_reads_stack_ptrs_and_client_snapshot(self):
        stack = [
            {"func": "dispatch_game_action_for__client", "file": "client.c", "line": "315"},
            {"func": "send_outbound_game_action", "file": "game.c", "line": "575"},
            {"func": "run_game", "file": "game.c", "line": "716"},
            {"func": "main", "file": "main.c", "line": "10"},
        ]
        gdb = _client_scanner_gdb(_client_scanner_struct(), stack)
        responses = _bp_hit(args=[
            {"name": "p_client", "value": "0x5555556e3a00"},
            {"name": "p_game", "value": "0x5555556e3000"},
            {"name": "p_tcp_socket_manager", "value": "0x5555556e3b00"},
            {"name": "p_game_action", "value": "0x5555556e4100"},
            {"name": "p_ptr_OUT_process", "value": "0x7fffffff00"},
        ])
        ev = L._capture_game_action_dispatch(gdb, responses)
        self.assertEqual(ev["event"], "dispatch")
        self.assertEqual(ev["game_action_ptr"], "0x5555556e4100")
        self.assertEqual(ev["client_ptr"], "0x5555556e3a00")
        self.assertEqual(len(ev["stack"]), 4)
        self.assertIn("dispatch_game_action_for__client", ev["stack"][0])
        self.assertIn("main", ev["stack"][3])
        # The client-scanner snapshot parsed the current action + client state.
        client = ev["client"]
        self.assertIsNotNone(client)
        self.assertEqual(client["ga_outbound_kind"],
                         "Game_Action_Kind__Global_Space__Store")
        self.assertEqual(client["ga_outbound_uuid"], "0xd6a36011")
        self.assertEqual(client["uuid"], "0x20000000")
        self.assertEqual(client["flags"], "2")
        self.assertEqual(client["center"], {"x": 0, "y": 63, "z": 2})
        self.assertEqual(client["ga_outbound_count"], 5)

    def test_capture_no_frame_args_reads_ptrs_as_none(self):
        gdb = _client_scanner_gdb(_client_scanner_struct(),
                                  [{"func": "main", "file": "main.c", "line": "10"}])
        ev = L._capture_game_action_dispatch(gdb, _bp_hit())  # no frame args
        self.assertIsNone(ev["game_action_ptr"])
        self.assertIsNone(ev["client_ptr"])
        self.assertIsNotNone(ev["client"])  # the client scanner still works

    def test_capture_client_scanner_unavailable(self):
        """A release build (no debug symbols) yields no scanner struct; the
        capture degrades the client snapshot to None but keeps the backtrace."""
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": [
                    {"func": "dispatch_game_action_for__client", "file": "client.c",
                     "line": "315"}]})
            return []  # the scanner eval yields nothing
        gdb = _make_gdb(write)
        ev = L._capture_game_action_dispatch(gdb, _bp_hit())
        self.assertEqual(len(ev["stack"]), 1)
        self.assertIsNone(ev["client"])

    def test_capture_never_raises_on_gdb_failure(self):
        def write(command, *a, **kw):
            raise RuntimeError("gdb gone")
        gdb = _make_gdb(write)
        ev = L._capture_game_action_dispatch(gdb, _bp_hit())
        # Degrades gracefully: event is still returned with empty fields.
        self.assertEqual(ev["event"], "dispatch")
        self.assertEqual(ev["stack"], [])
        self.assertIsNone(ev["client"])


class TestResolveGameActionDispatchTrace(unittest.TestCase):
    """Test resolve_game_action_dispatch_trace (the safe-point drain + log)."""

    def setUp(self):
        L.reset_ga_dispatch_deep_trace_state()

    def tearDown(self):
        L.reset_ga_dispatch_deep_trace_state()

    def _dispatch_event(self, ptr="0x1", client=None, stack=None):
        return {"event": "dispatch", "ts": 1.0, "game_action_ptr": ptr,
                "client_ptr": "0x2", "client": client,
                "stack": stack or ["#0 dispatch at client.c:315"]}

    def test_no_hook_returns_zero(self):
        L._ga_dispatch_deep_trace_state["hook"] = None
        count = L.resolve_game_action_dispatch_trace(MagicMock(), MagicMock())
        self.assertEqual(count, 0)

    def test_drains_and_logs_events(self):
        hook = BreakpointHook.__new__(BreakpointHook)
        hook.captured_events = [
            self._dispatch_event("0x1"),
            self._dispatch_event("0x2"),
        ]
        L._ga_dispatch_deep_trace_state["hook"] = hook

        config = MagicMock()
        config.log_file = None  # None -> stdout
        with patch("builtins.print") as mock_print:
            count = L.resolve_game_action_dispatch_trace(MagicMock(), config)
        self.assertEqual(count, 2)
        printed = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertIn("dispatch ptr=0x1", printed)
        self.assertIn("dispatch ptr=0x2", printed)
        self.assertIn("[game-action-trace]", printed)
        # Events are drained.
        self.assertEqual(hook.captured_events, [])

    def test_logs_to_file_when_configured(self):
        hook = BreakpointHook.__new__(BreakpointHook)
        hook.captured_events = [self._dispatch_event("0x9")]
        L._ga_dispatch_deep_trace_state["hook"] = hook

        tmpdir = tempfile.mkdtemp()
        config = MagicMock()
        config.log_file = tmpdir  # a directory -> tmpdir/game_action_trace.log
        count = L.resolve_game_action_dispatch_trace(MagicMock(), config)
        self.assertEqual(count, 1)
        log_path = os.path.join(tmpdir, "game_action_trace.log")
        self.assertTrue(os.path.isfile(log_path))
        with open(log_path) as f:
            content = f.read()
        self.assertIn("dispatch ptr=0x9", content)
        self.assertIn("[game-action-trace]", content)

    def test_writes_structured_record_to_main_jsonl(self):
        """The PRIMARY trace (structured) goes to the session JSONL via
        GDBSession.log_record — the same file as the GDB-response records."""
        client = {"uuid": "0x20000000", "flags": "2",
                  "center": {"x": 0, "y": 63, "z": 2}, "client_count": 1,
                  "ga_inbound_count": 0, "ga_outbound_count": 5,
                  "ga_inbound_kind": None, "ga_outbound_kind":
                  "Game_Action_Kind__Global_Space__Store",
                  "ga_inbound_uuid": None, "ga_outbound_uuid": "0xd6b00001"}
        hook = BreakpointHook.__new__(BreakpointHook)
        hook.captured_events = [self._dispatch_event("0x77", client=client)]
        L._ga_dispatch_deep_trace_state["hook"] = hook

        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession(log_file=log_file)
            config = MagicMock()
            config.log_file = tmpdir
            count = L.resolve_game_action_dispatch_trace(gdb, config)
        self.assertEqual(count, 1)
        with open(log_file) as f:
            recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        ga = [r for r in recs if r.get("type") == "game-action-trace"]
        self.assertEqual(len(ga), 1)
        self.assertEqual(ga[0]["event"], "dispatch")
        self.assertEqual(ga[0]["game_action_ptr"], "0x77")
        self.assertEqual(ga[0]["client"]["ga_outbound_kind"],
                         "Game_Action_Kind__Global_Space__Store")
        self.assertEqual(ga[0]["client"]["center"], {"x": 0, "y": 63, "z": 2})
        gdb.close()


class TestGaDispatchDeepTraceState(unittest.TestCase):
    """Test the deep dispatch-trace state reset + enable/toggle helpers."""

    def test_reset_ga_dispatch_deep_trace_state(self):
        L._ga_dispatch_deep_trace_state["hook"] = object()
        L._ga_dispatch_deep_trace_state["enabled"] = True
        L.reset_ga_dispatch_deep_trace_state()
        self.assertIsNone(L._ga_dispatch_deep_trace_state["hook"])
        self.assertFalse(L._ga_dispatch_deep_trace_state["enabled"])

    def test_reset_trace_state_resets_deep_trace(self):
        L._ga_dispatch_deep_trace_state["hook"] = object()
        L._ga_dispatch_deep_trace_state["enabled"] = True
        L.reset_trace_state()
        self.assertIsNone(L._ga_dispatch_deep_trace_state["hook"])
        self.assertFalse(L._ga_dispatch_deep_trace_state["enabled"])

    def test_set_and_toggle_enabled(self):
        L.reset_ga_dispatch_deep_trace_state()
        self.assertFalse(L._ga_dispatch_deep_trace_state["enabled"])
        # Toggle before registration flips the stored flag.
        self.assertTrue(L.toggle_ga_dispatch_deep_trace(MagicMock()))
        self.assertTrue(L._ga_dispatch_deep_trace_state["enabled"])
        self.assertFalse(L.toggle_ga_dispatch_deep_trace(MagicMock()))
        self.assertFalse(L._ga_dispatch_deep_trace_state["enabled"])
        # set_..._enabled is explicit.
        L.set_ga_dispatch_deep_trace_enabled(MagicMock(), True)
        self.assertTrue(L._ga_dispatch_deep_trace_state["enabled"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
