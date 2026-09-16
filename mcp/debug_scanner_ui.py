"""
debug_scanner_ui.py — UI scanner (debug_ui.h) with batched GDB calls.

Wraps debug_get_ui_scanner(&game), which returns a DEBUG_UI_Scanner by value.
The scanner is captured by value into the gdb convenience variable
``$debug_ui_scanner`` and its state is presented as a nested JSON table.

This module implements **batched** GDB function-pointer calls to minimize
round-trips.  After ``debug_get_ui_scanner`` returns, the scanner has
post-condition fields populated with element counts.  We then issue
a single ``call {((m_DEBUG_UI_Scanner_Func)$s.m_next_manager)(),
((m_DEBUG_UI_Scanner_Func)$s.m_next_element)(), ...}`` expression to
visit every allocated manager and its elements in one shot.

The table maps each **UI_Manager pointer** to:
    {"uuid": <hex uuid>,
     "quantity_of__ui_elements": <int>,
     "ui_elements": {<ptr>: {"uuid": <hex>, "kind": <enum name>}}}

Only allocated managers and elements appear; deallocated slots (UUID ==
IDENTIFIER__UNKNOWN__u32) are omitted.

Note: debug_ui.h is guarded by ``#ifndef NDEBUG``; the symbols are absent in
release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

import re

from .debug_scanner import DebugScannerBase
from .lavender_debug import parse_hex

# Field layout of DEBUG_UI_Scanner (see core/include/debug/debug_ui.h).
DEBUG_UI_SCANNER_FIELDS = (
    "p_ui_context",
    "p_ui_manager__current",
    "p_ptr_ui_element__current",
    "p_ui_element__current",
    "m_next_manager",
    "m_next_element",
    "m_refresh",
    "array_of__quantity_of__elements_in__all_managers__u32",
    "uuid_of__ui_manager__current",
    "uuid_of__ui_element__current",
    "max_quantity_of__ui_managers__u32",
    "the_kind_of__ui_element__current",
    # Handler function pointers (set per-element when scanning).
    "m_ui_clicked_handler__current",
    "m_ui_dragged_handler__current",
    "m_ui_dropped_handler__current",
    "m_ui_receive_drop_handler__current",
    "m_ui_held_handler__current",
    "m_ui_typed_handler__current",
    "m_ui_transformed_handler__current",
    "m_ui_compose_handler__current",
    "m_ui_dispose_handler__current",
    # Tree navigation pointers (parent/child/next in UI element hierarchy).
    "p_parent__current",
    "p_child__current",
    "p_next__current",
)

# Sentinel for a deallocated serialization header (defines.h).
_IDENT_UNKNOWN__U32 = "(Identifier__u32)-1"

# UI_Element_Kind enum names (types/implemented/ui_element_kind.h).
_UI_ELEMENT_KIND_NAMES = (
    "UI_Element_Kind__None",
    "UI_Element_Kind__Button",
    "UI_Element_Kind__Draggable",
    "UI_Element_Kind__Slider",
    "UI_Element_Kind__Drop_Zone",
    "UI_Element_Kind__Text",
    "UI_Element_Kind__Text_Box",
    "UI_Element_Kind__Logical",
    "UI_Element_Kind__Window",
    "UI_Element_Kind__Unknown",
)

MAX_QUANTITY_OF__UI_MANAGERS = 8


class DebugUIScanner(DebugScannerBase):
    """UI scanner with batched GDB calls.

    Typical usage (game halted under gdb)::

        ex = DebugUIScanner(gdbmi)
        ex.get_scanner()
        ex.get_table()      # builds the table with batched calls
    """

    SCANNER_VAR = "$debug_ui_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_UI_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_ui_scanner(&game)"
    _TOP_LEVEL_FIELDS = DEBUG_UI_SCANNER_FIELDS

    # Type-homogeneous groups of the top-level fields for batched reads. GDB
    # prints a whole brace-list in one round-trip but REJECTS mixed-type lists,
    # so each group casts its elements to one type. Within a group, field order
    # must match the printed value order. Single-field groups (the enum and the
    # u32[8] qty-array, which can't share a scalar brace-list) are read with one
    # -data-evaluate-expression. See PLANS/ui_scan_latency.md.
    _FIELD_GROUPS = (
        ("void*", ("p_ui_context", "p_ui_manager__current",
                   "p_ptr_ui_element__current", "p_ui_element__current",
                   "p_parent__current", "p_child__current", "p_next__current")),
        ("void*", ("m_next_manager", "m_next_element", "m_refresh",
                   "m_ui_clicked_handler__current",
                   "m_ui_dragged_handler__current",
                   "m_ui_dropped_handler__current",
                   "m_ui_receive_drop_handler__current",
                   "m_ui_held_handler__current",
                   "m_ui_typed_handler__current",
                   "m_ui_transformed_handler__current",
                   "m_ui_compose_handler__current",
                   "m_ui_dispose_handler__current")),
        ("unsigned int", ("uuid_of__ui_manager__current",
                          "uuid_of__ui_element__current",
                          "max_quantity_of__ui_managers__u32")),
        (None, ("the_kind_of__ui_element__current",)),
        (None, ("array_of__quantity_of__elements_in__all_managers__u32",)),
    )

    def _build_top_level_table(self) -> dict:
        """Read the 24 top-level fields in ~5 round-trips instead of 24.

        Multi-field groups go through one console ``print {…}`` (GDB prints the
        whole brace-list); single-field groups use one ``-data-evaluate-
        expression``. This is the bulk of the ui-scan latency win (see
        PLANS/ui_scan_latency.md): ~4.9 s of per-field reads collapses to ~1 s.
        """
        out: dict = {}
        for cast, fields in self._FIELD_GROUPS:
            if len(fields) == 1:
                f = fields[0]
                expr = (f"({cast}){self.SCANNER_VAR}.{f}" if cast
                        else f"{self.SCANNER_VAR}.{f}")
                out[f] = self._eval(expr)
                continue
            if cast:
                inner = ", ".join(
                    f"({cast}){self.SCANNER_VAR}.{f}" for f in fields)
            else:
                inner = ", ".join(f"{self.SCANNER_VAR}.{f}" for f in fields)
            values = self._parse_value_array(self._console_print(inner))
            for f, v in zip(fields, values):
                out[f] = v
        return out

    # -- enrichment: batched iteration --------------------------------------- #

    def _enrich_table(self, table: dict) -> None:
        """Build the ``ui_managers`` sub-table using a single batched call.

        Strategy:
        1. Read ``max_quantity_of__ui_managers__u32`` from the top-level
           table (already read by get_table()).
        2. Compose a single batched ``call`` expression that visits every
           allocated manager (via ``m_next_manager``) and for each, batches
           ``m_next_element`` calls.  The total number of calls is
           ``N + sum(E_i)`` where N is the manager count and E_i is the
           element count for manager i.
        3. Parse the returned struct array.  Walk the positions, detecting
           manager transitions (when ``p_ui_manager__current`` changes) and
           grouping elements under their current manager.
        4. Skip deallocated slots (UUID == IDENTIFIER__UNKNOWN__u32).
        """
        max_mgrs = self._to_int(
            table.get("max_quantity_of__ui_managers__u32"))
        if max_mgrs is None or max_mgrs <= 0:
            table["ui_managers"] = {}
            return

        qty_array_raw = table.get(
            "array_of__quantity_of__elements_in__all_managers__u32")
        qty_array = self._parse_qty_array(qty_array_raw)

        # Compose the batched call expression.
        # After debug_get_ui_scanner, the scanner is at the last allocated
        # manager.  We batch max_mgrs m_next_manager calls (one per slot),
        # and for each slot with elements, we insert m_next_element calls.
        mgr_expr = (
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_next_manager)()"
        )
        el_expr = (
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_next_element)()"
        )

        call_exprs: list[str] = []
        for i in range(max_mgrs):
            call_exprs.append(mgr_expr)
            el_count = qty_array[i] if i < len(qty_array) else 0
            for j in range(el_count):
                call_exprs.append(el_expr)

        if not call_exprs:
            table["ui_managers"] = {}
            return

        # Issue the batched call.
        console_records = self._batch_call(call_exprs)
        positions = self._parse_batch_structs(
            console_records,
            [
                "p_ui_manager__current",
                "p_ui_element__current",
                "uuid_of__ui_manager__current",
                "uuid_of__ui_element__current",
                "the_kind_of__ui_element__current",
                "m_ui_clicked_handler__current",
                "m_ui_dragged_handler__current",
                "m_ui_dropped_handler__current",
                "m_ui_receive_drop_handler__current",
                "m_ui_held_handler__current",
                "m_ui_typed_handler__current",
                "m_ui_transformed_handler__current",
                "m_ui_compose_handler__current",
                "m_ui_dispose_handler__current",
                "p_parent__current",
                "p_child__current",
                "p_next__current",
            ]
        )

        # Fallback: if the batch call didn't produce usable field values
        # (e.g. the struct output format from real GDB wasn't parsed correctly),
        # fall back to reading the post-condition fields via _eval after
        # each advance.  This preserves the batching for the advancement
        # (reducing round-trips) while ensuring field extraction works.
        if not positions or all(
            p.get("p_ui_manager__current") is None for p in positions
        ):
            positions = self._batch_with_eval_fallback(
                call_exprs, qty_array, max_mgrs
            )

        # Walk the parsed positions, grouping elements under their managers.
        # We detect manager transitions by tracking whether
        # p_ui_manager__current changed since the last position.
        managers: dict = {}
        current_mgr_key: str | None = None
        current_mgr_data: dict | None = None

        for pos in positions:
            mgr_ptr = pos.get("p_ui_manager__current")
            mgr_uuid = pos.get("uuid_of__ui_manager__current")

            # Skip deallocated or invalid managers.
            if not mgr_ptr or not mgr_uuid:
                continue
            # Check for the deallocated sentinel.
            normalized_uuid = self._normalize_uuid(mgr_uuid)
            if normalized_uuid is None or normalized_uuid == _IDENT_UNKNOWN__U32:
                continue
            # Also check decimal form of the sentinel.
            if mgr_uuid.strip() == "4294967295":
                continue

            mgr_key = parse_hex(mgr_ptr)
            if not mgr_key:
                continue

            # Check if this is a new manager.
            if mgr_key != current_mgr_key:
                current_mgr_key = mgr_key
                current_mgr_data = managers.get(mgr_key)
                if current_mgr_data is None:
                    current_mgr_data = {
                        "uuid": self._normalize_uuid(mgr_uuid),
                        "quantity_of__ui_elements": 0,
                        "ui_elements": {},
                    }
                    managers[mgr_key] = current_mgr_data

            # If this position has an element, add it.
            # p_ui_element__current is a UI_Element * (single indirection).
            # The table key is the element address.
            el_ptr = pos.get("p_ui_element__current")
            el_uuid = pos.get("uuid_of__ui_element__current")
            el_kind = pos.get("the_kind_of__ui_element__current")

            if el_ptr and el_uuid:
                # Check for deallocated sentinel (both hex and decimal forms).
                if el_uuid == _IDENT_UNKNOWN__U32 or el_uuid.strip() == "4294967295":
                    continue
                el_key = parse_hex(el_ptr)
                if el_key:
                    # Kind may come as an integer (from mock) or an enum
                    # name string (from real GDB).
                    kind_name = self._normalize_kind(el_kind)
                    if el_key not in current_mgr_data["ui_elements"]:
                        current_mgr_data["ui_elements"][el_key] = {
                            "uuid": self._normalize_uuid(el_uuid),
                            "kind": kind_name,
                            # Handler function pointers (may be None if not set).
                            "handlers": {
                                "clicked": self._normalize_handler_ptr(
                                    pos.get("m_ui_clicked_handler__current")),
                                "dragged": self._normalize_handler_ptr(
                                    pos.get("m_ui_dragged_handler__current")),
                                "dropped": self._normalize_handler_ptr(
                                    pos.get("m_ui_dropped_handler__current")),
                                "receive_drop": self._normalize_handler_ptr(
                                    pos.get("m_ui_receive_drop_handler__current")),
                                "held": self._normalize_handler_ptr(
                                    pos.get("m_ui_held_handler__current")),
                                "typed": self._normalize_handler_ptr(
                                    pos.get("m_ui_typed_handler__current")),
                                "transformed": self._normalize_handler_ptr(
                                    pos.get("m_ui_transformed_handler__current")),
                                "compose": self._normalize_handler_ptr(
                                    pos.get("m_ui_compose_handler__current")),
                                "dispose": self._normalize_handler_ptr(
                                    pos.get("m_ui_dispose_handler__current")),
                            },
                            # Tree navigation pointers (UI_Element *).
                            "p_parent": self._normalize_ptr(
                                pos.get("p_parent__current")),
                            "p_child": self._normalize_ptr(
                                pos.get("p_child__current")),
                            "p_next": self._normalize_ptr(
                                pos.get("p_next__current")),
                        }
                    current_mgr_data["quantity_of__ui_elements"] = len(
                        current_mgr_data["ui_elements"]
                    )

        table["ui_managers"] = managers

    def _batch_with_eval_fallback(
        self, call_exprs: list[str], qty_array: list[int], max_mgrs: int
    ) -> list[dict]:
        """Fallback when batch struct parsing fails.

        Advances the scanner via individual ``_advance`` calls (which still
        use the cast-and-call pattern), but reads the post-condition fields
        via ``_eval`` after each step.  This is slower than pure batching but
        ensures correctness when the batch struct array format isn't parseable.
        """
        positions: list[dict] = []
        for i in range(max_mgrs):
            # Advance to next manager.
            self._advance("m_next_manager")
            positions.append(self._read_post_condition_fields("manager"))

            el_count = qty_array[i] if i < len(qty_array) else 0
            for j in range(el_count):
                self._advance("m_next_element")
                positions.append(self._read_post_condition_fields("element"))
        return positions

    def _read_post_condition_fields(self, step_type: str) -> dict:
        """Read post-condition fields from the current scanner position."""
        fields = [
            "p_ui_manager__current",
            "p_ui_element__current",
            "uuid_of__ui_manager__current",
            "uuid_of__ui_element__current",
            "the_kind_of__ui_element__current",
            "m_ui_clicked_handler__current",
            "m_ui_dragged_handler__current",
            "m_ui_dropped_handler__current",
            "m_ui_receive_drop_handler__current",
            "m_ui_held_handler__current",
            "m_ui_typed_handler__current",
            "m_ui_transformed_handler__current",
            "m_ui_compose_handler__current",
            "m_ui_dispose_handler__current",
            "p_parent__current",
            "p_child__current",
            "p_next__current",
        ]
        pos: dict = {}
        for field in fields:
            pos[field] = self._eval(f"{self.SCANNER_VAR}.{field}")
        return pos

    def _parse_qty_array(self, raw: str | None) -> list[int]:
        """Parse gdb's printed array, e.g. ``"{2, 0, 0, 1, 0, 0, 0, 0}"``.

        Handles both curly-brace ``{...}`` and square-bracket ``[...]`` formats.
        """
        if not raw:
            return [0] * MAX_QUANTITY_OF__UI_MANAGERS
        inner = raw.strip()
        # Strip outer braces or brackets.
        if inner.startswith("{") and inner.endswith("}"):
            inner = inner[1:-1]
        elif inner.startswith("[") and inner.endswith("]"):
            inner = inner[1:-1]
        if not inner:
            return [0] * MAX_QUANTITY_OF__UI_MANAGERS
        parts = [p.strip() for p in inner.split(",")]
        result = []
        for p in parts:
            val = self._to_int(p)
            result.append(val if val is not None else 0)
        # Pad to MAX_QUANTITY_OF__UI_MANAGERS if needed.
        while len(result) < MAX_QUANTITY_OF__UI_MANAGERS:
            result.append(0)
        return result

    @classmethod
    def _normalize_kind(cls, value: str | None) -> str:
        """Normalize the kind field to an enum name string.

        Handles:
        - Integer: ``"1"`` → ``"UI_Element_Kind__Button"``
        - Enum name: ``"UI_Element_Kind__Button"`` → unchanged
        """
        if not value:
            return "UI_Element_Kind__Unknown"
        text = value.strip()
        # Already an enum name?
        if text.startswith("UI_Element_Kind__"):
            return text
        # Integer index?
        kind_int = int(text) if text.isdigit() else -1
        if 0 <= kind_int < len(_UI_ELEMENT_KIND_NAMES):
            return _UI_ELEMENT_KIND_NAMES[kind_int]
        return "UI_Element_Kind__Unknown"

    @staticmethod
    def _normalize_uuid(value: str | None) -> str | None:
        """Normalize a UUID value to a consistent string format.

        Handles:
        - Hex strings: ``"0xAAAA"`` → ``"0xAAAA"``
        - Decimal integers: ``"4059140233"`` → ``"0xF1E2D3C9"``
        - Sentinel: ``"(Identifier__u32)-1"`` → unchanged
        """
        if not value:
            return None
        text = value.strip()
        # Already hex?
        if text.startswith("0x") or text.startswith("0X"):
            return text
        # Sentinel?
        if "IDENTIFIER__UNKNOWN" in text or text == "-1":
            return _IDENT_UNKNOWN__U32
        # Decimal integer?
        try:
            val = int(text)
            return f"0x{val:08x}" if val > 0 else None
        except ValueError:
            pass
        return text

    @staticmethod
    def _normalize_handler_ptr(value: str | None) -> str | None:
        """Normalize a function pointer value.

        Returns the pointer value as gdb printed it — the hex address **plus
        its ``<symbol>`` annotation when present** (e.g. ``0x555555562f90
        <m_ui_button__clicked_handler__singleplayer>``) — or None if the
        handler is not set (null/zero). Keeping the annotation is deliberate:
        it carries the handler's function name for free, so callers do not
        need an extra GDB round-trip to resolve it (see
        PLANS/ui_scan_latency.md).
        """
        if not value:
            return None
        text = value.strip()
        if not text or text == "0" or text == "0x0":
            return None
        if re.match(r"0x[0-9a-fA-F]+", text):
            return text  # "0xADDR" or "0xADDR <symbol>"
        return text

    @staticmethod
    def _normalize_ptr(value: str | None) -> str | None:
        """Normalize a UI_Element * pointer value.

        Returns the pointer address as a hex string, or None if the
        pointer is null/zero.
        """
        if not value:
            return None
        text = value.strip()
        if not text or text == "0" or text == "0x0":
            return None
        # Extract the address from gdb's output format:
        # "0x555555814030" or "0x555555813030 <some_symbol>"
        addr_match = re.match(r"(0x[0-9a-fA-F]+)", text)
        if addr_match:
            return addr_match.group(1)
        if text.startswith("0x"):
            return text
        return text if text else None

    def _parse_batch_structs(
        self, console_records: list, fields: list[str]
    ) -> list[dict]:
        """Parse a batch call's console output into a list of field dicts.

        The console output for a batch call looks like::

            $1 = {<struct1>, <struct2>, ...}

        Each struct has fields like ``p_ui_manager__current = 0x...``.
        """
        text = ""
        for rec in console_records:
            text += rec.get("payload", "") or ""

        structs = self._split_struct_array(text)

        results: list[dict] = []
        for struct_text in structs:
            entry: dict = {}
            for field in fields:
                val = self._extract_field(struct_text, field)
                entry[field] = val
            results.append(entry)
        return results

    def _split_struct_array(self, text: str) -> list[str]:
        """Split a batch call's output into individual struct strings."""
        # Find the struct array: "$N = {struct1, struct2, ...}"
        m = re.search(r"\$?\d*\s*=\s*\{(.*)\}\s*$", text, re.DOTALL)
        if not m:
            return []
        inner = m.group(1)

        # The inner content is a sequence of {struct1}, {struct2}, ...
        # Each struct is delimited by { and } at depth 0.
        # Extract each top-level {...} block.
        structs = []
        i = 0
        while i < len(inner):
            # Skip whitespace.
            while i < len(inner) and inner[i] in " \t\n":
                i += 1
            if i >= len(inner):
                break
            # Expect a {
            if inner[i] != "{":
                i += 1
                continue
            # Find the matching }
            depth = 1
            start = i
            i += 1
            while i < len(inner) and depth > 0:
                if inner[i] == "{":
                    depth += 1
                elif inner[i] == "}":
                    depth -= 1
                i += 1
            structs.append(inner[start:i].strip())

        return structs

    def _extract_field(self, struct_text: str, field_name: str) -> str | None:
        """Extract a field value from a struct's printed representation.

        Looks for ``field_name = value`` where value extends until the next
        ``field = `` or the closing ``}``.
        """
        pattern = rf"{re.escape(field_name)}\s*=\s*(.+?)(?:,\s+\w+\s*=|\}}\s*$)"
        match = re.search(pattern, struct_text, re.DOTALL)
        if match:
            val = match.group(1).strip().rstrip(",").rstrip()
            return val
        return None

    # -- advancement (non-batched, for next_element/next_manager) ----------- #

    def next_element(self) -> str | None:
        """Advance the scanner via ``m_next_element`` (single call)."""
        return self._advance("m_next_element")

    def next_manager(self) -> str | None:
        """Advance the scanner via ``m_next_manager`` (single call)."""
        return self._advance("m_next_manager")
