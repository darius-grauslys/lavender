#!/usr/bin/env python3
"""Verify harness debug-input + debug-scanner helpers with a stub gdbmi.

Run from the repo root:
    python3 -m harness.verify_driver

The scanner tests exercise the *table / demeter* API on DebugScannerBase:
    get_scanner() / get_table() / get_fields() / get_field(demeter) /
    find_demeters(sub)
and assert the exact gdb command strings and the shape of the JSON tables.
"""
import json
import os
import re
import sys

# Ensure the repo root is on sys.path so the ``harness`` package is importable
# regardless of the current working directory.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)

from harness.gdb_frame_controller import GDBFrameController
from harness.lavender_debug import (
    Input_Flags__u32,
    parse_hex,
    _extract_call_value,
    _vector__3i32_literal,
)
from harness.debug_input_driver import DebugInputDriver
from harness.debug_scanner import DebugScannerBase
from harness.debug_scanner_ui import (
    DebugUIScanner,
    DEBUG_UI_SCANNER_FIELDS,
    UI_MANAGER_FIELDS,
    UI_ELEMENT_FIELDS,
)
from harness.debug_scanner_entity import (
    DebugEntityScanner,
    DEBUG_ENTITY_SCANNER_FIELDS,
)
from harness.debug_scanner_scene import (
    DebugSceneScanner,
    DEBUG_SCENE_SCANNER_FIELDS,
)


# --------------------------------------------------------------------------- #
#  Fake gdbmi stubs
# --------------------------------------------------------------------------- #

class FakeGdbmi:
    """A stub gdbmi that returns canned values for a flat scanner struct.

    Works with any ``$<scanner_var>`` convenience variable: if the expression
    is ``$var`` (bare) it returns a struct repr; if it is ``$var.<dotted>``
    it looks up the full dotted suffix in ``self.fields``.  (The suffix keeps
    its dots, so chained C members like ``_serialization_header.uuid`` can be
    canned as a single key.)
    """

    def __init__(self, fields=None, level=3):
        self.fields = dict(fields or {})
        self.commands = []
        self.level = level

    def _struct_repr(self):
        parts = ", ".join(f"{k} = {v}" for k, v in self.fields.items())
        return "{" + parts + "}"

    def _eval(self, expr):
        if "." in expr and expr.startswith("$"):
            # $var.<dotted.field...>
            suffix = expr.split(".", 1)[1]
            return self.fields.get(suffix, "0x0")
        if expr.startswith("$"):
            # $var (bare, struct repr)
            return self._struct_repr()
        return "0x0"

    def write(self, cmd):
        self.commands.append(cmd)
        if cmd.startswith("-stack-info-frame"):
            return [
                {"type": "result", "message": "done",
                 "payload": {"frame": {"level": str(self.level)}}}
            ]
        if cmd.startswith("-data-evaluate-expression"):
            expr = cmd[len("-data-evaluate-expression "):].strip()
            return [{"type": "result", "message": "done",
                     "payload": {"value": self._eval(expr)}}]
        # -stack-select-frame N, -interpreter-exec console "..."
        return [{"type": "result", "message": "done"}]


class FakeUIGdbmi(FakeGdbmi):
    """A stub gdbmi that models the UI scanner's nested managers -> elements.

    ``managers`` maps a manager index to:
        {"allocated": bool,
         "fields": {dotted_field: value},
         "elements": {elem_index: {"ptr": str|None, "fields": {dotted_field: value}}}}
    """

    def __init__(self, top_fields, managers, level=3):
        super().__init__(fields={}, level=level)
        self.top_fields = dict(top_fields)
        self.managers = managers

    def _struct_repr(self):
        parts = ", ".join(f"{k} = {v}" for k, v in self.top_fields.items())
        return "{%s}" % parts

    def _eval(self, expr):
        if expr == "$debug_ui_scanner":
            return self._struct_repr()
        if not expr.startswith("$debug_ui_scanner."):
            return "0x0"
        rest = expr[len("$debug_ui_scanner."):]

        # manager allocation: ...ui_managers[i]._serialization_header.uuid != (Identifier__u32)-1
        m = re.match(
            r"p_ui_context->ui_managers\[(\d+)\]\._serialization_header\.uuid"
            r" != \(Identifier__u32\)-1$", rest)
        if m:
            mgr = self.managers.get(int(m.group(1)))
            return "1" if (mgr and mgr.get("allocated")) else "0"

        # element pointer: ...ui_managers[i].pM_ptr_array_of__ui_elements[j]
        m = re.match(
            r"p_ui_context->ui_managers\[(\d+)\]\."
            r"pM_ptr_array_of__ui_elements\[(\d+)\]$", rest)
        if m:
            el = self.managers.get(int(m.group(1)), {}).get(
                "elements", {}).get(int(m.group(2)))
            return el["ptr"] if (el and el.get("ptr")) else "(UI_Element *) 0x0"

        # element field: ...ui_managers[i].pM_ptr_array_of__ui_elements[j].<dotted>
        m = re.match(
            r"p_ui_context->ui_managers\[(\d+)\]\."
            r"pM_ptr_array_of__ui_elements\[(\d+)\]\.(.+)$", rest)
        if m:
            el = self.managers.get(int(m.group(1)), {}).get(
                "elements", {}).get(int(m.group(2)), {})
            return el.get("fields", {}).get(m.group(3), "0x0")

        # manager field: ...ui_managers[i].<dotted>
        m = re.match(r"p_ui_context->ui_managers\[(\d+)\]\.(.+)$", rest)
        if m:
            return self.managers.get(int(m.group(1)), {}).get(
                "fields", {}).get(m.group(2), "0x0")

        # top-level scanner field
        if rest in self.top_fields:
            return self.top_fields[rest]
        return "0x0"


# ---- Base scanner (synthetic subclass exercising DebugScannerBase) -------- #

class _BaseTestScanner(DebugScannerBase):
    """A minimal scanner used to unit-test the base table/demeter machinery."""

    SCANNER_VAR = "$test_scanner"
    _FUNC_PTR_TYPE = "Test_Func"
    _GET_SCANNER_EXPR = "test_get_scanner(&game)"
    _TOP_LEVEL_FIELDS = ("alpha", "beta", "_serialization_header.uuid")

    def _enrich_table(self, table):
        table["nested"] = {"gamma": "g-value", "deep": {"delta": "d-value"}}


def _base_fields():
    return {
        "alpha": "a-val",
        "beta": "b-val",
        "_serialization_header.uuid": "u-val",
    }


# ---- Base ------------------------------------------------------------------ #

def test_base_scanner():
    g = FakeGdbmi(_base_fields())
    ex = _BaseTestScanner(g)

    # get_scanner: push_main_frame, set $var = test_get_scanner(&game), pop, eval
    repr_s = ex.get_scanner()
    assert repr_s is not None and "alpha = a-val" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $test_scanner = test_get_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"  # pop_frame restores origin

    # get_table: reads each top-level field, then runs the enrichment hook
    table = ex.get_table()
    assert table == {
        "alpha": "a-val",
        "beta": "b-val",
        "_serialization_header": {"uuid": "u-val"},   # dotted field -> nested
        "nested": {"gamma": "g-value", "deep": {"delta": "d-value"}},
    }

    # get_fields: top-level keys of the table (valid top-level demeters)
    assert ex.get_fields() == [
        "alpha", "beta", "_serialization_header", "nested"]

    # get_field: law-of-demeter navigation over the table
    assert ex.get_field("alpha") == "a-val"
    assert ex.get_field("_serialization_header.uuid") == "u-val"
    assert ex.get_field("nested.gamma") == "g-value"
    assert ex.get_field("nested.deep.delta") == "d-value"
    assert ex.get_field("nested") == {
        "gamma": "g-value", "deep": {"delta": "d-value"}}

    # get_field on an unknown demeter raises KeyError
    for bad in ("nope", "alpha.beta", "nested.deep.nope"):
        try:
            ex.get_field(bad)
        except KeyError:
            pass
        else:
            raise AssertionError(f"get_field({bad!r}) should raise KeyError")

    # find_demeters: grep keys, return the valid dot-paths (document order)
    assert ex.find_demeters("uuid") == ["_serialization_header.uuid"]
    assert ex.find_demeters("gamma") == ["nested.gamma"]
    assert ex.find_demeters("delta") == ["nested.deep.delta"]
    assert ex.find_demeters("deep") == ["nested.deep"]
    assert ex.find_demeters("zzz") == []

    # Liskov invariant: the table is JSON-parsable
    round_trip = json.loads(ex.table_json())
    assert round_trip == table

    # caching: a second get_table does NOT re-query gdb
    before = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    ex.get_table()
    after = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    assert before == after, "get_table must be cached"

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  base scanner: OK")


# ---- UI scanner ------------------------------------------------------------ #

_UI_TOP = {
    "p_ui_context": "0x1000",
    "p_ui_manager__current": "0x1000",
    "p_ptr_ui_element__current": "0x2000",
    "m_next_manager": "0x555555555229 <adv_manager>",
    "m_next_element": "0x5555555551c3 <adv_element>",
}


def _ui_managers():
    return {
        0: {
            "allocated": True,
            "fields": {
                "_serialization_header.uuid": "0xAAAA",
                "pM_ui_element_pool": "0x3000",
                "pM_ptr_array_of__ui_elements": "0x4000",
                "p_ui_element__focused": "0x2000",
                "max_quantity_of__ui_elements": "2",
                "ui_manager_flags__u8": "1",
            },
            "elements": {
                0: {"ptr": "0x2000", "fields": {
                    "_serialization_header.uuid": "0xE0001",
                    "p_parent": "0x0",
                    "p_child": "0x0",
                    "p_next": "0x2100",
                    "ui_flags": "4",
                    "the_kind_of_ui_element__this_is": "1",
                }},
                1: {"ptr": "0x2100", "fields": {
                    "_serialization_header.uuid": "0xE0002",
                    "p_parent": "0x2000",
                    "p_child": "0x0",
                    "p_next": "0x0",
                    "ui_flags": "8",
                    "the_kind_of_ui_element__this_is": "3",
                }},
            },
        },
        3: {
            "allocated": True,
            "fields": {
                "_serialization_header.uuid": "0xBBBB",
                "pM_ui_element_pool": "0x5000",
                "pM_ptr_array_of__ui_elements": "0x6000",
                "p_ui_element__focused": "0x0",
                "max_quantity_of__ui_elements": "1",
                "ui_manager_flags__u8": "0",
            },
            "elements": {
                0: {"ptr": "0x7000", "fields": {
                    "_serialization_header.uuid": "0xE1000",
                    "p_parent": "0x0",
                    "p_child": "0x0",
                    "p_next": "0x0",
                    "ui_flags": "2",
                    "the_kind_of_ui_element__this_is": "5",
                }},
            },
        },
        # indices 1,2,4,5,6,7 are deallocated
    }


def test_ui_scanner():
    g = FakeUIGdbmi(_UI_TOP, _ui_managers())
    ex = DebugUIScanner(g)

    # field list mirrors debug_ui.h
    assert DEBUG_UI_SCANNER_FIELDS == (
        "p_ui_context", "p_ui_manager__current", "p_ptr_ui_element__current",
        "m_next_manager", "m_next_element",
    )
    assert set(UI_MANAGER_FIELDS) == {
        "_serialization_header.uuid", "pM_ui_element_pool",
        "pM_ptr_array_of__ui_elements", "p_ui_element__focused",
        "max_quantity_of__ui_elements", "ui_manager_flags__u8",
    }
    assert set(UI_ELEMENT_FIELDS) == {
        "_serialization_header.uuid", "p_parent", "p_child", "p_next",
        "ui_flags", "the_kind_of_ui_element__this_is",
    }

    # get_scanner: push_main_frame, set $var = debug_get_ui_scanner(&game), pop
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_ui_context = 0x1000" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_ui_scanner = debug_get_ui_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"  # pop_frame restores origin

    # get_table: top-level fields + ui_managers nested map
    table = ex.get_table()
    assert table["p_ui_context"] == "0x1000"
    assert table["m_next_element"] == "0x5555555551c3 <adv_element>"
    assert ex.get_fields() == [
        "p_ui_context", "p_ui_manager__current", "p_ptr_ui_element__current",
        "m_next_manager", "m_next_element", "ui_managers",
    ]

    # only allocated managers are mapped, keyed by index
    assert list(table["ui_managers"].keys()) == ["0", "3"]

    # manager 0
    mgr0 = table["ui_managers"]["0"]
    assert mgr0["_serialization_header"]["uuid"] == "0xAAAA"
    assert mgr0["max_quantity_of__ui_elements"] == "2"
    assert list(mgr0["ui_elements"].keys()) == ["0", "1"]
    assert mgr0["ui_elements"]["0"]["_serialization_header"]["uuid"] == "0xE0001"
    assert mgr0["ui_elements"]["1"]["the_kind_of_ui_element__this_is"] == "3"

    # manager 3
    mgr3 = table["ui_managers"]["3"]
    assert mgr3["_serialization_header"]["uuid"] == "0xBBBB"
    assert mgr3["ui_elements"]["0"]["_serialization_header"]["uuid"] == "0xE1000"

    # get_field: navigate the nested table via demeter dot-paths
    assert ex.get_field("ui_managers.0._serialization_header.uuid") == "0xAAAA"
    assert ex.get_field("ui_managers.0.ui_elements.1.p_parent") == "0x2000"
    assert ex.get_field("ui_managers.3") == mgr3  # a nested node -> dict

    # find_demeters: every "...uuid" path, in document order
    assert ex.find_demeters("uuid") == [
        "ui_managers.0._serialization_header.uuid",
        "ui_managers.0.ui_elements.0._serialization_header.uuid",
        "ui_managers.0.ui_elements.1._serialization_header.uuid",
        "ui_managers.3._serialization_header.uuid",
        "ui_managers.3.ui_elements.0._serialization_header.uuid",
    ]

    # Liskov invariant: the table is JSON-parsable
    assert json.loads(ex.table_json()) == table

    # caching: a second get_table does NOT re-query gdb
    before = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    ex.get_table()
    after = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    assert before == after, "get_table must be cached"

    # next_element / next_manager issue the cast-and-call exec, then pop+eval
    g3 = FakeUIGdbmi(_UI_TOP, _ui_managers())
    ex3 = DebugUIScanner(g3)
    ex3.next_element()
    assert g3.commands[2] == '-interpreter-exec console "set $debug_ui_scanner = ((m_DEBUG_UI_Scanner_Func)$debug_ui_scanner.m_next_element)()"', g3.commands[2]

    g4 = FakeUIGdbmi(_UI_TOP, _ui_managers())
    ex4 = DebugUIScanner(g4)
    ex4.next_manager()
    assert g4.commands[2] == '-interpreter-exec console "set $debug_ui_scanner = ((m_DEBUG_UI_Scanner_Func)$debug_ui_scanner.m_next_manager)()"', g4.commands[2]

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  ui scanner: OK")


# ---- Entity scanner -------------------------------------------------------- #

def test_entity_scanner():
    fields = {
        "p_entity_manager": "0x1000",
        "p_entity__current": "0x2000",
        "m_next_entity": "0x555555555100 <adv_entity>",
    }
    g = FakeGdbmi(fields)
    ex = DebugEntityScanner(g)

    # field list mirrors debug_entity.h
    assert DEBUG_ENTITY_SCANNER_FIELDS == (
        "p_entity_manager",
        "p_entity__current",
        "m_next_entity",
    )

    # get_scanner: push_main_frame, set $var, pop
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_entity__current = 0x2000" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_entity_scanner = debug_get_entity_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"

    # flat table: top-level fields only (no enrichment)
    table = ex.get_table()
    assert table == {
        "p_entity_manager": "0x1000",
        "p_entity__current": "0x2000",
        "m_next_entity": "0x555555555100 <adv_entity>",
    }
    assert ex.get_fields() == list(DEBUG_ENTITY_SCANNER_FIELDS)
    assert ex.get_field("p_entity_manager") == "0x1000"
    assert ex.get_field("m_next_entity") == "0x555555555100 <adv_entity>"
    assert ex.find_demeters("manager") == ["p_entity_manager"]
    assert json.loads(ex.table_json()) == table

    # next_entity issues the cast-and-call exec
    g3 = FakeGdbmi(fields)
    ex3 = DebugEntityScanner(g3)
    ex3.next_entity()
    assert g3.commands[2] == '-interpreter-exec console "set $debug_entity_scanner = ((m_DEBUG_Entity_Scanner_Func)$debug_entity_scanner.m_next_entity)()"', g3.commands[2]

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  entity scanner: OK")


# ---- Scene scanner --------------------------------------------------------- #

def test_scene_scanner():
    fields = {
        "p_scene_manager": "0x3000",
        "p_scene__running": "0x4000 <scene_a>",
        "p_scene__current_in__scan": "0x5000 <scene_b>",
        "m_iterate_scene": "0x555555555300 <iterate>",
        "m_go_to__scene": "0x555555555400 <go_to>",
    }
    g = FakeGdbmi(fields)
    ex = DebugSceneScanner(g)

    # field list mirrors debug_scene.h
    assert DEBUG_SCENE_SCANNER_FIELDS == (
        "p_scene_manager",
        "p_scene__running",
        "p_scene__current_in__scan",
        "m_iterate_scene",
        "m_go_to__scene",
    )

    # get_scanner
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_scene__running = 0x4000 <scene_a>" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_scene_scanner = debug_get_scene_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"

    # flat table: top-level fields only (no enrichment)
    table = ex.get_table()
    assert table == {
        "p_scene_manager": "0x3000",
        "p_scene__running": "0x4000 <scene_a>",
        "p_scene__current_in__scan": "0x5000 <scene_b>",
        "m_iterate_scene": "0x555555555300 <iterate>",
        "m_go_to__scene": "0x555555555400 <go_to>",
    }
    assert ex.get_fields() == list(DEBUG_SCENE_SCANNER_FIELDS)
    assert ex.get_field("p_scene_manager") == "0x3000"
    assert ex.get_field("p_scene__running") == "0x4000 <scene_a>"
    assert ex.find_demeters("scene__running") == ["p_scene__running"]
    assert json.loads(ex.table_json()) == table

    # iterate_scene / go_to__scene issue the cast-and-call exec
    g3 = FakeGdbmi(fields)
    ex3 = DebugSceneScanner(g3)
    ex3.iterate_scene()
    assert g3.commands[2] == '-interpreter-exec console "set $debug_scene_scanner = ((m_DEBUG_Scene_Scanner_Func)$debug_scene_scanner.m_iterate_scene)()"', g3.commands[2]

    g4 = FakeGdbmi(fields)
    ex4 = DebugSceneScanner(g4)
    ex4.go_to__scene()
    assert g4.commands[2] == '-interpreter-exec console "set $debug_scene_scanner = ((m_DEBUG_Scene_Scanner_Func)$debug_scene_scanner.m_go_to__scene)()"', g4.commands[2]

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  scene scanner: OK")


# ---- Input driver ---------------------------------------------------------- #

def test_input_driver():
    g = FakeGdbmi()
    d = DebugInputDriver(g)

    # frame stack nesting + main frame selection
    d.push_frame(2)
    assert g.commands == ["-stack-info-frame", "-stack-select-frame 2"]
    assert d._frame_stack == [3]
    d.push_main_frame()
    assert g.commands[-2:] == ["-stack-info-frame", "-stack-select-frame 0"]
    d.pop_frame()
    assert g.commands[-1] == "-stack-select-frame 3"
    assert d._frame_stack == [3]

    # enum mirrors platform_defaults.h
    assert Input_Flags__u32.CLICK == 4096
    assert Input_Flags__u32.FORWARD == 1

    # drive_input__flag emits the right call + frame dance
    d.drive_input__flag(Input_Flags__u32.CLICK)
    assert g.commands[-4] == "-stack-info-frame"
    assert g.commands[-3] == "-stack-select-frame 0"
    assert g.commands[-2] == '-interpreter-exec console "call debug_drive_input__flag(&game, 4096)"'
    assert g.commands[-1] == "-stack-select-frame 3"

    # mouse pos vector literal
    d.drive_input__mouse_pos(10, 20, 5)
    assert g.commands[-2] == '-interpreter-exec console "call debug_drive_input__mouse_pos(&game, (Vector__3i32){10, 20, 5})"'

    # dispatch_click returns parsed pointer from console value
    resp_console = [
        {"type": "console", "payload": "$1 = (Process *) 0x55558018\n"},
        {"type": "result", "message": "done", "payload": None},
    ]

    class _GdbForDispatch(FakeGdbmi):
        def write(self, cmd):
            if cmd.startswith("-interpreter-exec console") and "call debug_dispatch_click" in cmd:
                return resp_console
            return super().write(cmd)

    g3 = _GdbForDispatch()
    d3 = DebugInputDriver(g3)
    assert d3.dispatch_click(7, 8) == "0x55558018"

    # empty stack pop is a safe no-op
    DebugInputDriver(FakeGdbmi()).pop_frame()  # must not raise

    print("  input driver: OK")


# ---- helpers --------------------------------------------------------------- #

def test_helpers():
    assert _vector__3i32_literal(1, 2, 3) == "(Vector__3i32){1, 2, 3}"
    assert _extract_call_value([
        {"type": "console", "payload": "$1 = (Foo *) 0x555555558018 <f>\n"},
        {"type": "result", "message": "done", "payload": None},
    ]) == "0x555555558018"
    assert _extract_call_value([{"type": "result", "message": "done", "payload": None}]) is None

    # _is_null: exact null tokens only; a real address ending in 0 is NOT null
    is_null = DebugScannerBase._is_null
    assert is_null("0") is True
    assert is_null("0x0") is True
    assert is_null("(UI_Element *) 0x0") is True
    assert is_null("(UI_Element *) 0") is True
    assert is_null("(UI_Element *) NULL") is True
    assert is_null(None) is True
    assert is_null("") is True
    assert is_null("0x1000") is False   # ends in 0 but is a live pointer
    assert is_null("0x55558018") is False
    assert is_null("(Process *) 0x55558018") is False

    # _is_truthy / _to_int
    assert DebugScannerBase._is_truthy("1") is True
    assert DebugScannerBase._is_truthy("true") is True
    assert DebugScannerBase._is_truthy("0") is False
    assert DebugScannerBase._is_truthy(None) is False
    assert DebugScannerBase._to_int("2") == 2
    assert DebugScannerBase._to_int("0x10") == 16
    assert DebugScannerBase._to_int("4 <name>") == 4
    assert DebugScannerBase._to_int(None) is None
    assert DebugScannerBase._to_int("n/a") is None
    print("  helpers: OK")


def main():
    test_helpers()
    test_input_driver()
    test_base_scanner()
    test_ui_scanner()
    test_entity_scanner()
    test_scene_scanner()
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
