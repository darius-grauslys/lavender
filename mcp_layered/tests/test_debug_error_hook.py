"""Tests for the non-fatal debug_error BreakpointHook (error reporting).

Since -DCRASH_ON_ERROR was dropped from the build, debug_error() no longer
aborts: the game prints the error and keeps running, so the step driver
never sees a crash signal. The debug_error BreakpointHook captures the same
report the old SIGABRT crash path produced (backtrace with the debug_error
caller highlighted + arguments, via debug_error.build_error_report) and the
step driver surfaces it in the step response.

Also covered here:
  - the MI negative-capability cache (debug_error.format_arguments_for_frame
    never retries an MI command that errored "Undefined MI command" — the
    historical ~2.5s-per-error stall + gdb_error log spam);
  - burst suppression in _capture_debug_error_event (only the first N
    occurrences per signature get a full capture; repeats cost zero GDB I/O
    and drain as one aggregated record);
  - GDBSession._log_error_response dedupe (first GDB_ERROR_LOG_LIMIT
    occurrences per (command, error) are logged; repeats summarized at
    close()).

Run from repo root: python3 -m unittest mcp_layered.tests.test_debug_error_hook -v
Or:                 python3 mcp_layered/tests/test_debug_error_hook.py

The capture (GDB I/O) is exercised against a mocked GDBSession; no live GDB
is required.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LAYERED_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _LAYERED_ROOT)

from mcp_layered.debug_response import parse
from mcp_layered.debug_error import build_error_report
from mcp_layered.layer_pygdbmi import GDBSession, BreakpointHook
import mcp_layered.layer_lav_init as L


def _result_done(payload):
    """A raw (pygdbmi-format) ^done record — what a mocked GdbController.write
    returns. GDBSession.write() runs parse() over it."""
    return [{"type": "result", "message": "done", "payload": payload}]


def _result_error(msg):
    return [{"type": "result", "message": "error",
             "payload": {"msg": msg}}]


def _bp_hit(func="debug_error", bkpt="5", args=None):
    return parse([{
        "type": "notify", "message": "stopped",
        "payload": {"reason": "breakpoint-hit", "bkptno": bkpt,
                    "frame": {"func": func, "file": "e.c", "line": "64",
                              "args": args or []}},
    }])


def _make_gdb(write_side_effect, get_response=None):
    """A GDBSession over a mock controller whose write() uses the given
    side_effect (command -> response list). ``get_response`` sets what
    get_gdb_response() returns (used by the info-args console fallback)."""
    with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
        mock_gdb = MagicMock()
        mock_gdb.write.side_effect = write_side_effect
        if get_response is not None:
            mock_gdb.get_gdb_response.return_value = get_response
        mock_cls.return_value = mock_gdb
        return GDBSession()


# The real-world shape of the error this hook exists for (from the
# /tmp/lav-log world-load crash): debug_error called from
# poll_for_collision_node_update.
_WORLD_LOAD_STACK = [
    {"func": "debug_error", "file": "core/source/debug/debug.c", "line": "64"},
    {"func": "poll_for_collision_node_update", "file": "core/source/world/world.c",
     "line": "383"},
    {"func": "m_process__game_action__hitbox",
     "file": "core/source/game_action/core/hitbox/game_action__hitbox.c",
     "line": "103"},
    {"func": "poll_process_manager", "file": "core/source/process/process_manager.c",
     "line": "185"},
    {"func": "manage_game__post_render", "file": "core/source/game.c", "line": "748"},
    {"func": "run_game", "file": "core/source/game.c", "line": "716"},
    {"func": "main", "file": "core/source/main.c", "line": "10"},
]

_INFO_ARGS_CONSOLE = (
    "All locals:\n"
    "  p_game = 0x5555556e2d50 <game>\n"
    "  position_old__3i32F4 = <optimized out>\n"
    "  position_new__3i32F4 = <optimized out>\n"
    "  uuid_u32_of__entry = 536870912\n"
)


class TestBuildErrorReport(unittest.TestCase):
    """Tests for debug_error.build_error_report (the shared report builder)."""

    def _frames(self):
        return [
            {'level': '#0', 'func': 'debug_error',
             'location': 'core/source/debug/debug.c:64',
             'line': '64', 'addr': ''},
            {'level': '#1', 'func': 'poll_for_collision_node_update',
             'location': 'core/source/world/world.c:383',
             'line': '383', 'addr': ''},
            {'level': '#2', 'func': 'm_process__game_action__hitbox',
             'location': 'core/source/game_action/core/hitbox/game_action__hitbox.c:103',
             'line': '103', 'addr': ''},
        ]

    def test_debug_error_caller_highlighted(self):
        report = build_error_report(self._frames(), gdb=None)
        lines = report.split("\n")
        # Non-highlighted frames use the "   " (marker + separator) prefix,
        # exactly as the old _get_signal_info output in the crash logs.
        self.assertIn(">> #1 poll_for_collision_node_update at "
                      "core/source/world/world.c:383", lines)
        self.assertIn("   #0 debug_error at core/source/debug/debug.c:64", lines)

    def test_no_debug_error_in_stack_highlights_frame0(self):
        frames = [
            {'level': '#0', 'func': 'abort', 'location': 'stdlib/abort.c:73',
             'line': '73', 'addr': ''},
            {'level': '#1', 'func': 'raise', 'location': 'sysdeps/posix/raise.c:26',
             'line': '26', 'addr': ''},
        ]
        report = build_error_report(frames, gdb=None)
        lines = report.split("\n")
        self.assertIn(">> #0 abort at stdlib/abort.c:73", lines)
        self.assertIn("   #1 raise at sysdeps/posix/raise.c:26", lines)

    def test_empty_frames_returns_empty(self):
        self.assertEqual(build_error_report([], gdb=None), "")

    def test_no_gdb_skips_arguments(self):
        report = build_error_report(self._frames(), gdb=None)
        self.assertNotIn("Arguments:", report)

    def test_with_gdb_appends_arguments(self):
        """Arguments come from the info-args console fallback (the real GDB
        errors on -stack-info-arguments, as seen in the live logs)."""
        def write(command, *a, **kw):
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            if command == "-stack-select-frame 1":
                return _result_done({"frame": {"func": "poll_for_collision_node_update"}})
            return _result_done({})
        gdb = _make_gdb(
            write,
            get_response=[{"type": "console", "payload": _INFO_ARGS_CONSOLE}])
        try:
            report = build_error_report(self._frames(), gdb)
            self.assertIn("Arguments:", report)
            self.assertIn("uuid_u32_of__entry = 536870912", report)
        finally:
            gdb.close()

    def test_mi_cache_skips_after_first_failure(self):
        """Once -stack-info-arguments has failed for a session, it is never
        sent again and the slow console fallback is skipped — this is what
        stops the ~2.5s-per-error stall + gdb_error log spam in bursty
        error storms."""
        calls = []
        def write(command, *a, **kw):
            calls.append(command)
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            return _result_done({})
        gdb = _make_gdb(
            write,
            get_response=[{"type": "console", "payload": _INFO_ARGS_CONSOLE}])
        try:
            # First call: the probe fails, the console fallback runs.
            report1 = build_error_report(self._frames(), gdb)
            self.assertIn("Arguments:", report1)
            self.assertIn("uuid_u32_of__entry = 536870912", report1)
            self.assertTrue(any(c.startswith("-stack-info-arguments") for c in calls))
            # Second call: cached miss — no -stack-info-arguments, no frame
            # select, no console exec; the section degrades gracefully.
            calls.clear()
            report2 = build_error_report(self._frames(), gdb)
            self.assertIn(">> #1", report2)
            self.assertIn("(no argument info available)", report2)
            self.assertFalse(any(c.startswith("-stack-info-arguments") for c in calls))
            self.assertFalse(any(c == "-stack-select-frame 1" for c in calls))
            self.assertFalse(any("interpreter-exec" in c for c in calls))
        finally:
            gdb.close()


class TestRawStackFrameToDebugErrorFrame(unittest.TestCase):
    """Tests for the raw -stack-list-frames -> debug_error.py frame conversion."""

    def test_file_and_line(self):
        f = L.raw_stack_frame_to_debug_error_frame(
            3, {"func": "main", "file": "a.c", "line": "10", "pc": "0x1000"})
        self.assertEqual(f["level"], "#3")
        self.assertEqual(f["func"], "main")
        self.assertEqual(f["location"], "a.c:10")
        self.assertEqual(f["line"], "10")
        self.assertEqual(f["addr"], "0x1000")

    def test_file_only(self):
        f = L.raw_stack_frame_to_debug_error_frame(
            0, {"func": "main", "file": "a.c", "line": "", "pc": ""})
        self.assertEqual(f["location"], "a.c")

    def test_addr_only(self):
        f = L.raw_stack_frame_to_debug_error_frame(
            0, {"func": "???", "file": "", "line": "", "pc": "0x7f00"})
        self.assertEqual(f["location"], "0x7f00")

    def test_nothing(self):
        f = L.raw_stack_frame_to_debug_error_frame(
            0, {"func": "???", "file": "", "line": "", "pc": ""})
        self.assertEqual(f["location"], "???")


class TestCaptureDebugErrorEvent(unittest.TestCase):
    """Tests for _capture_debug_error_event (the GDB-I/O capture at the hit)."""

    def setUp(self):
        # Isolate the module-level burst-suppression signature state.
        L.reset_debug_error_report_state()

    def tearDown(self):
        L.reset_debug_error_report_state()

    def test_capture_builds_report_like_sigabrt(self):
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": _WORLD_LOAD_STACK})
            if command.startswith("-stack-info-arguments"):
                # Real GDB: not an MI command in this build -> fallback path.
                return _result_error("Undefined MI command: stack-info-arguments")
            if command == "-stack-select-frame 1":
                return _result_done(
                    {"frame": {"func": "poll_for_collision_node_update"}})
            return _result_done({})
        gdb = _make_gdb(
            write,
            get_response=[{"type": "console", "payload": _INFO_ARGS_CONSOLE}])
        try:
            ev = L._capture_debug_error_event(gdb, _bp_hit())
            self.assertIsNotNone(ev)
            self.assertEqual(ev["event"], "debug_error")
            # The error ORIGINATED in the debug_error caller (frame 1).
            self.assertEqual(ev["func"], "poll_for_collision_node_update")
            self.assertEqual(ev["file"], "core/source/world/world.c")
            self.assertEqual(ev["line"], "383")
            # The report mirrors the SIGABRT crash report shape.
            report = ev["report"]
            self.assertIn(">> #1 poll_for_collision_node_update at "
                          "core/source/world/world.c:383", report)
            self.assertIn("   #0 debug_error at core/source/debug/debug.c:64", report)
            self.assertIn("Arguments:", report)
            # The arguments include the msg_fmt-style values GDB can recover —
            # here the entry uuid from the real crash.
            self.assertIn("uuid_u32_of__entry = 536870912", report)
            # Full callee stack is recorded for the JSONL record.
            self.assertEqual(len(ev["stack"]), len(_WORLD_LOAD_STACK))
            self.assertIn("manage_game__post_render", ev["stack"][4])
        finally:
            gdb.close()

    def test_capture_extracts_msg_fmt_from_stop_frame(self):
        """The actual error message (debug_error's msg_fmt arg) is read from
        the stop frame's args — zero round-trips — and prepended to the
        report. This is the text the game printed to its stdout."""
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": _WORLD_LOAD_STACK})
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            if command == "-stack-select-frame 1":
                return _result_done(
                    {"frame": {"func": "poll_for_collision_node_update"}})
            return _result_done({})
        gdb = _make_gdb(write)
        try:
            ev = L._capture_debug_error_event(gdb, _bp_hit(args=[
                {"name": "msg_fmt",
                 "value": '"poll_for_collision_node_update, '
                          'p_global_space__new == 0."'},
            ]))
            self.assertEqual(
                ev["message"],
                '"poll_for_collision_node_update, p_global_space__new == 0."')
            self.assertTrue(ev["report"].startswith("Error message: "))
            self.assertIn("p_global_space__new == 0.", ev["report"])
        finally:
            gdb.close()

    def test_capture_no_frames_returns_none(self):
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": []})
            return _result_done({})
        gdb = _make_gdb(write)
        try:
            self.assertIsNone(L._capture_debug_error_event(gdb, _bp_hit()))
        finally:
            gdb.close()

    def test_capture_never_raises_on_gdb_failure(self):
        def write(command, *a, **kw):
            raise RuntimeError("gdb gone")
        gdb = _make_gdb(write)
        try:
            # No report could be built -> the event is dropped (None), never
            # an exception out of the capture.
            self.assertIsNone(L._capture_debug_error_event(gdb, _bp_hit()))
        finally:
            gdb.close()

    def test_repeats_suppressed_after_full_captures(self):
        """Burst suppression, end to end: after
        full_captures_per_signature full captures of the same signature,
        further hits do NO GDB I/O (not even the stack read), and the drain
        surfaces the repeats as ONE aggregated record (per drain)."""
        limit = L._debug_error_report_state["full_captures_per_signature"]
        calls = []
        def write(command, *a, **kw):
            calls.append(command)
            if command == "-stack-list-frames":
                return _result_done({"stack": _WORLD_LOAD_STACK})
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            return _result_done({})
        gdb = _make_gdb(write)
        try:
            hook = BreakpointHook(gdb, "debug_error", "debug_error",
                                  capture=L._capture_debug_error_event)
            L._debug_error_report_state["hook"] = hook
            hook.enable = lambda: True  # skip the real bp insertion
            hook._enabled = True
            gdb.add_hook(hook._make_hook())
            args = [{"name": "msg_fmt",
                     "value": '"allocate_process_in__process_manager, '
                              'failed to allocate."'}]
            gdb._in_nested_read = False
            raw = [{
                "type": "notify", "message": "stopped",
                "payload": {"reason": "breakpoint-hit", "bkptno": "11",
                            "frame": {"func": "debug_error",
                                      "file": "core/source/debug/debug.c",
                                      "line": "64",
                                      "args": args}},
            }]
            # The first `limit` hits: full captures (stack reads happen).
            for _ in range(limit):
                gdb.process_hooks_on_raw(raw)
            self.assertEqual(len(hook.captured_events), limit)
            stack_reads = sum(1 for c in calls if c == "-stack-list-frames")
            self.assertEqual(stack_reads, limit)
            # Two more hits of the SAME signature: suppressed — no new
            # events, no GDB I/O at all.
            gdb.process_hooks_on_raw(raw)
            gdb.process_hooks_on_raw(raw)
            self.assertEqual(len(hook.captured_events), limit)
            stack_reads = sum(1 for c in calls if c == "-stack-list-frames")
            self.assertEqual(stack_reads, limit)  # unchanged

            sigs = L._debug_error_report_state["signatures"]
            self.assertEqual(len(sigs), 1)
            st = next(iter(sigs.values()))
            self.assertEqual(st["seen"], limit + 2)
            self.assertEqual(st["full"], limit)
            self.assertEqual(st["suppressed"], 2)

            # The drain surfaces the repeats as one aggregated record.
            events = L.resolve_debug_error_events(gdb, MagicMock())
            agg = [e for e in events if e.get("aggregated")]
            self.assertEqual(len(agg), 1)
            self.assertIn("2 repeat(s)", agg[0]["report"])
            # A second drain with no new repeats surfaces nothing new.
            events2 = L.resolve_debug_error_events(gdb, MagicMock())
            self.assertEqual(
                [e for e in events2 if e.get("aggregated")], [])
        finally:
            gdb.close()

    def test_distinct_signatures_each_get_full_captures(self):
        """Suppression is per signature: two different errors each get the
        full capture (they do not share the quota)."""
        limit = L._debug_error_report_state["full_captures_per_signature"]
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": _WORLD_LOAD_STACK})
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            return _result_done({})
        gdb = _make_gdb(write)
        try:
            for value in ('"error A, detail."', '"error B, detail."'):
                ev = L._capture_debug_error_event(gdb, _bp_hit(args=[
                    {"name": "msg_fmt", "value": value}]))
                self.assertIsNotNone(ev)
                self.assertEqual(ev["message"], value)
            sigs = L._debug_error_report_state["signatures"]
            self.assertEqual(len(sigs), 2)
            for st in sigs.values():
                self.assertEqual(st["full"], 1)
                self.assertEqual(st["suppressed"], 0)
        finally:
            gdb.close()


class TestResolveDebugErrorEvents(unittest.TestCase):
    """Tests for resolve_debug_error_events (the safe-point drain + log)."""

    def _hook_with_events(self, events):
        hook = BreakpointHook.__new__(BreakpointHook)
        hook.captured_events = list(events)
        return hook

    def test_drains_and_logs_jsonl(self):
        ev = {"event": "debug_error", "ts": 1.0,
              "func": "poll_for_collision_node_update",
              "file": "core/source/world/world.c", "line": "383",
              "message": '"poll_for_collision_node_update, p_global_space__new == 0."',
              "stack": ["#1 poll_for_collision_node_update at world.c:383"],
              "report": ">> #1 poll_for_collision_node_update at world.c:383"}
        L._debug_error_report_state["hook"] = self._hook_with_events([ev])

        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession(log_file=log_file)
            try:
                events = L.resolve_debug_error_events(gdb, MagicMock())
            finally:
                gdb.close()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["func"], "poll_for_collision_node_update")
        # Drained from the hook.
        self.assertEqual(L._debug_error_report_state["hook"].captured_events, [])
        # Structured "debug-error" record in the session JSONL.
        with open(log_file) as f:
            recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        de = [r for r in recs if r.get("type") == "debug-error"]
        self.assertEqual(len(de), 1)
        self.assertEqual(de[0]["func"], "poll_for_collision_node_update")
        self.assertEqual(de[0]["line"], "383")
        self.assertIn(">> #1", de[0]["report"])

    def test_no_hook_returns_empty(self):
        L._debug_error_report_state["hook"] = None
        self.assertEqual(L.resolve_debug_error_events(MagicMock()), [])


class TestFormatDebugErrorEvents(unittest.TestCase):
    """Tests for format_debug_error_events (step-response section)."""

    def test_empty_returns_empty(self):
        self.assertEqual(L.format_debug_error_events([], 10), "")

    def test_nonfatal_header_and_step_labeling(self):
        evs = [
            {"step": 20, "report": ">> #1 f at a.c:1\nArguments:\n  x = 1"},
            {"step": 21, "report": ">> #2 g at b.c:2"},
        ]
        out = L.format_debug_error_events(evs, 102)
        self.assertIn("2 non-fatal debug_error(s) occurred during this step", out)
        self.assertIn("the game kept running", out)
        self.assertIn("ERROR: debug_error on step 20/102.", out)
        self.assertIn("ERROR: debug_error on step 21/102.", out)
        self.assertIn(">> #1 f at a.c:1", out)

    def test_fatal_header(self):
        evs = [{"step": 3, "report": ">> #1 f at a.c:1"}]
        out = L.format_debug_error_events(evs, 10, fatal=True)
        self.assertIn("occurred before the crash", out)
        self.assertNotIn("kept running", out)

    def test_reports_capped_at_five(self):
        evs = [{"step": i, "report": f"report {i}"} for i in range(7)]
        out = L.format_debug_error_events(evs, 100)
        for i in range(5):
            self.assertIn(f"report {i}", out)
        self.assertNotIn("report 5", out)
        self.assertNotIn("report 6", out)
        self.assertIn("2 more", out)


class TestRegistrationAndWiring(unittest.TestCase):
    """Tests for the hook registration in _register_breakpoint_hooks_for_gdb."""

    def setUp(self):
        L.reset_trace_state()

    def tearDown(self):
        L.reset_trace_state()

    def test_register_creates_and_enables_debug_error_hook(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_gdb = MagicMock()
            mock_gdb.write.return_value = [
                {"type": "result", "message": "done",
                 "payload": {"bkpt": {"number": "11"}}}]
            mock_cls.return_value = mock_gdb
            gdb = GDBSession()
            try:
                L._register_breakpoint_hooks_for_gdb(gdb)
                hook = L._debug_error_report_state["hook"]
                self.assertIsInstance(hook, BreakpointHook)
                self.assertEqual(hook.name, "debug_error")
                self.assertEqual(hook.target, "debug_error")
                self.assertTrue(hook.enabled)
                self.assertEqual(hook.bp_number, "11")
            finally:
                gdb.close()

    def test_reset_debug_error_report_state(self):
        L._debug_error_report_state["hook"] = object()
        L._debug_error_report_state["enabled"] = False
        L.reset_debug_error_report_state()
        self.assertIsNone(L._debug_error_report_state["hook"])
        self.assertTrue(L._debug_error_report_state["enabled"])

    def test_hook_capture_fires_on_debug_error_hit(self):
        """End-to-end through the BreakpointHook machinery: a breakpoint-hit
        stop at debug_error (read via process_hooks_on_raw, a safe context)
        runs the capture (mocked GDB I/O) and buffers the event for
        consume_events()."""
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": _WORLD_LOAD_STACK})
            if command.startswith("-stack-info-arguments"):
                return _result_error("Undefined MI command: stack-info-arguments")
            if command == "-stack-select-frame 1":
                return _result_done(
                    {"frame": {"func": "poll_for_collision_node_update"}})
            return _result_done({})
        gdb = _make_gdb(
            write,
            get_response=[{"type": "console", "payload": _INFO_ARGS_CONSOLE}])
        L.reset_debug_error_report_state()
        try:
            hook = BreakpointHook(gdb, "debug_error", "debug_error",
                                  capture=L._capture_debug_error_event)
            hook.enable = lambda: True  # skip the real bp insertion
            hook._enabled = True
            gdb.add_hook(hook._make_hook())

            # A stop at debug_error, processed from a safe (non-nested) context.
            gdb._in_nested_read = False
            raw = [{
                "type": "notify", "message": "stopped",
                "payload": {"reason": "breakpoint-hit", "bkptno": "11",
                            "frame": {"func": "debug_error",
                                      "file": "core/source/debug/debug.c",
                                      "line": "64"}},
            }]
            gdb.process_hooks_on_raw(raw)

            self.assertEqual(len(hook.captured_events), 1)
            ev = hook.consume_events()[0]
            self.assertEqual(ev["func"], "poll_for_collision_node_update")
            self.assertIn(">> #1 poll_for_collision_node_update", ev["report"])
            # Drained.
            self.assertEqual(hook.consume_events(), [])
        finally:
            gdb.close()

    def test_hook_ignores_other_function_hits(self):
        """A breakpoint hit in some other function must not run the capture."""
        def write(command, *a, **kw):
            raise AssertionError("no GDB I/O expected for a non-matching hit")
        gdb = _make_gdb(write)
        L.reset_debug_error_report_state()
        try:
            hook = BreakpointHook(gdb, "debug_error", "debug_error",
                                  capture=L._capture_debug_error_event)
            hook.enable = lambda: True
            hook._enabled = True
            gdb.add_hook(hook._make_hook())

            gdb._in_nested_read = False
            raw = [{
                "type": "notify", "message": "stopped",
                "payload": {"reason": "breakpoint-hit", "bkptno": "11",
                            "frame": {"func": "some_other_func",
                                      "file": "x.c", "line": "5"}},
            }]
            gdb.process_hooks_on_raw(raw)
            self.assertEqual(hook.captured_events, [])
        finally:
            gdb.close()


class TestSessionStatusSurfacesDebugErrors(unittest.TestCase):
    """The session_status driver surfaces PENDING (not yet drained)
    debug_error events as one-line summaries (the full report of each is
    in the session JSONL log)."""

    def setUp(self):
        L.reset_trace_state()
        L.reset_scene_state()
        self._p_scene = patch.object(L, "resolve_pending_scene_transitions")
        self._p_pt = patch.object(L, "resolve_process_trace")
        self._p_scene.start()
        self._p_pt.start()
        L._register_builtin_drivers()
        L.reset_session_state()
        L._SESSION_STATE.running = True
        L._SESSION_STATE.halted = True
        L._SESSION_STATE.crashed = False
        L._SESSION_STATE.backtrace = "#0 main at main.c:10"

    def tearDown(self):
        self._p_scene.stop()
        self._p_pt.stop()
        L.reset_trace_state()
        L.reset_scene_state()
        L.reset_session_state()

    def test_status_shows_pending_debug_error_summary(self):
        from mcp_layered.layer_lav_config import LavConfig
        from mcp_layered.layer_lav_cmd import get_driver

        hook = BreakpointHook.__new__(BreakpointHook)
        hook.captured_events = [{
            "event": "debug_error", "ts": 1.0,
            "func": "poll_for_collision_node_update",
            "file": "core/source/world/world.c", "line": "383",
            "message": '"poll_for_collision_node_update, '
                       'p_global_space__new == 0."',
            "stack": ["#1 poll_for_collision_node_update at world.c:383"],
            "report": ">> #1 poll_for_collision_node_update at world.c:383",
        }]
        L._debug_error_report_state["hook"] = hook

        gdb = MagicMock()
        gdb.is_closed = False
        result = get_driver("session_status")(gdb, LavConfig(), {})

        self.assertIn("debug_error events since last status: 1", result)
        self.assertIn(
            "ERROR: debug_error in poll_for_collision_node_update "
            "at core/source/world/world.c:383", result)
        # Drained.
        self.assertEqual(hook.captured_events, [])

    def test_status_clean_when_nothing_pending(self):
        from mcp_layered.layer_lav_config import LavConfig
        from mcp_layered.layer_lav_cmd import get_driver

        L._debug_error_report_state["hook"] = None
        gdb = MagicMock()
        gdb.is_closed = False
        result = get_driver("session_status")(gdb, LavConfig(), {})
        self.assertIn("Game is HALTED", result)
        self.assertNotIn("debug_error events", result)


class TestStepDriverSurfacesDebugErrors(unittest.TestCase):
    """Integration: the step driver drains captured debug_error events at its
    safe point and surfaces them in the step response (SIGABRT-shaped)."""

    def setUp(self):
        L.reset_trace_state()
        L.reset_scene_state()
        # The step_driver closure captures step_frame_detailed / detect_signal
        # at registration time — patch before _register_builtin_drivers.
        self._p_step = patch("mcp.gdb_nav_utils.step_frame_detailed")
        self._p_detect = patch("mcp_layered.layer_pygdbmi.detect_signal")
        mock_step = self._p_step.start()
        mock_detect = self._p_detect.start()
        self._mock_step = mock_step
        self._mock_detect = mock_detect
        mock_detect.return_value = None
        # The safe-point resolvers that do real GDB I/O are no-ops here.
        self._p_scene = patch.object(L, "resolve_pending_scene_transitions")
        self._p_proctrace = patch.object(L, "resolve_process_trace")
        self._p_scene.start()
        self._p_proctrace.start()
        # Patch object so that the driver's closure can access the patched functions
        # since they are module-level names.
        self._p_format = patch.object(L, "format_scene_transitions", return_value="")
        self._p_format.start()
        L._register_builtin_drivers()

    def tearDown(self):
        self._p_step.stop()
        self._p_detect.stop()
        self._p_scene.stop()
        self._p_proctrace.stop()
        self._p_format.stop()
        L.reset_trace_state()
        L.reset_scene_state()

    def _write(self, command, *a, **kw):
        if command in ("-gdb-set pagination off", "-gdb-set confirm off"):
            return _result_done({})
        if command == "-exec-finish":
            return []  # no signal in the finish responses
        return _result_done({})

    def _gdb(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_gdb = MagicMock()
            mock_gdb.write.side_effect = self._write
            mock_gdb.is_closed = False
            mock_cls.return_value = mock_gdb
            return GDBSession()

    def test_step_surfaces_captured_debug_errors(self):
        from mcp_layered.layer_lav_config import LavConfig
        from mcp_layered.layer_lav_cmd import get_driver

        gdb = self._gdb()
        try:
            # Two successful frames; a debug_error event was captured (at its
            # transient stop) during frame 1 and sits in the hook's queue.
            self._mock_step.side_effect = [(True, None), (True, None)]
            hook = BreakpointHook.__new__(BreakpointHook)
            hook.captured_events = [{
                "event": "debug_error", "ts": 1.0,
                "func": "poll_for_collision_node_update",
                "file": "core/source/world/world.c", "line": "383",
                "stack": ["#1 poll_for_collision_node_update at world.c:383"],
                "report": (">> #1 poll_for_collision_node_update at "
                           "core/source/world/world.c:383\nArguments:\n"
                           "  uuid_u32_of__entry = 536870912"),
            }]
            L._debug_error_report_state["hook"] = hook

            result = get_driver("step")(gdb, LavConfig(), {"count": 2})

            self.assertIn("Stepped 2 game frame(s) to post-render.", result)
            self.assertIn(
                "1 non-fatal debug_error(s) occurred during this step", result)
            self.assertIn("the game kept running", result)
            self.assertIn("ERROR: debug_error on step 1/2.", result)
            self.assertIn(">> #1 poll_for_collision_node_update at "
                          "core/source/world/world.c:383", result)
            self.assertIn("uuid_u32_of__entry = 536870912", result)
            # The event was drained from the hook.
            self.assertEqual(hook.captured_events, [])
        finally:
            gdb.close()

    def test_step_without_errors_is_unchanged(self):
        from mcp_layered.layer_lav_config import LavConfig
        from mcp_layered.layer_lav_cmd import get_driver

        gdb = self._gdb()
        try:
            self._mock_step.side_effect = [(True, None), (True, None)]
            L._debug_error_report_state["hook"] = None  # unregistered

            result = get_driver("step")(gdb, LavConfig(), {"count": 2})

            self.assertIn("Stepped 2 game frame(s) to post-render.", result)
            self.assertNotIn("debug_error", result)
        finally:
            gdb.close()


class TestLogErrorResponseDedupe(unittest.TestCase):
    """GDBSession._log_error_response dedupes per (command, error): only the
    first GDB_ERROR_LOG_LIMIT occurrences are written; repeats are counted
    and summarized once at close(). A single repeatedly-failing command
    (e.g. an unsupported MI command retried by a bursty hook) must not be
    able to flood the session log."""

    def _session(self, log_file):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            return GDBSession(log_file=log_file)

    def _gdb_error_records(self, log_file):
        with open(log_file) as f:
            recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        return [r for r in recs if r.get("type") == "gdb_error"]

    def test_dedupes_repeated_errors_and_summarizes_at_close(self):
        from mcp_layered import layer_pygdbmi as P
        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        gdb = self._session(log_file)
        try:
            parsed = parse([{
                "type": "result", "message": "error",
                "payload": {"msg": "Undefined MI command: stack-info-arguments"},
            }])
            for _ in range(P.GDB_ERROR_LOG_LIMIT + 2):
                gdb._log_error_response("-stack-info-arguments --frame 1",
                                        parsed[0])
            self.assertEqual(len(self._gdb_error_records(log_file)),
                             P.GDB_ERROR_LOG_LIMIT)
            # close() writes ONE summary record for the suppressed repeats.
            gdb.close()
            errs = self._gdb_error_records(log_file)
            self.assertEqual(len(errs), P.GDB_ERROR_LOG_LIMIT + 1)
            self.assertEqual(errs[-1].get("suppressed_repeats"), 2)
            self.assertEqual(errs[-1].get("total"), P.GDB_ERROR_LOG_LIMIT + 2)
        finally:
            gdb.close()

    def test_distinct_errors_are_not_cross_deduped(self):
        from mcp_layered import layer_pygdbmi as P
        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        gdb = self._session(log_file)
        try:
            for msg in ("error A", "error B"):
                parsed = parse([{
                    "type": "result", "message": "error",
                    "payload": {"msg": msg},
                }])
                for _ in range(P.GDB_ERROR_LOG_LIMIT):
                    gdb._log_error_response("-some-command", parsed[0])
            self.assertEqual(len(self._gdb_error_records(log_file)),
                             2 * P.GDB_ERROR_LOG_LIMIT)
        finally:
            gdb.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
