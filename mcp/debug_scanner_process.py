"""
debug_scanner_process.py — Process scanner with batched GDB calls (debug_process.h).

Wraps ``debug_get_process_scanner(&game)``, which returns a DEBUG_Process_Scanner
by value.  The scanner is captured by value into the gdb convenience variable
``$debug_process_scanner`` and its state is presented as a nested JSON table.

This module implements **batched** GDB function-pointer calls to minimize
round-trips.  After ``debug_get_process_scanner`` returns, the scanner has
``quantity_of__processes`` populated.  We then issue a single
``call {((m_DEBUG_Process_Scanner_Func)$s.m_next_process)(), ...}`` expression
to visit every allocated process in one shot.

The table maps each **Process pointer** to:
    {"uuid": <hex uuid>, "kind": <enum name>}

Only allocated processes appear; deallocated slots (UUID ==
IDENTIFIER__UNKNOWN__u32) are omitted.

Field layout (see ``core/include/debug/debug_process.h``)::

    typedef struct DEBUG_Process_Scanner_t {
        Process_Manager         *p_process_manager;
        Process                 *p_process__current;
        m_DEBUG_Process_Scanner_Func m_refresh;
        m_DEBUG_Process_Scanner_Func m_next_process;
        Quantity__u32            quantity_of__processes;
        Identifier__u32          uuid_of__process__current;
        Process_Kind             the_kind_of__process__current;
    } DEBUG_Process_Scanner;

Note: ``debug_process.h`` is guarded by ``#ifndef NDEBUG``; the symbols are
absent in release builds, in which case these calls will error at the gdb
prompt.
"""

from __future__ import annotations

import re

from .debug_scanner import DebugScannerBase
from .lavender_debug import parse_hex


# Field layout of DEBUG_Process_Scanner (see core/include/debug/debug_process.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_PROCESS_SCANNER_FIELDS = (
    "p_process_manager",
    "p_process__current",
    "m_refresh",
    "m_next_process",
    "quantity_of__processes",
    "uuid_of__process__current",
    "the_kind_of__process__current",
)

# Sentinel for a deallocated serialization header (defines.h).
_IDENT_UNKNOWN__U32 = "(Identifier__u32)-1"

# Process_Kind enum names (types/implemented/process/process_kind.h).
# Mirrors the C enum that identifies the type of a Process.
_PROCESS_KIND_NAMES = (
    "Process_Kind__None",
    "Process_Kind__Click",
    "Process_Kind__AI",
    "Process_Kind__Animation",
    "Process_Kind__Physics",
    "Process_Kind__Script",
    "Process_Kind__Timed",
    "Process_Kind__UI",
    "Process_Kind__Unknown",
)


class DebugProcessScanner(DebugScannerBase):
    """Process scanner with batched GDB calls.

    Typical usage (game halted under gdb)::

        ex = DebugProcessScanner(gdbmi)
        ex.get_scanner()
        ex.get_table()      # builds the table with batched calls
    """

    SCANNER_VAR = "$debug_process_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Process_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_process_scanner(&game)"
    _TOP_LEVEL_FIELDS = DEBUG_PROCESS_SCANNER_FIELDS

    # -- enrichment: batched iteration --------------------------------------- #

    def _enrich_table(self, table: dict) -> None:
        """Build the ``processes`` sub-table using a single batched call.

        Strategy:
        1. Read ``quantity_of__processes`` from the top-level table.
        2. Compose a single batched ``call`` with that many ``m_next_process``
           calls.
        3. Parse the returned struct array.  Each position has the
           post-condition fields (uuid, kind).
        4. Skip deallocated slots (UUID == IDENTIFIER__UNKNOWN__u32).
        """
        qty = self._to_int(table.get("quantity_of__processes"))
        if qty is None or qty <= 0:
            table["processes"] = {}
            return

        # Compose the batched call expression.
        process_expr = (
            f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.m_next_process)()"
        )

        call_exprs: list[str] = [process_expr for _ in range(qty)]

        # Issue the batched call.
        console_records = self._batch_call(call_exprs)
        positions = self._parse_batch_structs(
            console_records,
            [
                "p_process__current",
                "uuid_of__process__current",
                "the_kind_of__process__current",
            ],
        )

        # Fallback: if the batch call didn't produce usable field values,
        # fall back to individual _advance + _eval calls.
        if not positions or all(
            p.get("p_process__current") is None for p in positions
        ):
            positions = self._batch_with_eval_fallback(qty)

        # Build the processes map.
        processes: dict = {}
        for pos in positions:
            proc_ptr = pos.get("p_process__current")
            proc_uuid = pos.get("uuid_of__process__current")

            # Skip deallocated or invalid processes.
            if not proc_ptr or not proc_uuid:
                continue
            normalized_uuid = self._normalize_uuid(proc_uuid)
            if normalized_uuid is None or normalized_uuid == _IDENT_UNKNOWN__U32:
                continue
            if proc_uuid.strip() == "4294967295":
                continue

            proc_key = parse_hex(proc_ptr)
            if not proc_key:
                continue

            kind_name = self._normalize_kind(
                pos.get("the_kind_of__process__current")
            )
            if proc_key not in processes:
                processes[proc_key] = {
                    "uuid": normalized_uuid,
                    "kind": kind_name,
                }

        table["processes"] = processes

    def _batch_with_eval_fallback(self, qty: int) -> list[dict]:
        """Fallback when batch struct parsing fails."""
        positions: list[dict] = []
        for _ in range(qty):
            self._advance("m_next_process")
            positions.append(self._read_post_condition_fields())
        return positions

    def _read_post_condition_fields(self) -> dict:
        """Read post-condition fields from the current scanner position."""
        return {
            "p_process__current": self._eval(
                f"{self.SCANNER_VAR}.p_process__current"
            ),
            "uuid_of__process__current": self._eval(
                f"{self.SCANNER_VAR}.uuid_of__process__current"
            ),
            "the_kind_of__process__current": self._eval(
                f"{self.SCANNER_VAR}.the_kind_of__process__current"
            ),
        }

    @classmethod
    def _normalize_kind(cls, value: str | None) -> str:
        """Normalize the kind field to an enum name string.

        Handles:
        - Integer: ``"0"`` → ``"Process_Kind__None"``
        - Enum name: ``"Process_Kind__None"`` → unchanged
        """
        if not value:
            return "Process_Kind__Unknown"
        text = value.strip()
        if text.startswith("Process_Kind__"):
            return text
        kind_int = int(text) if text.isdigit() else -1
        if 0 <= kind_int < len(_PROCESS_KIND_NAMES):
            return _PROCESS_KIND_NAMES[kind_int]
        return "Process_Kind__Unknown"

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

    # -- advancement (non-batched, for next_process) --------------------------- #

    def next_process(self) -> str | None:
        """Advance the scanner via ``m_next_process`` (single call)."""
        return self._advance("m_next_process")
