"""
debug_scanner_entity.py — Entity scanner with batched GDB calls (debug_entity.h).

Wraps debug_get_entity_scanner(&game), which returns a DEBUG_Entity_Scanner
by value.  The scanner is captured by value into the gdb convenience variable
``$debug_entity_scanner`` and its state is presented as a nested JSON table.

This module implements **batched** GDB function-pointer calls to minimize
round-trips.  After ``debug_get_entity_scanner`` returns, the scanner has
``quantity_of__entities`` populated.  We then issue a single
``call {((m_DEBUG_Entity_Scanner_Func)$s.m_next_entity)(), ...}`` expression
to visit every allocated entity in one shot.

The table maps each **Entity pointer** to:
    {"uuid": <hex uuid>, "kind": <enum name>}

Only allocated entities appear; deallocated slots (UUID ==
IDENTIFIER__UNKNOWN__u32) are omitted.

Field layout (see core/include/debug/debug_entity.h):

    typedef struct DEBUG_Entity_Scanner_t {
        Entity_Manager *p_entity_manager;
        Entity *p_entity__current;
        m_DEBUG_Entity_Scanner_Func m_refresh;
        m_DEBUG_Entity_Scanner_Func m_next_entity;
        Quantity__u32 quantity_of__entities;
        Identifier__u32 uuid_of__entity__current;
        Entity_Kind the_kind_of__entity__current;
    } DEBUG_Entity_Scanner;

Note: debug_entity.h is guarded by ``#ifndef NDEBUG``; the symbols are absent
in release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

import re

from .debug_scanner import DebugScannerBase
from .lavender_debug import parse_hex


# Field layout of DEBUG_Entity_Scanner (see core/include/debug/debug_entity.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_ENTITY_SCANNER_FIELDS = (
    "p_entity_manager",
    "p_entity__current",
    "m_refresh",
    "m_next_entity",
    "quantity_of__entities",
    "uuid_of__entity__current",
    "the_kind_of__entity__current",
)

# Sentinel for a deallocated serialization header (defines.h).
_IDENT_UNKNOWN__U32 = "(Identifier__u32)-1"

# Entity_Kind enum names (types/implemented/entity/entity_kind.h).
# Note: this is a minimal enum; real projects typically expand it.
_ENTITY_KIND_NAMES = (
    "Entity_Kind__None",
    "Entity_Kind__Unknown",
)


class DebugEntityScanner(DebugScannerBase):
    """Entity scanner with batched GDB calls.

    Typical usage (game halted under gdb)::

        ex = DebugEntityScanner(gdbmi)
        ex.get_scanner()
        ex.get_table()      # builds the table with batched calls
    """

    SCANNER_VAR = "$debug_entity_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Entity_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_entity_scanner(&game)"
    _TOP_LEVEL_FIELDS = DEBUG_ENTITY_SCANNER_FIELDS

    # -- enrichment: batched iteration --------------------------------------- #

    def _enrich_table(self, table: dict) -> None:
        """Build the ``entities`` sub-table using a single batched call.

        Strategy:
        1. Read ``quantity_of__entities`` from the top-level table.
        2. Compose a single batched ``call`` with that many ``m_next_entity``
           calls.
        3. Parse the returned struct array.  Each position has the
           post-condition fields (uuid, kind).
        4. Skip deallocated slots (UUID == IDENTIFIER__UNKNOWN__u32).
        """
        qty = self._to_int(table.get("quantity_of__entities"))
        if qty is None or qty <= 0:
            table["entities"] = {}
            return

        # Compose the batched call expression.
        entity_expr = (
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_next_entity)()"
        )

        call_exprs: list[str] = [entity_expr for _ in range(qty)]

        # Issue the batched call.
        console_records = self._batch_call(call_exprs)
        positions = self._parse_batch_structs(
            console_records,
            [
                "p_entity__current",
                "uuid_of__entity__current",
                "the_kind_of__entity__current",
            ],
        )

        # Fallback: if the batch call didn't produce usable field values,
        # fall back to individual _advance + _eval calls.
        if not positions or all(
            p.get("p_entity__current") is None for p in positions
        ):
            positions = self._batch_with_eval_fallback(qty)

        # Build the entities map.
        entities: dict = {}
        for pos in positions:
            ent_ptr = pos.get("p_entity__current")
            ent_uuid = pos.get("uuid_of__entity__current")

            # Skip deallocated or invalid entities.
            if not ent_ptr or not ent_uuid:
                continue
            normalized_uuid = self._normalize_uuid(ent_uuid)
            if normalized_uuid is None or normalized_uuid == _IDENT_UNKNOWN__U32:
                continue
            if ent_uuid.strip() == "4294967295":
                continue

            ent_key = parse_hex(ent_ptr)
            if not ent_key:
                continue

            kind_name = self._normalize_kind(pos.get("the_kind_of__entity__current"))
            if ent_key not in entities:
                entities[ent_key] = {
                    "uuid": normalized_uuid,
                    "kind": kind_name,
                }

        table["entities"] = entities

    def _batch_with_eval_fallback(self, qty: int) -> list[dict]:
        """Fallback when batch struct parsing fails."""
        positions: list[dict] = []
        for _ in range(qty):
            self._advance("m_next_entity")
            positions.append(self._read_post_condition_fields())
        return positions

    def _read_post_condition_fields(self) -> dict:
        """Read post-condition fields from the current scanner position."""
        return {
            "p_entity__current": self._eval(f"{self.SCANNER_VAR}.p_entity__current"),
            "uuid_of__entity__current": self._eval(
                f"{self.SCANNER_VAR}.uuid_of__entity__current"
            ),
            "the_kind_of__entity__current": self._eval(
                f"{self.SCANNER_VAR}.the_kind_of__entity__current"
            ),
        }

    @classmethod
    def _normalize_kind(cls, value: str | None) -> str:
        """Normalize the kind field to an enum name string.

        Handles:
        - Integer: ``"0"`` → ``"Entity_Kind__None"``
        - Enum name: ``"Entity_Kind__None"`` → unchanged
        """
        if not value:
            return "Entity_Kind__Unknown"
        text = value.strip()
        if text.startswith("Entity_Kind__"):
            return text
        kind_int = int(text) if text.isdigit() else -1
        if 0 <= kind_int < len(_ENTITY_KIND_NAMES):
            return _ENTITY_KIND_NAMES[kind_int]
        return "Entity_Kind__Unknown"

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
        if text.startswith("0x") or text.startswith("0X"):
            return text
        if "IDENTIFIER__UNKNOWN" in text or text == "-1":
            return _IDENT_UNKNOWN__U32
        try:
            val = int(text)
            return f"0x{val:08x}" if val > 0 else None
        except ValueError:
            pass
        return text

    def _parse_batch_structs(
        self, console_records: list, fields: list[str]
    ) -> list[dict]:
        """Parse a batch call's console output into a list of field dicts."""
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
        m = re.search(r"\$?\d*\s*=\s*\{(.*)\}\s*$", text, re.DOTALL)
        if not m:
            return []
        inner = m.group(1)

        structs = []
        i = 0
        while i < len(inner):
            while i < len(inner) and inner[i] in " \t\n":
                i += 1
            if i >= len(inner):
                break
            if inner[i] != "{":
                i += 1
                continue
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
        """Extract a field value from a struct's printed representation."""
        pattern = rf"{re.escape(field_name)}\s*=\s*(.+?)(?:,\s+\w+\s*=|\}}\s*$)"
        match = re.search(pattern, struct_text, re.DOTALL)
        if match:
            val = match.group(1).strip().rstrip(",").rstrip()
            return val
        return None

    # -- advancement (non-batched, for next_entity) --------------------------- #

    def next_entity(self) -> str | None:
        """Advance the scanner via ``m_next_entity`` (single call)."""
        return self._advance("m_next_entity")
