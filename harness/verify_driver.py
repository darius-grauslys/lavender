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
)
from harness.debug_scanner_entity import (
    DebugEntityScanner,
    DEBUG_ENTITY_SCANNER_FIELDS,
)
from harness.debug_scanner_scene import (
    DebugSceneScanner,
    DEBUG_SCENE_SCANNER_FIELDS,
)

# Sentinel for a deallocated serialization header (defines.h):
#   #define IDENTIFIER__UNKNOWN__u32 (uint32_t)(-1)
_IDENT_UNKNOWN__U32 = "(Identifier__u32)-1"


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
    """A stub gdbmi that models the UI scanner's function-pointer iteration.

    ``managers`` maps a manager pointer to:
        {"uuid": hex_uuid,
         "elements": {elem_ptr: {"uuid": hex_uuid, "kind": int}}}

    The fake tracks which manager / element the scanner is currently
    positioned at (mimicking ``p_ui_manager__current`` /
    ``p_ptr_ui_element__current``).  The cast-and-call advance
    (``((m_DEBUG_UI_Scanner_Func)$debug_ui_scanner.m_next_manager)()``)
    is intercepted in ``write()`` to advance the position.

    On ``get_scanner()`` (the ``set $debug_ui_scanner = ...`` exec), the fake
    resets to the first allocated manager and its first element.
    """

    def __init__(self, top_fields, managers, level=3):
        super().__init__(fields={}, level=level)
        self.top_fields = dict(top_fields)
        # managers: dict[str_ptr -> {"uuid": hex, "elements": dict[ptr -> {"uuid": hex, "kind": int}]}
        self.managers = managers
        self._mgr_keys = list(managers.keys())
        # Position state (set / reset on get_scanner).
        self._current_mgr_idx: int | None = None  # index into _mgr_keys
        self._current_el_ptr: str | None = None

    def _current_mgr_ptr(self) -> str | None:
        if self._current_mgr_idx is None:
            return None
        return self._mgr_keys[self._current_mgr_idx]

    def _current_mgr_data(self) -> dict | None:
        ptr = self._current_mgr_ptr()
        if ptr is None:
            return None
        return self.managers.get(ptr, {})

    def _current_el_data(self) -> dict | None:
        if self._current_el_ptr is None:
            return None
        mgr = self._current_mgr_data()
        if mgr is None:
            return None
        return mgr.get("elements", {}).get(self._current_el_ptr, {})

    def _struct_repr(self):
        """Build a struct repr that reflects the *current* scanner position."""
        mgr_ptr = self._current_mgr_ptr() or "0x0"
        el_ptr_field = self._current_el_ptr or "0x0"
        mgr = self._current_mgr_data()
        mgr_uuid = mgr.get("uuid", _IDENT_UNKNOWN__U32) if mgr else _IDENT_UNKNOWN__U32
        el = self._current_el_data()
        el_uuid = el.get("uuid", _IDENT_UNKNOWN__U32) if el else _IDENT_UNKNOWN__U32
        el_kind = str(el.get("kind", 9)) if el else "9"

        parts = dict(self.top_fields)
        parts["p_ui_context"] = self.top_fields.get("p_ui_context", "0xABCD")
        parts["p_ui_manager__current"] = mgr_ptr
        parts["p_ptr_ui_element__current"] = el_ptr_field
        parts["p_ui_element__current"] = el_ptr_field
        parts["m_next_manager"] = self.top_fields.get("m_next_manager", "0x0")
        parts["m_next_element"] = self.top_fields.get("m_next_element", "0x0")
        parts["m_refresh"] = self.top_fields.get("m_refresh", "0x0")
        parts["uuid_of__ui_manager__current"] = mgr_uuid
        parts["uuid_of__ui_element__current"] = el_uuid
        parts["the_kind_of__ui_element__current"] = el_kind
        parts["max_quantity_of__ui_managers__u32"] = self.top_fields.get("max_quantity_of__ui_managers__u32", "8")
        parts["array_of__quantity_of__elements_in__all_managers__u32"] = self.top_fields.get("array_of__quantity_of__elements_in__all_managers__u32", "[0, 0, 0, 0, 0, 0, 0, 0]")
        # Handler function pointers (mock returns "0x0" for unset).
        parts["m_ui_clicked_handler__current"] = "0x0"
        parts["m_ui_dragged_handler__current"] = "0x0"
        parts["m_ui_dropped_handler__current"] = "0x0"
        parts["m_ui_receive_drop_handler__current"] = "0x0"
        parts["m_ui_held_handler__current"] = "0x0"
        parts["m_ui_typed_handler__current"] = "0x0"
        parts["m_ui_transformed_handler__current"] = "0x0"
        parts["m_ui_compose_handler__current"] = "0x0"
        parts["m_ui_dispose_handler__current"] = "0x0"
        # Tree navigation pointers (mock returns current element for all).
        parts["p_parent__current"] = el_ptr_field
        parts["p_child__current"] = "0x0"
        parts["p_next__current"] = "0x0"
        return "{" + ", ".join(f"{k} = {v}" for k, v in parts.items()) + "}"

    def _advance_manager(self) -> None:
        """Mimic m_next_manager: move to the next allocated manager (circular)."""
        if not self._mgr_keys:
            return
        if self._current_mgr_idx is None:
            self._current_mgr_idx = 0
        else:
            self._current_mgr_idx = (self._current_mgr_idx + 1) % len(self._mgr_keys)
        # Reset element to first when moving to a new manager.
        mgr = self._current_mgr_data()
        if mgr:
            els = mgr.get("elements", {})
            self._current_el_ptr = next(iter(els)) if els else None
        else:
            self._current_el_ptr = None

    def _advance_element(self) -> None:
        """Mimic m_next_element: move to the next allocated element (circular)."""
        mgr = self._current_mgr_data()
        if not mgr:
            self._current_el_ptr = None
            return
        els = mgr.get("elements", {})
        if not els:
            self._current_el_ptr = None
            return
        el_keys = list(els.keys())
        if self._current_el_ptr is None:
            self._current_el_ptr = el_keys[0]
        else:
            idx = el_keys.index(self._current_el_ptr)
            self._current_el_ptr = el_keys[(idx + 1) % len(el_keys)]

    def _handle_batch_call(self, cmd: str) -> list:
        """Simulate a batched call and return console records with struct array.

        Parses the batch expression to determine the sequence of
        ``m_next_manager`` / ``m_next_element`` calls, simulates advancing
        through all positions, and returns a console stream record containing
        the printed struct array.
        """
        # Count the number of each call type in the batch.
        # The expression looks like: call {((FUNC)$s.m_next_manager)(), ((FUNC)$s.m_next_element)(), ...}
        # Note the ")" before "()": it's m_next_manager)(), not m_next_manager().
        import re as _re
        calls = _re.findall(
            r"m_next_manager\)\(\)|m_next_element\)\(\)", cmd)
        # Normalize to the simple name for comparison.
        calls = [c.replace(")", "").replace("(", "") for c in calls]

        # Snapshot the starting state so we can restore after capturing all
        # positions.
        start_mgr_idx = self._current_mgr_idx
        start_el_ptr = self._current_el_ptr

        positions: list[str] = []
        for call_name in calls:
            if call_name == "m_next_manager":
                self._advance_manager()
            elif call_name == "m_next_element":
                self._advance_element()
            # Capture the struct repr after this call.
            positions.append(self._struct_repr())

        # Restore the starting state (the struct array captures all positions).
        self._current_mgr_idx = start_mgr_idx
        self._current_el_ptr = start_el_ptr

        # Build the struct array output: $1 = {<struct1>, <struct2>, ...}
        if not positions:
            struct_array = "$1 = {}"
        else:
            struct_array = "$1 = {" + ", ".join(positions) + "}"

        # Return as a console stream record (like pygdbmi would).
        return [{"type": "console", "payload": struct_array + "\n"}]

    # Override write to intercept the cast-and-call advance and batch calls.
    def write(self, cmd):
        # Intercept batched calls: "call {expr1, expr2, ...}"
        # These contain "m_next_manager" or "m_next_element" and "call" and "{".
        if ("call " in cmd and "{" in cmd and "interpreter-exec console" in cmd
                and ("m_next_manager" in cmd or "m_next_element" in cmd)):
            self.commands.append(cmd)
            return self._handle_batch_call(cmd)

        # Intercept the cast-and-call advance for m_next_manager.
        # (Checked first because the get_scanner reset also starts with
        #  "set $debug_ui_scanner" but uses debug_get_ui_scanner, not m_next_.)
        if "m_next_manager" in cmd and "interpreter-exec console" in cmd:
            self.commands.append(cmd)
            self._advance_manager()
            return [{"type": "result", "message": "done"}]

        # Intercept the cast-and-call advance for m_next_element.
        if "m_next_element" in cmd and "interpreter-exec console" in cmd:
            self.commands.append(cmd)
            self._advance_element()
            return [{"type": "result", "message": "done"}]

        # Intercept the exec for set $debug_ui_scanner (get_scanner).
        # Only matches debug_get_ui_scanner, not the cast-and-call advances above.
        if "-interpreter-exec console \"set $debug_ui_scanner = debug_get_ui_scanner" in cmd:
            self.commands.append(cmd)
            # Reset position: first allocated manager, first element.
            self._current_mgr_idx = 0
            mgr = self._current_mgr_data()
            if mgr:
                els = mgr.get("elements", {})
                self._current_el_ptr = next(iter(els)) if els else None
            else:
                self._current_el_ptr = None
            return [{"type": "result", "message": "done"}]

        return super().write(cmd)

    def _eval(self, expr):
        if expr == "$debug_ui_scanner":
            return self._struct_repr()

        if not expr.startswith("$debug_ui_scanner."):
            return "0x0"
        rest = expr[len("$debug_ui_scanner."):]

        # p_ui_manager__current — the pointer to the current manager.
        if rest == "p_ui_manager__current":
            return self._current_mgr_ptr() or "0x0"

        # p_ptr_ui_element__current — the pointer-to-pointer slot.
        # In the mock, this returns the element pointer directly (simulating
        # the dereferenced value). Real GDB would return a UI_Element ** address.
        if rest == "p_ptr_ui_element__current":
            return self._current_el_ptr or "0x0"

        # p_ui_element__current — the single indirection UI_Element * pointer.
        # This is the same as the element pointer in the mock.
        if rest == "p_ui_element__current":
            return self._current_el_ptr or "0x0"

        # Handler function pointers (mock returns 0x0 for all).
        if rest.endswith("__current") and "handler" in rest:
            return "0x0"

        # Tree navigation pointers.
        if rest == "p_parent__current":
            return self._current_el_ptr or "0x0"
        if rest in ("p_child__current", "p_next__current"):
            return "0x0"

        # Post-condition fields: return based on current position.
        if rest == "uuid_of__ui_manager__current":
            mgr = self._current_mgr_data()
            return mgr.get("uuid", _IDENT_UNKNOWN__U32) if mgr else _IDENT_UNKNOWN__U32

        if rest == "uuid_of__ui_element__current":
            el = self._current_el_data()
            return el.get("uuid", _IDENT_UNKNOWN__U32) if el else _IDENT_UNKNOWN__U32

        if rest == "the_kind_of__ui_element__current":
            el = self._current_el_data()
            return str(el.get("kind", 9)) if el else "9"

        # top-level scanner fields (from the captured struct repr)
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

_MGR0_PTR = "0x1000"
_MGR3_PTR = "0x5000"

# The scanner's post-condition fields (debug_ui.h lines 51-56).
# _struct_repr and _eval return these based on the current position.
_UI_TOP = {
    "p_ui_context": "0xABCD",
    "m_next_manager": "0x555555555229 <adv_manager>",
    "m_next_element": "0x5555555551c3 <adv_element>",
    "m_refresh": "0x555555555330 <refresh>",
    "max_quantity_of__ui_managers__u32": "8",
    "array_of__quantity_of__elements_in__all_managers__u32": "[2, 0, 0, 1, 0, 0, 0, 0]",
}


def _ui_managers():
    """Return pointer-keyed manager data for the UI scanner tests.

    The first manager (0x1000) has two elements (0x2000, 0x2100).
    The second manager (0x5000) has one element (0x7000).

    Each manager has:
        "uuid": hex uuid of the manager
        "elements": {ptr: {"uuid": hex, "kind": int}}
    """
    return {
        _MGR0_PTR: {
            "uuid": "0xAAAA",
            "elements": {
                "0x2000": {"uuid": "0xE0001", "kind": 1},  # UI_Element_Kind__Button
                "0x2100": {"uuid": "0xE0002", "kind": 3},  # UI_Element_Kind__Slider
            },
        },
        _MGR3_PTR: {
            "uuid": "0xBBBB",
            "elements": {
                "0x7000": {"uuid": "0xE1000", "kind": 5},  # UI_Element_Kind__Text
            },
        },
    }


def test_ui_scanner():
    g = FakeUIGdbmi(_UI_TOP, _ui_managers())
    ex = DebugUIScanner(g)

    # field list mirrors debug_ui.h
    assert DEBUG_UI_SCANNER_FIELDS == (
        "p_ui_context", "p_ui_manager__current", "p_ptr_ui_element__current",
        "p_ui_element__current",
        "m_next_manager", "m_next_element", "m_refresh",
        "array_of__quantity_of__elements_in__all_managers__u32",
        "uuid_of__ui_manager__current", "uuid_of__ui_element__current",
        "max_quantity_of__ui_managers__u32", "the_kind_of__ui_element__current",
        "m_ui_clicked_handler__current",
        "m_ui_dragged_handler__current",
        "m_ui_dropped_handler__current",
        "m_ui_receive_drop_handler__current",
        "m_ui_held_handler__current",
        "m_ui_typed_handler__current",
        "m_ui_transformed_handler__current",
        "m_ui_compose_handler__current",
        "m_ui_dispose_handler__current",
        "p_parent__current", "p_child__current", "p_next__current",
    )

    # get_scanner: push_main_frame, set $var = debug_get_ui_scanner(&game), pop
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_ui_context = 0xABCD" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_ui_scanner = debug_get_ui_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"  # pop_frame restores origin

    # get_table: top-level fields + ui_managers nested map
    table = ex.get_table()
    assert table["p_ui_context"] == "0xABCD"
    assert table["m_next_element"] == "0x5555555551c3 <adv_element>"
    assert ex.get_fields() == [
        "p_ui_context", "p_ui_manager__current", "p_ptr_ui_element__current",
        "p_ui_element__current",
        "m_next_manager", "m_next_element", "m_refresh",
        "array_of__quantity_of__elements_in__all_managers__u32",
        "uuid_of__ui_manager__current", "uuid_of__ui_element__current",
        "max_quantity_of__ui_managers__u32", "the_kind_of__ui_element__current",
        "m_ui_clicked_handler__current",
        "m_ui_dragged_handler__current",
        "m_ui_dropped_handler__current",
        "m_ui_receive_drop_handler__current",
        "m_ui_held_handler__current",
        "m_ui_typed_handler__current",
        "m_ui_transformed_handler__current",
        "m_ui_compose_handler__current",
        "m_ui_dispose_handler__current",
        "p_parent__current", "p_child__current", "p_next__current",
        "ui_managers",
    ]

    # only allocated managers are mapped, keyed by pointer
    assert set(table["ui_managers"].keys()) == {_MGR0_PTR, _MGR3_PTR}

    # manager 0
    mgr0 = table["ui_managers"][_MGR0_PTR]
    assert mgr0["uuid"] == "0xAAAA"
    assert mgr0["quantity_of__ui_elements"] == 2
    # elements are keyed by pointer, each entry has uuid and kind
    assert set(mgr0["ui_elements"].keys()) == {"0x2000", "0x2100"}
    assert mgr0["ui_elements"]["0x2000"]["uuid"] == "0xE0001"
    assert mgr0["ui_elements"]["0x2000"]["kind"] == "UI_Element_Kind__Button"
    assert mgr0["ui_elements"]["0x2100"]["uuid"] == "0xE0002"
    assert mgr0["ui_elements"]["0x2100"]["kind"] == "UI_Element_Kind__Slider"

    # manager 1
    mgr3 = table["ui_managers"][_MGR3_PTR]  # mgr3 = 0x5000
    assert mgr3["uuid"] == "0xBBBB"
    assert mgr3["quantity_of__ui_elements"] == 1
    assert mgr3["ui_elements"]["0x7000"]["uuid"] == "0xE1000"
    assert mgr3["ui_elements"]["0x7000"]["kind"] == "UI_Element_Kind__Text"

    # get_field: navigate the nested table via demeter dot-paths
    assert ex.get_field(f"ui_managers.{_MGR0_PTR}.uuid") == "0xAAAA"
    assert ex.get_field(f"ui_managers.{_MGR0_PTR}.ui_elements.0x2100.kind") == "UI_Element_Kind__Slider"
    assert ex.get_field(f"ui_managers.{_MGR3_PTR}") == mgr3  # a nested node -> dict

    # find_demeters: every "...uuid" key, in document order (includes top-level
    # scanner fields like uuid_of__ui_manager__current).
    # Note: mock cycles managers, so mgr3 appears before mgr0 in the batch output.
    assert ex.find_demeters("uuid") == [
        "uuid_of__ui_manager__current",
        "uuid_of__ui_element__current",
        f"ui_managers.{_MGR3_PTR}.uuid",
        f"ui_managers.{_MGR3_PTR}.ui_elements.0x7000.uuid",
        f"ui_managers.{_MGR0_PTR}.uuid",
        f"ui_managers.{_MGR0_PTR}.ui_elements.0x2000.uuid",
        f"ui_managers.{_MGR0_PTR}.ui_elements.0x2100.uuid",
    ]

    # Liskov invariant: the table is JSON-parsable
    assert json.loads(ex.table_json()) == table

    # caching: a second get_table does NOT re-query gdb
    before = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    ex.get_table()
    after = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    assert before == after, "get_table must be cached"

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  ui scanner: OK")


# ---- Entity scanner -------------------------------------------------------- #

# ---- Entity scanner fake ----------------------------------------------------- #

class FakeEntityGdbmi(FakeGdbmi):
    """A stub gdbmi that models the entity scanner's function-pointer iteration.

    ``entities`` maps an entity pointer to:
        {"uuid": hex_uuid, "kind": int}

    The fake tracks which entity the scanner is currently positioned at.
    """

    def __init__(self, top_fields, entities, level=3):
        super().__init__(fields={}, level=level)
        self.top_fields = dict(top_fields)
        self.entities = entities
        self._entity_keys = list(entities.keys())
        self._current_ent_idx: int | None = None

    def _current_ent_ptr(self) -> str | None:
        if self._current_ent_idx is None:
            return None
        return self._entity_keys[self._current_ent_idx]

    def _current_ent_data(self) -> dict | None:
        ptr = self._current_ent_ptr()
        if ptr is None:
            return None
        return self.entities.get(ptr, {})

    def _struct_repr(self):
        ent_ptr = self._current_ent_ptr() or "0x0"
        ent = self._current_ent_data()
        ent_uuid = ent.get("uuid", _IDENT_UNKNOWN__U32) if ent else _IDENT_UNKNOWN__U32
        ent_kind = str(ent.get("kind", 0)) if ent else "0"

        parts = dict(self.top_fields)
        parts["p_entity_manager"] = self.top_fields.get("p_entity_manager", "0x1000")
        parts["p_entity__current"] = ent_ptr
        parts["m_refresh"] = self.top_fields.get("m_refresh", "0x0")
        parts["m_next_entity"] = self.top_fields.get("m_next_entity", "0x0")
        parts["quantity_of__entities"] = self.top_fields.get("quantity_of__entities", "2")
        parts["uuid_of__entity__current"] = ent_uuid
        parts["the_kind_of__entity__current"] = ent_kind
        return "{" + ", ".join(f"{k} = {v}" for k, v in parts.items()) + "}"

    def _advance_entity(self) -> None:
        if not self._entity_keys:
            return
        if self._current_ent_idx is None:
            self._current_ent_idx = 0
        else:
            self._current_ent_idx = (self._current_ent_idx + 1) % len(self._entity_keys)

    def _handle_batch_call(self, cmd: str) -> list:
        import re as _re
        calls = _re.findall(r"m_next_entity\)\(\)", cmd)

        start_idx = self._current_ent_idx
        positions: list[str] = []
        for _ in calls:
            self._advance_entity()
            positions.append(self._struct_repr())

        self._current_ent_idx = start_idx

        if not positions:
            struct_array = "$1 = {}"
        else:
            struct_array = "$1 = {" + ", ".join(positions) + "}"
        return [{"type": "console", "payload": struct_array + "\n"}]

    def write(self, cmd):
        if ("call " in cmd and "{" in cmd and "interpreter-exec console" in cmd
                and "m_next_entity" in cmd):
            self.commands.append(cmd)
            return self._handle_batch_call(cmd)

        if "m_next_entity" in cmd and "interpreter-exec console" in cmd:
            self.commands.append(cmd)
            self._advance_entity()
            return [{"type": "result", "message": "done"}]

        if "-interpreter-exec console \"set $debug_entity_scanner = debug_get_entity_scanner" in cmd:
            self.commands.append(cmd)
            self._current_ent_idx = 0
            return [{"type": "result", "message": "done"}]

        return super().write(cmd)

    def _eval(self, expr):
        if expr == "$debug_entity_scanner":
            return self._struct_repr()

        if not expr.startswith("$debug_entity_scanner."):
            return "0x0"
        rest = expr[len("$debug_entity_scanner."):]

        if rest == "p_entity__current":
            return self._current_ent_ptr() or "0x0"

        if rest == "uuid_of__entity__current":
            ent = self._current_ent_data()
            return ent.get("uuid", _IDENT_UNKNOWN__U32) if ent else _IDENT_UNKNOWN__U32

        if rest == "the_kind_of__entity__current":
            ent = self._current_ent_data()
            return str(ent.get("kind", 0)) if ent else "0"

        if rest in self.top_fields:
            return self.top_fields[rest]
        return "0x0"


# ---- Entity scanner test ----------------------------------------------------- #

def test_entity_scanner():
    _ENTITY0_PTR = "0x2000"
    _ENTITY1_PTR = "0x2100"

    _ENT_TOP = {
        "p_entity_manager": "0x1000",
        "m_refresh": "0x555555555350 <refresh>",
        "m_next_entity": "0x555555555100 <adv_entity>",
        "quantity_of__entities": "2",
    }

    def _entities():
        return {
            _ENTITY0_PTR: {"uuid": "0xE0001", "kind": 0},  # Entity_Kind__None
            _ENTITY1_PTR: {"uuid": "0xE0002", "kind": 1},  # Entity_Kind__Unknown
        }

    g = FakeEntityGdbmi(_ENT_TOP, _entities())
    ex = DebugEntityScanner(g)

    # field list mirrors debug_entity.h
    assert DEBUG_ENTITY_SCANNER_FIELDS == (
        "p_entity_manager", "p_entity__current",
        "m_refresh", "m_next_entity",
        "quantity_of__entities",
        "uuid_of__entity__current",
        "the_kind_of__entity__current",
    )

    # get_scanner
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_entity_manager = 0x1000" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_entity_scanner = debug_get_entity_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"

    # table with entities sub-map (batched)
    table = ex.get_table()
    assert table["p_entity_manager"] == "0x1000"
    assert ex.get_fields() == [
        "p_entity_manager", "p_entity__current",
        "m_refresh", "m_next_entity",
        "quantity_of__entities",
        "uuid_of__entity__current",
        "the_kind_of__entity__current",
        "entities",
    ]

    # only allocated entities are mapped, keyed by pointer
    assert set(table["entities"].keys()) == {_ENTITY0_PTR, _ENTITY1_PTR}
    assert table["entities"][_ENTITY0_PTR] == {
        "uuid": "0xE0001", "kind": "Entity_Kind__None",
    }
    assert table["entities"][_ENTITY1_PTR] == {
        "uuid": "0xE0002", "kind": "Entity_Kind__Unknown",
    }

    # navigate via demeter dot-paths
    assert ex.get_field(f"entities.{_ENTITY0_PTR}.uuid") == "0xE0001"
    assert ex.get_field(f"entities.{_ENTITY1_PTR}.kind") == "Entity_Kind__Unknown"

    # find_demeters
    assert f"entities.{_ENTITY0_PTR}.uuid" in ex.find_demeters("uuid")
    assert f"entities.{_ENTITY1_PTR}.uuid" in ex.find_demeters("uuid")

    # Liskov invariant
    assert json.loads(ex.table_json()) == table

    # caching
    before = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    ex.get_table()
    after = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    assert before == after, "get_table must be cached"

    # next_entity issues the cast-and-call exec
    g3 = FakeEntityGdbmi(_ENT_TOP, _entities())
    ex3 = DebugEntityScanner(g3)
    ex3.next_entity()
    assert g3.commands[2] == '-interpreter-exec console "set $debug_entity_scanner = ((m_DEBUG_Entity_Scanner_Func)$debug_entity_scanner.m_next_entity)()"', g3.commands[2]

    # inheritance
    assert isinstance(ex, GDBFrameController)
    assert isinstance(ex, DebugScannerBase)

    print("  entity scanner: OK")


# ---- Scene scanner --------------------------------------------------------- #

# ---- Scene scanner fake ------------------------------------------------------ #

class FakeSceneGdbmi(FakeGdbmi):
    """A stub gdbmi that models the scene scanner's function-pointer iteration.

    ``scenes`` maps a scene pointer to:
        {"kind": int}
    """

    def __init__(self, top_fields, scenes, level=3):
        super().__init__(fields={}, level=level)
        self.top_fields = dict(top_fields)
        self.scenes = scenes
        self._scene_keys = list(scenes.keys())
        self._current_scene_idx: int | None = None

    def _current_scene_ptr(self) -> str | None:
        if self._current_scene_idx is None:
            return None
        return self._scene_keys[self._current_scene_idx]

    def _current_scene_data(self) -> dict | None:
        ptr = self._current_scene_ptr()
        if ptr is None:
            return None
        return self.scenes.get(ptr, {})

    def _struct_repr(self):
        scene_ptr = self._current_scene_ptr() or "0x0"
        scene = self._current_scene_data()
        scene_kind = str(scene.get("kind", 0)) if scene else "0"

        parts = dict(self.top_fields)
        parts["p_scene_manager"] = self.top_fields.get("p_scene_manager", "0x3000")
        parts["p_scene__running"] = self.top_fields.get("p_scene__running", "0x4000")
        parts["p_scene__current_in__scan"] = scene_ptr
        parts["m_refresh"] = self.top_fields.get("m_refresh", "0x0")
        parts["m_iterate_scene"] = self.top_fields.get("m_iterate_scene", "0x0")
        parts["m_go_to__scene"] = self.top_fields.get("m_go_to__scene", "0x0")
        parts["quantity_of__scenes"] = self.top_fields.get("quantity_of__scenes", "2")
        parts["the_kind_of__scene"] = scene_kind
        return "{" + ", ".join(f"{k} = {v}" for k, v in parts.items()) + "}"

    def _advance_scene(self) -> None:
        if not self._scene_keys:
            return
        if self._current_scene_idx is None:
            self._current_scene_idx = 0
        else:
            self._current_scene_idx = (self._current_scene_idx + 1) % len(self._scene_keys)

    def _handle_batch_call(self, cmd: str) -> list:
        import re as _re
        calls = _re.findall(r"m_iterate_scene\)\(\)", cmd)

        start_idx = self._current_scene_idx
        positions: list[str] = []
        for _ in calls:
            self._advance_scene()
            positions.append(self._struct_repr())

        self._current_scene_idx = start_idx

        if not positions:
            struct_array = "$1 = {}"
        else:
            struct_array = "$1 = {" + ", ".join(positions) + "}"
        return [{"type": "console", "payload": struct_array + "\n"}]

    def write(self, cmd):
        if ("call " in cmd and "{" in cmd and "interpreter-exec console" in cmd
                and "m_iterate_scene" in cmd):
            self.commands.append(cmd)
            return self._handle_batch_call(cmd)

        if "m_iterate_scene" in cmd and "interpreter-exec console" in cmd:
            self.commands.append(cmd)
            self._advance_scene()
            return [{"type": "result", "message": "done"}]

        if "m_go_to__scene" in cmd and "interpreter-exec console" in cmd:
            self.commands.append(cmd)
            return [{"type": "result", "message": "done"}]

        if "-interpreter-exec console \"set $debug_scene_scanner = debug_get_scene_scanner" in cmd:
            self.commands.append(cmd)
            self._current_scene_idx = 0
            return [{"type": "result", "message": "done"}]

        return super().write(cmd)

    def _eval(self, expr):
        if expr == "$debug_scene_scanner":
            return self._struct_repr()

        if not expr.startswith("$debug_scene_scanner."):
            return "0x0"
        rest = expr[len("$debug_scene_scanner."):]

        if rest == "p_scene__current_in__scan":
            return self._current_scene_ptr() or "0x0"

        if rest == "the_kind_of__scene":
            scene = self._current_scene_data()
            return str(scene.get("kind", 0)) if scene else "0"

        if rest in self.top_fields:
            return self.top_fields[rest]
        return "0x0"


# ---- Scene scanner test ------------------------------------------------------ #

def test_scene_scanner():
    _SCENE0_PTR = "0x4000"
    _SCENE1_PTR = "0x5000"

    _SCENE_TOP = {
        "p_scene_manager": "0x3000",
        "p_scene__running": "0x4000 <scene_a>",
        "m_refresh": "0x555555555350 <refresh>",
        "m_iterate_scene": "0x555555555300 <iterate>",
        "m_go_to__scene": "0x555555555400 <go_to>",
        "quantity_of__scenes": "2",
    }

    def _scenes():
        return {
            _SCENE0_PTR: {"kind": 0},  # Scene_Kind__None
            _SCENE1_PTR: {"kind": 1},  # Scene_Kind__Unknown
        }

    g = FakeSceneGdbmi(_SCENE_TOP, _scenes())
    ex = DebugSceneScanner(g)

    # field list mirrors debug_scene.h
    assert DEBUG_SCENE_SCANNER_FIELDS == (
        "p_scene_manager", "p_scene__running", "p_scene__current_in__scan",
        "m_refresh", "m_iterate_scene", "m_go_to__scene",
        "quantity_of__scenes", "the_kind_of__scene",
    )

    # get_scanner
    repr_s = ex.get_scanner()
    assert repr_s is not None and "p_scene_manager = 0x3000" in repr_s
    assert g.commands[0] == "-stack-info-frame"
    assert g.commands[1] == "-stack-select-frame 0"
    assert g.commands[2] == '-interpreter-exec console "set $debug_scene_scanner = debug_get_scene_scanner(&game)"'
    assert g.commands[3] == "-stack-select-frame 3"

    # table with scenes sub-map (batched)
    table = ex.get_table()
    assert table["p_scene_manager"] == "0x3000"
    assert table["p_scene__running"] == "0x4000 <scene_a>"
    assert ex.get_fields() == [
        "p_scene_manager", "p_scene__running", "p_scene__current_in__scan",
        "m_refresh", "m_iterate_scene", "m_go_to__scene",
        "quantity_of__scenes", "the_kind_of__scene",
        "scenes",
    ]

    # only allocated scenes are mapped, keyed by pointer
    assert set(table["scenes"].keys()) == {_SCENE0_PTR, _SCENE1_PTR}
    assert table["scenes"][_SCENE0_PTR] == {"kind": "Scene_Kind__None"}
    assert table["scenes"][_SCENE1_PTR] == {"kind": "Scene_Kind__Unknown"}

    # navigate via demeter dot-paths
    assert ex.get_field(f"scenes.{_SCENE0_PTR}.kind") == "Scene_Kind__None"
    assert ex.get_field(f"scenes.{_SCENE1_PTR}.kind") == "Scene_Kind__Unknown"

    # find_demeters
    assert f"scenes.{_SCENE0_PTR}.kind" in ex.find_demeters("kind")
    assert f"scenes.{_SCENE1_PTR}.kind" in ex.find_demeters("kind")

    # Liskov invariant
    assert json.loads(ex.table_json()) == table

    # caching
    before = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    ex.get_table()
    after = sum(c.startswith("-data-evaluate-expression") for c in g.commands)
    assert before == after, "get_table must be cached"

    # iterate_scene / go_to__scene issue the cast-and-call exec
    g3 = FakeSceneGdbmi(_SCENE_TOP, _scenes())
    ex3 = DebugSceneScanner(g3)
    ex3.iterate_scene()
    assert g3.commands[2] == '-interpreter-exec console "set $debug_scene_scanner = ((m_DEBUG_Scene_Scanner_Func)$debug_scene_scanner.m_iterate_scene)()"', g3.commands[2]

    g4 = FakeSceneGdbmi(_SCENE_TOP, _scenes())
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
