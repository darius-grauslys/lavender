"""
debug_scanner_scene.py — Scene scanner with batched GDB calls (debug_scene.h).

Wraps debug_get_scene_scanner(&game), which returns a DEBUG_Scene_Scanner by
value.  The scanner is captured by value into the gdb convenience variable
``$debug_scene_scanner`` and its state is presented as a nested JSON table.

This module implements **batched** GDB function-pointer calls to minimize
round-trips.  After ``debug_get_scene_scanner`` returns, the scanner has
``quantity_of__scenes`` populated.  We then issue a single
``call {((m_DEBUG_Scene_Scanner_Func)$s.m_iterate_scene)(), ...}`` expression
to visit every allocated scene in one shot.

The table maps each **Scene pointer** to:
    {"kind": <enum name>}

Note: DEBUG_Scene_Scanner does not have a UUID field (scenes are identified
by their kind, not a UUID).  Only allocated scenes appear.

Field layout (see core/include/debug/debug_scene.h):

    typedef struct DEBUG_Scene_Scanner_t {
        Scene_Manager *p_scene_manager;
        Scene *p_scene__running;
        Scene *p_scene__current_in__scan;
        m_DEBUG_Scene_Scanner_Func m_refresh;
        m_DEBUG_Scene_Scanner_Func m_iterate_scene;
        m_DEBUG_Scene_Scanner_Func m_go_to__scene;
        Quantity__u32 quantity_of__scenes;
        Scene_Kind the_kind_of__scene;
    } DEBUG_Scene_Scanner;

Note: debug_scene.h is guarded by ``#ifndef NDEBUG``; the symbols are absent
in release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

import re

from .debug_scanner import DebugScannerBase
from .lavender_debug import parse_hex


# Field layout of DEBUG_Scene_Scanner (see core/include/debug/debug_scene.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_SCENE_SCANNER_FIELDS = (
    "p_scene_manager",
    "p_scene__running",
    "p_scene__current_in__scan",
    "m_refresh",
    "m_iterate_scene",
    "m_go_to__scene",
    "quantity_of__scenes",
    "the_kind_of__scene",
)

# Scene_Kind enum names (types/implemented/scene/scene_kind.h).
_SCENE_KIND_NAMES = (
    "Scene_Kind__None",
    "Scene_Kind__Unknown",
)


class DebugSceneScanner(DebugScannerBase):
    """Scene scanner with batched GDB calls.

    Typical usage (game halted under gdb)::

        ex = DebugSceneScanner(gdbmi)
        ex.get_scanner()
        ex.get_table()      # builds the table with batched calls
    """

    SCANNER_VAR = "$debug_scene_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Scene_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_scene_scanner(&game)"
    _TOP_LEVEL_FIELDS = DEBUG_SCENE_SCANNER_FIELDS

    # -- enrichment: batched iteration --------------------------------------- #

    def _enrich_table(self, table: dict) -> None:
        """Build the ``scenes`` sub-table using a single batched call.

        Strategy:
        1. Read ``quantity_of__scenes`` from the top-level table.
        2. Compose a single batched ``call`` with that many
           ``m_iterate_scene`` calls.
        3. Parse the returned struct array.  Each position has the
           post-condition fields (scene pointer, kind).
        """
        qty = self._to_int(table.get("quantity_of__scenes"))
        if qty is None or qty <= 0:
            table["scenes"] = {}
            return

        # Compose the batched call expression.
        scene_expr = (
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_iterate_scene)()"
        )

        call_exprs: list[str] = [scene_expr for _ in range(qty)]

        # Issue the batched call.
        console_records = self._batch_call(call_exprs)
        positions = self._parse_batch_structs(
            console_records,
            [
                "p_scene__current_in__scan",
                "the_kind_of__scene",
            ],
        )

        # Fallback: if the batch call didn't produce usable field values,
        # fall back to individual _advance + _eval calls.
        if not positions or all(
            p.get("p_scene__current_in__scan") is None for p in positions
        ):
            positions = self._batch_with_eval_fallback(qty)

        # Build the scenes map.
        scenes: dict = {}
        for pos in positions:
            scene_ptr = pos.get("p_scene__current_in__scan")
            if not scene_ptr:
                continue

            scene_key = parse_hex(scene_ptr)
            if not scene_key:
                continue

            kind_name = self._normalize_kind(pos.get("the_kind_of__scene"))
            if scene_key not in scenes:
                scenes[scene_key] = {
                    "kind": kind_name,
                }

        table["scenes"] = scenes

    def _batch_with_eval_fallback(self, qty: int) -> list[dict]:
        """Fallback when batch struct parsing fails."""
        positions: list[dict] = []
        for _ in range(qty):
            self._advance("m_iterate_scene")
            positions.append(self._read_post_condition_fields())
        return positions

    def _read_post_condition_fields(self) -> dict:
        """Read post-condition fields from the current scanner position."""
        return {
            "p_scene__current_in__scan": self._eval(
                f"{self.SCANNER_VAR}.p_scene__current_in__scan"
            ),
            "the_kind_of__scene": self._eval(
                f"{self.SCANNER_VAR}.the_kind_of__scene"
            ),
        }

    @classmethod
    def _normalize_kind(cls, value: str | None) -> str:
        """Normalize the kind field to an enum name string.

        Handles:
        - Integer: ``"0"`` → ``"Scene_Kind__None"``
        - Enum name: ``"Scene_Kind__None"`` → unchanged
        """
        if not value:
            return "Scene_Kind__Unknown"
        text = value.strip()
        if text.startswith("Scene_Kind__"):
            return text
        kind_int = int(text) if text.isdigit() else -1
        if 0 <= kind_int < len(_SCENE_KIND_NAMES):
            return _SCENE_KIND_NAMES[kind_int]
        return "Scene_Kind__Unknown"

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

    # -- advancement (non-batched) --------------------------------------------- #

    def iterate_scene(self) -> str | None:
        """Advance the scanner via ``m_iterate_scene`` (single call)."""
        return self._advance("m_iterate_scene")

    def go_to__scene(self) -> str | None:
        """Trigger a scene transition via ``m_go_to__scene`` (single call)."""
        return self._advance("m_go_to__scene")