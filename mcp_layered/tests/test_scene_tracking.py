"""Tests for scene tracking: debug_scanner_scene + the
set_active_scene_for__scene_manager hook in layer_lav_init.

These tests use a fake GDB that records registered hooks and answers
-data-evaluate-expression with canned values, so they run without a
binary or a display.
"""

import os
import sys
import time
import unittest

# Setup import paths (so this file runs directly and as a module)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARASITIC_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))  # mcp_layered/
_REPO_ROOT = os.path.abspath(os.path.join(_PARASITIC_ROOT, ".."))  # Lavender_Dev/
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _PARASITIC_ROOT)

from mcp_layered.debug_response import DebugResponse, parse
from mcp_layered.debug_scanner_scene import DebugSceneScanner, parse_hex, _is_null
from mcp_layered.layer_lav_init import (
    _normalize_scene_kind,
    _scene_state,
    _register_breakpoint_hooks_for_gdb,
    resolve_pending_scene_transitions,
    resolve_function_name,
    format_scene_status,
    format_scene_transitions,
    reset_scene_state,
)


def _stopped_record(func: str, args: list, reason: str = "breakpoint-hit",
                    file: str = "/x/scene_manager.c",
                    line: str = "72") -> dict:
    """Build a raw pygdbmi-style *stopped notify dict."""
    return {
        "type": "notify",
        "message": "stopped",
        "payload": {
            "reason": reason,
            "bkptno": "6",
            "frame": {
                "func": func,
                "file": file,
                "line": line,
                "args": args,
            },
            "thread-id": "1",
            "stopped-threads": "all",
        },
    }


def _scene_transition_record() -> dict:
    """A *stopped record for the game.c:702 transition line breakpoint."""
    return _stopped_record("run_game", args=[],
                           file="/x/core/source/game.c", line="702")


def _make_global_reads(index: int, kind_name: str,
                       base: str = "0x1000", size: int = 8) -> dict:
    """Canned answers for resolve's direct global reads.

    Simulates the active scene sitting at array *index* (enum *kind_name*),
    with the scenes array at *base* and each Scene *size* bytes.
    """
    active = hex(int(base, 16) + index * size)
    return {
        "game.scene_manager.p_active_scene": active,
        "&game.scene_manager.scenes": base,
        "sizeof(Scene)": str(size),
        f"(Scene_Kind){index}": kind_name,
    }


class _FakeGDB:
    """Fake GDBSession: captures registered breakpoint hooks and answers
    -data-evaluate-expression / -interpreter-exec with canned values."""

    def __init__(self, eval_values: dict | None = None):
        self.hooks: dict = {}      # function-name -> hook (register_breakpoint_hook)
        self.hook_list: list = []  # raw hooks (add_hook)
        self.writes: list[str] = []
        self.eval_values = eval_values or {}
        self.is_closed = False

    def register_breakpoint_hook(self, function, hook_fn):
        self.hooks[function] = hook_fn

    def add_hook(self, hook):
        if hook not in self.hook_list:
            self.hook_list.append(hook)

    def set_breakpoint(self, function, temporary=False):
        return "6"

    def write(self, command, **kwargs):
        self.writes.append(command)
        if command.startswith("-data-evaluate-expression"):
            expr = command[len("-data-evaluate-expression"):].strip()
            value = self.eval_values.get(expr)
            if value is None:
                return [DebugResponse.from_dict(
                    {"type": "result", "message": "error",
                     "payload": {"msg": f"no canned value for {expr!r}"}}
                )]
            return [DebugResponse.from_dict(
                {"type": "result", "message": "done",
                 "payload": {"value": value}}
            )]
        # -interpreter-exec / other: plain done
        return [DebugResponse.from_dict(
            {"type": "result", "message": "done", "payload": {}}
        )]

    def close(self):
        self.is_closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _make_eval_values(active_index: str, active_kind_name: str,
                      new_scene_ptr: str = "0x55555571f420 <game+247360>") -> dict:
    """Canned eval answers for a scanner + hook run.

    Simulates: active scene at array index *active_index* whose enum
    name is *active_kind_name*.
    """
    return {
        "$debug_scene_scanner": "{p_scene_manager = 0x55555571f330 <game+247264>, p_scene__running = 0x55555571f2f8 <game+247208>}",
        "$debug_scene_scanner.p_scene_manager": "0x55555571f330 <game+247264>",
        "$debug_scene_scanner.p_scene__running": "0x55555571f2f8 <game+247208>",
        "(Scene*)$debug_scene_scanner.p_scene__running - (Scene*)$debug_scene_scanner.p_scene_manager->scenes": active_index,
        f"(Scene_Kind){active_index}": active_kind_name,
        "&((Scene_Manager *)0x55555571f330)->scenes[Scene_Kind__MainMenu]": new_scene_ptr,
    }


class TestParseHelpers(unittest.TestCase):
    """parse_hex / _is_null helpers in debug_scanner_scene."""

    def test_parse_hex_decorated(self):
        self.assertEqual(
            parse_hex("0x5555555551c3 <adv_element>"), "0x5555555551c3"
        )

    def test_parse_hex_cast_null(self):
        self.assertIsNone(parse_hex("(Scene *) 0x0"))

    def test_parse_hex_plain(self):
        self.assertEqual(parse_hex("0x1000"), "0x1000")

    def test_parse_hex_none(self):
        self.assertIsNone(parse_hex(None))

    def test_is_null_variants(self):
        for v in ("0", "0x0", "(Scene *) 0", "NULL", None, ""):
            self.assertTrue(_is_null(v), v)
        self.assertFalse(_is_null("0x1000"))
        self.assertFalse(_is_null("1000"))


class TestNormalizeSceneKind(unittest.TestCase):
    """_normalize_scene_kind in layer_lav_init."""

    def test_enum_name_passthrough(self):
        self.assertEqual(
            _normalize_scene_kind("Scene_Kind__MainMenu"), "Scene_Kind__MainMenu"
        )

    def test_integer_becomes_placeholder(self):
        self.assertEqual(_normalize_scene_kind("5"), "Scene_Kind__5")

    def test_hex_integer(self):
        self.assertEqual(_normalize_scene_kind("0x2"), "Scene_Kind__2")

    def test_null_becomes_none_kind(self):
        self.assertEqual(_normalize_scene_kind(None), "Scene_Kind__None")
        self.assertEqual(_normalize_scene_kind("0x0"), "Scene_Kind__None")
        self.assertEqual(_normalize_scene_kind(""), "Scene_Kind__None")

    def test_decorated_value(self):
        self.assertEqual(
            _normalize_scene_kind("  Scene_Kind__Game  "), "Scene_Kind__Game"
        )


class TestSceneHook(unittest.TestCase):
    """The game.c:702 line-breakpoint hook (sets dirty) + deferred
    resolve_pending_scene_transitions (reads the global, records it)."""

    def setUp(self):
        reset_scene_state()

    def tearDown(self):
        reset_scene_state()

    def _register_with_fake(self, eval_values=None):
        gdb = _FakeGDB(eval_values)
        _register_breakpoint_hooks_for_gdb(gdb)
        return gdb

    def test_scene_breakpoint_registered(self):
        """A line breakpoint at game.c:702 is set and a hook is added."""
        gdb = self._register_with_fake()
        self.assertTrue(
            any(w.startswith("-break-insert game.c:702") for w in gdb.writes),
            f"no game.c:702 breakpoint in {gdb.writes}"
        )
        self.assertGreaterEqual(len(gdb.hook_list), 1)

    def test_hook_sets_dirty_on_transition_line(self):
        """A stop at game.c:702 sets dirty and records NO transition yet
        (the scene read is deferred to resolve)."""
        gdb = self._register_with_fake(
            _make_global_reads(2, "Scene_Kind__Options"))
        hook = gdb.hook_list[-1]
        hook(parse([_scene_transition_record()]))
        self.assertEqual(_scene_state["dirty"], 1)
        self.assertEqual(len(_scene_state["transitions"]), 0)

    def test_hook_ignores_other_lines(self):
        """Breakpoint hits elsewhere (different file/line) don't set dirty."""
        gdb = self._register_with_fake()
        hook = gdb.hook_list[-1]
        hook(parse([_stopped_record("run_game", args=[],
                                    file="/x/game.c", line="705")]))
        hook(parse([_stopped_record("other_func", args=[],
                                    file="/x/other.c", line="10")]))
        self.assertEqual(_scene_state["dirty"], 0)

    def test_hook_ignores_non_breakpoint_stops(self):
        """Non-breakpoint stops (e.g. single-step) don't set dirty."""
        gdb = self._register_with_fake()
        hook = gdb.hook_list[-1]
        rec = _stopped_record("run_game", args=[], reason="single-step",
                              file="/x/game.c", line="702")
        hook(parse([rec]))
        self.assertEqual(_scene_state["dirty"], 0)

    def test_resolve_records_transition(self):
        """resolve reads the global and records old->new, clearing dirty."""
        gdb = self._register_with_fake(
            _make_global_reads(2, "Scene_Kind__Options"))
        gdb.hook_list[-1](parse([_scene_transition_record()]))  # dirty=1
        line = resolve_pending_scene_transitions(gdb)
        self.assertEqual(_scene_state["dirty"], 0)
        self.assertEqual(len(_scene_state["transitions"]), 1)
        t = _scene_state["transitions"][0]
        self.assertIsNone(t["from"])  # first scene: no previous
        self.assertEqual(t["to"], "Scene_Kind__Options")
        self.assertEqual(_scene_state["active_kind"], "Scene_Kind__Options")
        self.assertEqual(_scene_state["active_ptr"], t["new_scene_ptr"])
        self.assertIn("Scene transitions:", line)
        self.assertIn("Scene_Kind__Options", line)

    def test_resolve_noop_when_clean(self):
        """No pending transition: resolve returns '' and reads nothing."""
        gdb = self._register_with_fake(
            _make_global_reads(2, "Scene_Kind__Options"))
        before = len(gdb.writes)
        line = resolve_pending_scene_transitions(gdb)
        self.assertEqual(line, "")
        self.assertEqual(len(gdb.writes), before)  # no GDB reads issued
        self.assertEqual(len(_scene_state["transitions"]), 0)

    def test_resolve_degrades_on_error(self):
        """Dirty but the global reads fail (release build): no transition,
        dirty cleared, returns ''."""
        gdb = self._register_with_fake(eval_values={})  # all reads error
        gdb.hook_list[-1](parse([_scene_transition_record()]))  # dirty=1
        line = resolve_pending_scene_transitions(gdb)
        self.assertEqual(line, "")
        self.assertEqual(_scene_state["dirty"], 0)
        self.assertEqual(len(_scene_state["transitions"]), 0)

    def test_resolve_unchanged_scene_no_transition(self):
        """Dirty but the active scene is unchanged: no transition recorded,
        dirty cleared."""
        _scene_state["active_kind"] = "Scene_Kind__Options"
        _scene_state["active_ptr"] = "0x1010"
        gdb = self._register_with_fake(
            _make_global_reads(2, "Scene_Kind__Options"))
        gdb.hook_list[-1](parse([_scene_transition_record()]))  # dirty=1
        line = resolve_pending_scene_transitions(gdb)
        self.assertEqual(line, "")
        self.assertEqual(_scene_state["dirty"], 0)
        self.assertEqual(len(_scene_state["transitions"]), 0)  # unchanged
        self.assertEqual(_scene_state["active_kind"], "Scene_Kind__Options")

    def test_repeated_transitions_record_chain(self):
        """Multiple transitions resolve to a chain of endpoints."""
        gdb = self._register_with_fake(
            _make_global_reads(2, "Scene_Kind__Options"))
        gdb.hook_list[-1](parse([_scene_transition_record()]))
        resolve_pending_scene_transitions(gdb)
        self.assertEqual(_scene_state["active_kind"], "Scene_Kind__Options")

        gdb2 = self._register_with_fake(
            _make_global_reads(3, "Scene_Kind__Game"))
        gdb2.hook_list[-1](parse([_scene_transition_record()]))
        resolve_pending_scene_transitions(gdb2)

        self.assertEqual(len(_scene_state["transitions"]), 2)
        self.assertEqual(
            [t["to"] for t in _scene_state["transitions"]],
            ["Scene_Kind__Options", "Scene_Kind__Game"],
        )
        self.assertEqual(_scene_state["transitions"][1]["from"],
                         "Scene_Kind__Options")


class TestSceneFormatting(unittest.TestCase):
    """format_scene_status / format_scene_transitions."""

    def setUp(self):
        reset_scene_state()

    def tearDown(self):
        reset_scene_state()

    def test_status_empty_without_scene(self):
        self.assertEqual(format_scene_status(), "")

    def test_status_with_scene_and_transitions(self):
        _scene_state["active_kind"] = "Scene_Kind__MainMenu"
        _scene_state["active_ptr"] = "0x55555571f420"
        _scene_state["transitions"].extend([
            {"from": "Scene_Kind__None", "to": "Scene_Kind__Boot", "ts": 1.0},
            {"from": "Scene_Kind__Boot", "to": "Scene_Kind__MainMenu", "ts": 2.0},
        ])
        text = format_scene_status()
        self.assertIn("Scene: Scene_Kind__MainMenu (ptr=0x55555571f420)", text)
        self.assertIn("Scene transitions (most recent last):", text)
        self.assertIn("Scene_Kind__None -> Scene_Kind__Boot", text)
        self.assertIn("Scene_Kind__Boot -> Scene_Kind__MainMenu", text)

    def test_transitions_since_count(self):
        _scene_state["transitions"].extend([
            {"from": "A", "to": "B"},
            {"from": "B", "to": "C"},
            {"from": "C", "to": "D"},
        ])
        self.assertEqual(format_scene_transitions(0), "Scene transitions: A -> B -> C -> D")
        self.assertEqual(format_scene_transitions(1), "Scene transitions: B -> C -> D")
        self.assertEqual(format_scene_transitions(3), "")


class TestDebugSceneScanner(unittest.TestCase):
    """DebugSceneScanner against a fake GDB."""

    def test_get_scanner_captures(self):
        gdb = _FakeGDB({"$debug_scene_scanner": "{p_scene_manager = 0x1}"})
        scanner = DebugSceneScanner(gdb)
        self.assertIsNotNone(scanner.get_scanner())
        self.assertTrue(
            any("set $debug_scene_scanner = debug_get_scene_scanner(&game)" in w
                for w in gdb.writes)
        )

    def test_get_table_reads_fields(self):
        gdb = _FakeGDB({
            "$debug_scene_scanner": "{...}",
            "$debug_scene_scanner.p_scene_manager": "0x55555571f330",
            "$debug_scene_scanner.p_scene__running": "0x55555571f2f8",
            "$debug_scene_scanner.p_scene__current_in__scan": "0x55555571f2f8",
            "$debug_scene_scanner.m_refresh": "0x555555559000 <_m_debug_scene_Scanner__refresh>",
            "$debug_scene_scanner.m_iterate_scene": "0x555555559050",
            "$debug_scene_scanner.m_go_to__scene": "0x555555559100",
            "$debug_scene_scanner.quantity_of__scenes": "12",
            "$debug_scene_scanner.the_kind_of__scene": "Scene_Kind__None",
        })
        scanner = DebugSceneScanner(gdb)
        table = scanner.get_table()
        self.assertEqual(table["quantity_of__scenes"], "12")
        self.assertEqual(table["the_kind_of__scene"], "Scene_Kind__None")
        # cached
        self.assertIs(scanner.get_table(), table)

    def test_get_active_scene_kind(self):
        gdb = _FakeGDB(_make_eval_values("3", "Scene_Kind__MainMenu"))
        scanner = DebugSceneScanner(gdb)
        self.assertEqual(scanner.get_active_scene_kind(), "Scene_Kind__MainMenu")

    def test_get_active_scene_kind_null_active(self):
        gdb = _FakeGDB({
            "$debug_scene_scanner": "{...}",
            "$debug_scene_scanner.p_scene_manager": "0x55555571f330",
            "$debug_scene_scanner.p_scene__running": "(Scene *) 0x0",
        })
        scanner = DebugSceneScanner(gdb)
        self.assertEqual(scanner.get_active_scene_kind(), "Scene_Kind__None")

    def test_get_scenes_table(self):
        """Two scenes; the cursor eval returns a distinct ptr per advance."""
        gdb = _FakeGDB({
            "$debug_scene_scanner": "{...}",
            "$debug_scene_scanner.p_scene_manager": "0x55555571f330",
            "$debug_scene_scanner.p_scene__running": "0x55555571f2f8",
            "$debug_scene_scanner.p_scene__current_in__scan": "0x55555571f2f8",
            "$debug_scene_scanner.quantity_of__scenes": "2",
            "$debug_scene_scanner.the_kind_of__scene": "Scene_Kind__None",
            "((Scene *)0x55555571f2f8)->is_active": "false",
            "((Scene *)0x55555571f3b8)->is_active": "true",
        })
        scanner = DebugSceneScanner(gdb)
        cursor = iter([
            "0x55555571f2f8",  # first iterate -> scene 0
            "0x55555571f3b8",  # second iterate -> scene 1
        ])
        real_write = gdb.write

        def seq_write(command, **kw):
            if command.startswith("-data-evaluate-expression"):
                expr = command[len("-data-evaluate-expression"):].strip()
                if expr == "$debug_scene_scanner.p_scene__current_in__scan":
                    try:
                        val = next(cursor)
                    except StopIteration:
                        val = "0x55555571f2f8"  # wrapped around
                    return [DebugResponse.from_dict(
                        {"type": "result", "message": "done", "payload": {"value": val}}
                    )]
            return real_write(command, **kw)

        gdb.write = seq_write
        scenes = scanner.get_scenes_table()
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes["0x55555571f2f8"]["is_active"], "false")
        self.assertEqual(scenes["0x55555571f3b8"]["is_active"], "true")


class TestResolveFunctionName(unittest.TestCase):
    """resolve_function_name: address -> GDB symbol annotation."""

    def test_resolves_annotated_symbol(self):
        gdb = _FakeGDB({
            "(void*)0x555555570740":
                "0x555555570740 <m_ui_button__clicked_handler__singleplayer>"
        })
        self.assertEqual(
            resolve_function_name(gdb, "0x555555570740"),
            "m_ui_button__clicked_handler__singleplayer",
        )

    def test_unannotated_address_returns_none(self):
        gdb = _FakeGDB({"(void*)0xdeadbeef": "0xdeadbeef"})
        self.assertIsNone(resolve_function_name(gdb, "0xdeadbeef"))

    def test_none_addr_returns_none_no_call(self):
        gdb = _FakeGDB({})
        self.assertIsNone(resolve_function_name(gdb, None))
        self.assertEqual(len(gdb.writes), 0)

    def test_cache_dedupes_lookups(self):
        gdb = _FakeGDB({"(void*)0x1000": "0x1000 <handler_a>"})
        cache: dict = {}
        self.assertEqual(resolve_function_name(gdb, "0x1000", cache), "handler_a")
        writes_after_first = len(gdb.writes)
        self.assertEqual(resolve_function_name(gdb, "0x1000", cache), "handler_a")
        self.assertEqual(len(gdb.writes), writes_after_first)  # cached
        self.assertEqual(cache, {"0x1000": "handler_a"})

    def test_error_degrades_and_negative_caches(self):
        gdb = _FakeGDB({})  # no canned value -> error response
        cache: dict = {}
        self.assertIsNone(resolve_function_name(gdb, "0x1000", cache))
        self.assertEqual(cache, {"0x1000": None})  # negative-cached
        writes_after = len(gdb.writes)
        resolve_function_name(gdb, "0x1000", cache)
        self.assertEqual(len(gdb.writes), writes_after)  # served from cache


if __name__ == "__main__":
    unittest.main(verbosity=2)
