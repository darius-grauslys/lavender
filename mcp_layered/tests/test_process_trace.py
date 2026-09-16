"""Tests for the process create/remove trace in layer_lav_init.

Run from repo root: python3 -m unittest mcp_layered.tests.test_process_trace -v
Or:                 python3 mcp_layered/tests/test_process_trace.py

The capture (GDB I/O) is exercised against a mocked GDBSession; the deferred
resolve (safe point) is exercised against a real BreakpointHook + a temp log
file. No live GDB is required.
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
from mcp_layered.debug_scanner_process import DebugProcessScanner
import mcp_layered.layer_lav_init as L


def _result_done(payload):
    """A raw (pygdbmi-format) ^done record — what a mocked GdbController.write
    returns. GDBSession.write() runs parse() over it."""
    return [{"type": "result", "message": "done", "payload": payload}]


def _bp_hit(func="add_process_to__process_table",
            args=None, bkpt="3"):
    payload = {"reason": "breakpoint-hit", "bkptno": bkpt,
               "frame": {"func": func, "file": "x.c", "line": "50",
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


class TestCaptureProcessEvent(unittest.TestCase):
    """Test _capture_process_event (the GDB-I/O capture at the hit)."""

    def _write(self, command, *a, **kw):
        if command == "-stack-info-frame":
            # MI: {"frame": {"args": [...]}} — args nest under the frame object.
            return _result_done({"frame": {"args": [
                {"name": "p_process_table", "value": "0x1111"},
                {"name": "p_process", "value": "0x55556e3090"},
            ]}})
        if command.startswith("-data-evaluate-expression p_process->"):
            return _result_done({"value": "0x5555555542a0 <m_process_run__handler__fs>"})
        if command.startswith("-data-evaluate-expression (void*)"):
            return _result_done({"value": "(void *) 0x5555555542a0 <m_process_run__handler__fs>"})
        if command == "-stack-list-frames":
            return _result_done({"stack": [
                {"func": "add_process_to__process_table", "file": "a.c", "line": "54"},
                {"func": "allocate_process_in__process_manager", "file": "b.c", "line": "146"},
                {"func": "main", "file": "main.c", "line": "9"},
            ]})
        return _result_done({})

    def test_capture_reads_ptr_handler_stack(self):
        gdb = _make_gdb(self._write)
        # Frame carries the p_process arg (0 round-trips for the pointer).
        responses = _bp_hit(args=[
            {"name": "p_process_table", "value": "0x1111"},
            {"name": "p_process", "value": "0x55556e3090"},
        ])
        L.reset_process_trace_state()
        ev = L._capture_process_event(gdb, responses, "add")
        self.assertEqual(ev["event"], "add")
        self.assertEqual(ev["ptr"], "0x55556e3090")
        self.assertEqual(ev["handler"], "m_process_run__handler__fs")
        self.assertEqual(len(ev["stack"]), 3)
        self.assertIn("add_process_to__process_table", ev["stack"][0])
        self.assertIn("main", ev["stack"][2])

    def test_capture_null_handler_keeps_raw_addr(self):
        def write(command, *a, **kw):
            if command == "-stack-info-frame":
                # MI: {"frame": {"args": [...]}} — args nest under the frame object.
                return _result_done({"frame": {"args": [
                    {"name": "p_process", "value": "0x55556e3090"}]}})
            if command.startswith("-data-evaluate-expression p_process->"):
                return _result_done({"value": "0x0"})  # NULL handler
            if command == "-stack-list-frames":
                return _result_done({"stack": []})
            return _result_done({})
        gdb = _make_gdb(write)
        responses = _bp_hit()  # no frame args -> falls back to -stack-info-frame
        L.reset_process_trace_state()
        ev = L._capture_process_event(gdb, responses, "remove")
        self.assertEqual(ev["event"], "remove")
        self.assertEqual(ev["ptr"], "0x55556e3090")
        self.assertEqual(ev["handler"], "0x0")  # NULL -> raw addr, not a symbol

    def test_capture_never_raises_on_gdb_failure(self):
        def write(command, *a, **kw):
            raise RuntimeError("gdb gone")
        gdb = _make_gdb(write)
        ev = L._capture_process_event(gdb, _bp_hit(), "add")
        # Degrades gracefully: event is still returned with empty fields.
        self.assertEqual(ev["event"], "add")
        self.assertIsNone(ev["handler"])
        self.assertEqual(ev["stack"], [])


class TestResolveProcessTrace(unittest.TestCase):
    """Test resolve_process_trace (the safe-point drain + log)."""

    def test_drains_and_logs_events(self):
        # Two hooks, each with one captured event.
        add_hook = BreakpointHook.__new__(BreakpointHook)
        add_hook.captured_events = [
            {"event": "add", "ptr": "0x1", "handler": "h1",
             "ts": 1.0, "stack": ["#0 f at a.c:1"]}]
        remove_hook = BreakpointHook.__new__(BreakpointHook)
        remove_hook.captured_events = [
            {"event": "remove", "ptr": "0x2", "handler": "h2",
             "ts": 2.0, "stack": ["#0 g at b.c:2"]}]
        L._process_trace_state["add_hook"] = add_hook
        L._process_trace_state["remove_hook"] = remove_hook

        config = MagicMock()
        config.log_file = None  # None -> stdout

        with patch("builtins.print") as mock_print:
            count = L.resolve_process_trace(MagicMock(), config)
        self.assertEqual(count, 2)
        printed = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertIn("add ptr=0x1 handler=h1", printed)
        self.assertIn("remove ptr=0x2 handler=h2", printed)
        # Events are drained.
        self.assertEqual(add_hook.captured_events, [])
        self.assertEqual(remove_hook.captured_events, [])

    def test_logs_to_file_when_configured(self):
        add_hook = BreakpointHook.__new__(BreakpointHook)
        add_hook.captured_events = [
            {"event": "add", "ptr": "0x9", "handler": "hx",
             "ts": 3.0, "stack": ["#0 f at a.c:1"]}]
        L._process_trace_state["add_hook"] = add_hook
        L._process_trace_state["remove_hook"] = None

        tmpdir = tempfile.mkdtemp()
        config = MagicMock()
        config.log_file = tmpdir  # a directory -> tmpdir/process_trace.log

        count = L.resolve_process_trace(MagicMock(), config)
        self.assertEqual(count, 1)
        log_path = os.path.join(tmpdir, "process_trace.log")
        self.assertTrue(os.path.isfile(log_path))
        with open(log_path) as f:
            content = f.read()
        self.assertIn("add ptr=0x9 handler=hx", content)
        self.assertIn("[process-trace]", content)

    def test_writes_structured_record_to_main_jsonl(self):
        """The PRIMARY trace (structured, keyed by ptr) goes to the session JSONL
        via GDBSession.log_record — the same file as the GDB-response records."""
        add_hook = BreakpointHook.__new__(BreakpointHook)
        add_hook.captured_events = [
            {"event": "add", "ptr": "0x77", "handler": None,
             "ts": 5.0, "stack": ["#0 add_process at a.c:1"]}]
        L._process_trace_state["add_hook"] = add_hook
        L._process_trace_state["remove_hook"] = None
        L._process_trace_state["error_hook"] = None

        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession(log_file=log_file)
            config = MagicMock()
            config.log_file = tmpdir
            count = L.resolve_process_trace(gdb, config)
        self.assertEqual(count, 1)
        with open(log_file) as f:
            recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
        pt = [r for r in recs if r.get("type") == "process-trace"]
        self.assertEqual(len(pt), 1)
        self.assertEqual(pt[0]["event"], "add")
        self.assertEqual(pt[0]["ptr"], "0x77")
        self.assertEqual(pt[0]["stack"], ["#0 add_process at a.c:1"])
        gdb.close()


class TestProcessTraceStateAndWiring(unittest.TestCase):
    """Test the state reset and the hook wiring in _register_breakpoint_hooks_for_gdb."""

    def test_reset_process_trace_state(self):
        L._process_trace_state["add_hook"] = object()
        L._process_trace_state["remove_hook"] = object()
        L._process_trace_state["sym_cache"] = {"x": "y"}
        L.reset_process_trace_state()
        self.assertIsNone(L._process_trace_state["add_hook"])
        self.assertIsNone(L._process_trace_state["remove_hook"])
        self.assertEqual(L._process_trace_state["sym_cache"], {})
        self.assertTrue(L._process_trace_state["enabled"])

    def test_register_creates_and_enables_hooks(self):
        """_register_breakpoint_hooks_for_gdb creates the two process
        BreakpointHooks and enables them (on by default)."""
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_gdb = MagicMock()
            mock_gdb.write.return_value = [
                {"type": "result", "message": "done",
                 "payload": {"bkpt": {"number": "7"}}}]
            mock_cls.return_value = mock_gdb
            gdb = GDBSession()

            L.reset_process_trace_state()
            L._register_breakpoint_hooks_for_gdb(gdb)

            add_hook = L._process_trace_state["add_hook"]
            remove_hook = L._process_trace_state["remove_hook"]
            self.assertIsInstance(add_hook, BreakpointHook)
            self.assertIsInstance(remove_hook, BreakpointHook)
            self.assertTrue(add_hook.enabled)
            self.assertTrue(remove_hook.enabled)
            self.assertEqual(add_hook.bp_number, "7")
            # The registered hooks are present on the session.
            self.assertGreaterEqual(len(gdb._hooks), 2)
            gdb.close()

    def test_register_creates_error_hook(self):
        """The debug_error hook is also created and enabled (property 3)."""
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_gdb = MagicMock()
            mock_gdb.write.return_value = [
                {"type": "result", "message": "done",
                 "payload": {"bkpt": {"number": "9"}}}]
            mock_cls.return_value = mock_gdb
            gdb = GDBSession()
            L.reset_process_trace_state()
            L._register_breakpoint_hooks_for_gdb(gdb)
            error_hook = L._process_trace_state["error_hook"]
            self.assertIsInstance(error_hook, BreakpointHook)
            self.assertTrue(error_hook.enabled)
            self.assertEqual(error_hook.target, "debug_error")
            gdb.close()


class TestLogRecord(unittest.TestCase):
    """Test GDBSession.log_record (inject a structured record into the JSONL)."""

    def test_log_record_appends_to_file(self):
        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "session.jsonl")
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession(log_file=log_file)
            ok = gdb.log_record({"type": "process-trace", "event": "add", "ptr": "0x1"})
            self.assertTrue(ok)
            with open(log_file) as f:
                lines = [l for l in f.read().splitlines() if l.strip()]
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["type"], "process-trace")
            self.assertEqual(rec["ptr"], "0x1")
            gdb.close()

    def test_log_record_no_log_file(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession()  # no log_file -> no-op
            self.assertFalse(gdb.log_record({"a": 1}))
            gdb.close()


class TestCaptureErrorEvent(unittest.TestCase):
    """Test _capture_error_event (debug_error -> poll_process_manager -> p_process)."""

    def test_finds_poll_process_manager_and_reads_ptr(self):
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": [
                    {"func": "debug_error", "file": "e.c", "line": "10"},
                    {"func": "m_process_run__handler__fs", "file": "h.c", "line": "20"},
                    {"func": "poll_process_manager", "file": "pm.c", "line": "185"},
                    {"func": "run_game", "file": "g.c", "line": "731"},
                ]})
            if command == "-stack-select-frame 2":
                return _result_done({"frame": {"func": "poll_process_manager"}})
            if command == "-data-evaluate-expression p_process":
                return _result_done({"value": "0x5555556e30d0"})
            return _result_done({})
        gdb = _make_gdb(write)
        ev = L._capture_error_event(gdb, _bp_hit(func="debug_error"))
        self.assertEqual(ev["event"], "error")
        self.assertEqual(ev["ptr"], "0x5555556e30d0")
        self.assertEqual(len(ev["stack"]), 4)
        self.assertIn("debug_error", ev["stack"][0])
        self.assertIn("poll_process_manager", ev["stack"][2])

    def test_no_poll_process_manager_returns_none(self):
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": [
                    {"func": "debug_error", "file": "e.c", "line": "10"},
                    {"func": "some_other_func", "file": "o.c", "line": "30"},
                ]})
            return _result_done({})
        gdb = _make_gdb(write)
        ev = L._capture_error_event(gdb, _bp_hit(func="debug_error"))
        self.assertIsNone(ev)  # not a process error -> skip (no log noise)

    def test_optimized_out_falls_back_to_handler_first_arg(self):
        """poll_process_manager's p_process local is <optimized out> at -O2; the
        run-handler frame's first arg (passed by value) is the process pointer."""
        def write(command, *a, **kw):
            if command == "-stack-list-frames":
                return _result_done({"stack": [
                    {"func": "debug_error", "file": "e.c", "line": "64"},
                    {"func": "m_process__x__handler", "file": "h.c", "line": "32"},
                    {"func": "poll_process_manager", "file": "pm.c", "line": "185"},
                    {"func": "manage_game__post_render", "file": "g.c", "line": "748"},
                ]})
            if command == "-stack-select-frame 2":
                return _result_done({"frame": {"func": "poll_process_manager"}})
            if command == "-data-evaluate-expression p_process":
                return _result_done({"value": "<optimized out>"})  # local gone at -O2
            if command == "-stack-select-frame 1":
                return _result_done({"frame": {"func": "m_process__x__handler"}})
            if command == "-stack-info-frame":
                # the handler's first param (p_this_process) is the process pointer.
                # MI structure: the args list nests UNDER the `frame` object.
                return _result_done({"frame": {
                    "func": "m_process__x__handler",
                    "args": [
                        {"name": "p_this_process", "value": "0x5555556e31d0"},
                        {"name": "p_game", "value": "0x5555556e3000"}]}})
            return _result_done({})
        gdb = _make_gdb(write)
        ev = L._capture_error_event(gdb, _bp_hit(func="debug_error"))
        self.assertEqual(ev["event"], "error")
        # Recovered the ptr from the handler frame's first arg, not the optimized-out local.
        self.assertEqual(ev["ptr"], "0x5555556e31d0")
        self.assertNotIn("optimized out", ev["ptr"] or "")


class TestDebugProcessScanner(unittest.TestCase):
    """Test DebugProcessScanner.resolve_handler_name (property 4, safe)."""

    def test_resolves_handler_from_annotation(self):
        def write(command, *a, **kw):
            if command.endswith("->m_process_run__handler"):
                return _result_done(
                    {"value": "(m_Process) 0x5555555542a0 <m_process_run__handler__fs>"})
            return _result_done({})
        gdb = _make_gdb(write)
        scanner = DebugProcessScanner(gdb)
        self.assertEqual(
            scanner.resolve_handler_name("0x5555556e30d0"),
            "m_process_run__handler__fs")

    def test_null_ptr_returns_none(self):
        gdb = _make_gdb(lambda c, *a, **kw: _result_done({}))
        scanner = DebugProcessScanner(gdb)
        self.assertIsNone(scanner.resolve_handler_name(None))
        self.assertIsNone(scanner.resolve_handler_name("0x0"))

    def test_null_handler_returns_none(self):
        def write(command, *a, **kw):
            if command.endswith("->m_process_run__handler"):
                return _result_done({"value": "0x0"})
            return _result_done({})
        gdb = _make_gdb(write)
        scanner = DebugProcessScanner(gdb)
        self.assertIsNone(scanner.resolve_handler_name("0x5555556e30d0"))


class TestProcessHandlerDriver(unittest.TestCase):
    """Test the process_handler scanner driver (property 4)."""

    def test_resolves_and_logs_to_jsonl(self):
        def write(command, *a, **kw):
            if command.endswith("->m_process_run__handler"):
                return _result_done(
                    {"value": "(m_Process) 0x5555555542a0 <m_process_run__handler__fs>"})
            return _result_done({})
        tmpdir = tempfile.mkdtemp()
        log_file = os.path.join(tmpdir, "s.jsonl")
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_gdb = MagicMock()
            mock_gdb.write.side_effect = write
            mock_cls.return_value = mock_gdb
            gdb = GDBSession(log_file=log_file)
            L.reset_process_trace_state()
            out = L.process_handler_driver(
                gdb, MagicMock(), {"process_ptr": "0x5555556e30d0"})
            self.assertIn("m_process_run__handler__fs", out)
            self.assertIn("0x5555556e30d0", out)
            # The handler record is logged to the JSONL (event=handler, keyed by ptr).
            with open(log_file) as f:
                recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
            handler_recs = [r for r in recs
                            if r.get("type") == "process-trace"
                            and r.get("event") == "handler"]
            self.assertEqual(len(handler_recs), 1)
            self.assertEqual(handler_recs[0]["ptr"], "0x5555556e30d0")
            self.assertEqual(handler_recs[0]["handler"], "m_process_run__handler__fs")
            gdb.close()

    def test_no_ptr_errors(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession()
            out = L.process_handler_driver(gdb, MagicMock(), {})
            self.assertIn("ERROR", out)
            gdb.close()


def _pool_struct(uuid, ptr, handler, kind="Process_Kind__Timed",
                  status="Process_Status_Kind__Busy", flags=1, priority=0):
    """A realistic ``-data-evaluate-expression $debug_process_scanner`` printout.

    Uses %-formatting (not f-strings) so the literal ``{``/``}`` braces in the
    gdb struct printout are not treated as format fields."""
    return (
        "$3 = {p_process_manager = 0x5555556e3090 <game+832>, "
        "p_process__current = %s, "
        "p_ptr_process__current = 0x5555556e3200, "
        "m_refresh = 0x555555557000 <__m_debug_process_scanner__refresh>, "
        "m_iterate_process = 0x555555558000 <__m_debug_process_scanner__next_process>, "
        "quantity_of__processes = 0, "
        "copy_of__process__current = {_serialization_header = {size_of__struct = 64, "
        "uuid = %s}, "
        "m_process_run__handler = %s, "
        "m_process_dispose__handler = 0x0, p_enqueued_process = 0x0, "
        "p_process_data = 0x7fffdc001000, process_sub_state__u8 = 0, "
        "the_kind_of_status__this_process_has = %s, "
        "the_kind_of__process_this__process_is = %s, "
        "process_flags__u8 = %d '\\%03o', "
        "process_priority__u8 = %d '\\%03o'}}"
    ) % (ptr, uuid, handler, status, kind, flags, flags, priority, priority)


def _empty_pool_struct():
    """A scanner whose current process is deallocated (empty pool)."""
    return (
        "$3 = {p_process_manager = 0x5555556e3090 <game+832>, "
        "p_process__current = 0x0, p_ptr_process__current = 0x0, "
        "m_refresh = 0x555555557000 <__m_debug_process_scanner__refresh>, "
        "m_iterate_process = 0x555555558000 <__m_debug_process_scanner__next_process>, "
        "quantity_of__processes = 0, "
        "copy_of__process__current = {_serialization_header = {size_of__struct = 64, "
        "uuid = 4294967295}, m_process_run__handler = 0x0, m_process_dispose__handler = 0x0, "
        "p_enqueued_process = 0x0, p_process_data = 0x0, process_sub_state__u8 = 0, "
        "the_kind_of_status__this_process_has = Process_Status_Kind__None, "
        "the_kind_of__process_this__process_is = Process_Kind__None, "
        "process_flags__u8 = 0 '\\000', process_priority__u8 = 0 '\\000'}}"
    )


def _pool_gdb(structs):
    """A GDBSession whose ``-data-evaluate-expression $debug_process_scanner``
    returns ``structs[adv]`` where ``adv`` = the number of ``m_iterate_process``
    advances issued so far (cycling). The advance is the
    ``-interpreter-exec console`` that contains ``m_iterate_process``. This makes
    the initial get_scanner eval and the scan_pool's first eval agree (both at
    adv=0), matching real scanner behavior."""
    state = {"adv": 0}

    def write(command, *a, **kw):
        if command.startswith("-interpreter-exec") and "m_iterate_process" in command:
            state["adv"] += 1
            return _result_done({})
        if command == "-data-evaluate-expression $debug_process_scanner":
            return _result_done({"value": structs[state["adv"] % len(structs)]})
        return _result_done({})

    return _make_gdb(write)


class TestProcessPoolScan(unittest.TestCase):
    """Test DebugProcessScanner.scan_pool (the C-scanner-driven pool snapshot)."""

    def test_empty_pool(self):
        gdb = _pool_gdb([_empty_pool_struct()])
        scanner = DebugProcessScanner(gdb)
        scanner.get_scanner()
        pool = scanner.scan_pool()
        self.assertEqual(pool["active"], 0)
        self.assertEqual(pool["capacity"], 512)
        self.assertEqual(pool["free"], 512)
        self.assertFalse(pool["saturated"])
        self.assertEqual(pool["by_handler"], {})
        self.assertEqual(pool["processes"], {})

    def test_three_processes_tallies_by_handler(self):
        structs = [
            _pool_struct(1, "0x5555556e31d0", "0x10 <m_process__resolve>"),
            _pool_struct(2, "0x5555556e31e8", "0x10 <m_process__resolve>"),
            _pool_struct(3, "0x5555556e3200", "0x20 <m_process__deserialize>"),
        ]
        gdb = _pool_gdb(structs)
        scanner = DebugProcessScanner(gdb)
        scanner.get_scanner()
        pool = scanner.scan_pool()
        self.assertEqual(pool["active"], 3)
        self.assertFalse(pool["saturated"])
        self.assertEqual(pool["by_handler"], {"m_process__resolve": 2,
                                              "m_process__deserialize": 1})
        self.assertEqual(pool["processes"]["0x00000001"]["handler"], "m_process__resolve")
        self.assertEqual(pool["processes"]["0x00000001"]["kind"], "Process_Kind__Timed")

    def test_stops_on_ring_wrap(self):
        # A, B, then wrap back to A (uuid 1 repeats) -> stop after 2 distinct.
        a = _pool_struct(1, "0xaaa", "0x10 <m_process__a>")
        b = _pool_struct(2, "0xbbb", "0x10 <m_process__b>")
        gdb = _pool_gdb([a, b])  # cycles a,b,a,b,...
        scanner = DebugProcessScanner(gdb)
        scanner.get_scanner()
        pool = scanner.scan_pool()
        self.assertEqual(pool["active"], 2)
        self.assertEqual(set(pool["processes"].keys()), {"0x00000001", "0x00000002"})

    def test_saturated_when_full(self):
        # Patch capacity down to 3; fill all 3 -> saturated.
        structs = [
            _pool_struct(1, "0x1", "0x10 <m_process__x>"),
            _pool_struct(2, "0x2", "0x10 <m_process__x>"),
            _pool_struct(3, "0x3", "0x10 <m_process__y>"),
        ]
        gdb = _pool_gdb(structs)
        with patch.object(DebugProcessScanner, "_POOL_CAPACITY", 3):
            scanner = DebugProcessScanner(gdb)
            scanner.get_scanner()
            pool = scanner.scan_pool()
        self.assertEqual(pool["capacity"], 3)
        self.assertEqual(pool["active"], 3)
        self.assertTrue(pool["saturated"])

    def test_unavailable_scanner_returns_error(self):
        # The scanner eval yields nothing (release build / not started) -> error dict.
        gdb = _make_gdb(lambda c, *a, **kw: [] if c.startswith("-data-evaluate")
                        else _result_done({}))
        scanner = DebugProcessScanner(gdb)
        pool = scanner.scan_pool()
        self.assertIn("error", pool)
        self.assertEqual(pool["active"], 0)


class TestProcessPoolDriver(unittest.TestCase):
    """Test the process_pool scanner driver (formatting + error paths)."""

    def test_formats_pool_report(self):
        structs = [
            _pool_struct(1, "0x1", "0x10 <m_process__resolve>"),
            _pool_struct(2, "0x2", "0x10 <m_process__resolve>"),
            _pool_struct(3, "0x3", "0x20 <m_process__deserialize>"),
        ]
        gdb = _pool_gdb(structs)
        out = L.process_pool_driver(gdb, MagicMock(), {})
        self.assertIn("Process pool: 3/512 active", out)
        self.assertIn("m_process__resolve", out)
        self.assertIn("m_process__deserialize", out)
        self.assertIn("By run-handler", out)

    def test_scanner_unavailable_errors(self):
        gdb = _make_gdb(lambda c, *a, **kw: [] if c.startswith("-data-evaluate")
                        else _result_done({}))
        out = L.process_pool_driver(gdb, MagicMock(), {})
        self.assertIn("ERROR", out)

    def test_gdb_closed_errors(self):
        with patch("mcp_layered.layer_pygdbmi.GdbController") as mock_cls:
            mock_cls.return_value = MagicMock()
            gdb = GDBSession()
            gdb.close()
            out = L.process_pool_driver(gdb, MagicMock(), {})
            self.assertIn("ERROR", out)
            self.assertIn("closed", out)

    def test_max_iter_kwarg(self):
        # max_iter=1 -> only the first process is captured.
        structs = [
            _pool_struct(1, "0x1", "0x10 <m_process__a>"),
            _pool_struct(2, "0x2", "0x10 <m_process__b>"),
        ]
        gdb = _pool_gdb(structs)
        out = L.process_pool_driver(gdb, MagicMock(), {"max_iter": 1})
        self.assertIn("Process pool: 1/512 active", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
