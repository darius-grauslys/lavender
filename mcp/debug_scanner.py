"""
debug_scanner.py — Scan-pattern base class.

DebugScannerBase
    Generic mechanism for capturing a debug struct **by value** into a gdb
    convenience variable, presenting its state as a JSON-parsable nested
    *table*, and navigating that table via dot-paths ("demeters").

    Public API:
        get_scanner()                capture the struct by value into SCANNER_VAR
        get_table() -> dict          nested JSON-parsable snapshot of the state
        get_fields() -> list[str]    top-level field names (keys of the table)
        get_field(demeter) -> json   value at dot-path *demeter* in the table
        find_demeters(sub) -> list   dot-paths whose key contains *sub*

    The table is the scanner's single source of truth.  `get_table()` is the
    **only** method that talks to gdb for reads; everything else navigates the
    table it returns.  This is the "law of demeter" contract: a caller only
    ever steps one level at a time through the JSON (one dot = one level).

    Liskov contract: *every* subclass must return a table that is
    **JSON-parsable** — a graph of `dict`/`list`/`str`/`int`/`float`/`bool`/
    `None`.  The schema is **not** required to be uniform across subtypes; the
    only invariant is `json.dumps(scanner.get_table())` never raises.  Subtypes
    that manage an iterating structure (e.g. the UI scanner's managers →
    elements) override `_enrich_table()` to add the nested mappings.

    gdb cannot call a function pointer stored inside a convenience variable
    (error: "Attempt to take address of value not located in memory"), so
    advancement works by cast-and-call:
        set $var = ((FuncType)$var.m_field)()

Concrete scanners live in their own modules, here are some examples:
    debug_scanner_ui.py     — DebugUIScanner (debug_ui.h)
    debug_scanner_entity.py — DebugEntityScanner (debug_entity.h)
    debug_scanner_scene.py  — DebugSceneScanner (debug_scene.h)

All three mirror the same C pattern: a DEBUG_*_Scanner struct returned by value
from ``debug_get_*_scanner(&game)``, with function-pointer fields for advancement.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .gdb_frame_controller import GDBFrameController


# gdb prints a null pointer several ways depending on type/verbosity:
#   "0", "0x0", "(UI_Element *) 0x0", "(UI_Element *) 0", "(UI_Element *) NULL"
# Match an *exact* null token (optionally wrapped in a "(Type)" cast prefix),
# so that a real address like "0x1000" (which merely ends in 0) is NOT null.
_NULL_RE = re.compile(r"^\s*(?:\([^()]*\)\s*)?(0x0|0|NULL)\s*$")


def _set_path(node: dict, dotted_key: str, value: Any) -> None:
    """Set *value* in *node* at the dotted path *dotted_key*.

    Intermediate segments are created as dicts, so a C member read via a
    chained gdb expression (e.g. ``_serialization_header.uuid``) becomes nested
    JSON (``{"_serialization_header": {"uuid": value}}``).  This keeps a
    demeter dot-path aligned 1:1 with the table structure.
    """
    parts = dotted_key.split(".")
    target = node
    for part in parts[:-1]:
        nxt = target.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            target[part] = nxt
        target = nxt
    target[parts[-1]] = value


class DebugScannerBase(GDBFrameController):
    """
    Base class for the "scan pattern".

    A scanner captures a debug struct **by value** into a gdb convenience
    variable, then presents/advances through it.  Subclasses configure behavior
    via class attributes:

    Class attributes (override in subclass):
        SCANNER_VAR       — gdb convenience variable name (e.g. "$debug_ui_scanner")
        _FUNC_PTR_TYPE    — type name for cast-and-call of function pointers
        _GET_SCANNER_EXPR — gdb expression that returns the struct by value
                             (e.g. "debug_get_ui_scanner(&game)")
        _TOP_LEVEL_FIELDS — tuple of the C struct's top-level field names, each
                             a dotted path usable as a gdb member expression
                             (e.g. ("p_ui_context", "m_next_element"))

    Hooks:
        _enrich_table(table) — mutate the freshly built top-level table to add
                             nested mappings.  Default is a no-op (flat table).

    All frame-dependent methods wrap their work in push_main_frame() /
    pop_frame() so the caller's frame context is restored even on error.
    """

    SCANNER_VAR: str = ""
    _FUNC_PTR_TYPE: str = ""
    _GET_SCANNER_EXPR: str = ""
    _TOP_LEVEL_FIELDS: tuple[str, ...] = ()

    def __init__(self, gdbmi) -> None:
        super().__init__(gdbmi)
        self._table_cache: dict | None = None

    # -- capture ------------------------------------------------------------ #

    def get_scanner(self) -> str | None:
        """Capture the scanner struct by value.

        Executes (in the main frame)::
            set $SCANNER_VAR = _GET_SCANNER_EXPR

        Returns the captured struct's printed representation, or None on
        failure.  Call this once before reading the table.
        """
        self._table_cache = None  # a fresh capture invalidates any stale table
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = {self._GET_SCANNER_EXPR}"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)

    # -- table (the single source of truth) --------------------------------- #

    def get_table(self) -> dict:
        """Return the nested, JSON-parsable snapshot of the scanner state.

        Builds the table once (reading each top-level field via gdb, then
        invoking the ``_enrich_table`` hook) and caches it.  Repeated calls —
        including from :meth:`get_field` and :meth:`find_demeters` — return the
        same cached object without re-querying gdb.  The cache is invalidated
        by :meth:`get_scanner` and :meth:`_advance`.

        Returns a dict whose leaves are gdb-printed value strings and whose
        internal nodes are dicts (see the Liskov contract in the module doc).
        Must be called after :meth:`get_scanner`.
        """
        if self._table_cache is None:
            table = self._build_top_level_table()
            self._enrich_table(table)
            self._table_cache = table
        return self._table_cache

    def _enrich_table(self, table: dict) -> None:
        """Hook: mutate *table* to add nested mappings.  Default: no-op.

        Subtypes that iterate a manager structure (e.g. UI managers → elements)
        override this to attach nested dicts.  The mutation happens in place;
        the returned value is ignored.
        """

    def get_fields(self) -> list[str]:
        """Return the top-level field names the table exposes.

        These are the keys of :meth:`get_table` and therefore the valid
        top-level demeters.  Nested demeters are discovered with
        :meth:`find_demeters`.
        """
        return list(self.get_table().keys())

    def get_field(self, demeter: str) -> Any:
        """Return the value at dot-path *demeter* in the table.

        Applies the law of demeter to the JSON object returned by
        :meth:`get_table`: each dot in *demeter* steps exactly one level into
        the nested structure.  e.g.::

            get_field("p_ui_context")
            get_field("ui_managers.0.ui_elements.1._serialization_header.uuid")

        Returns a JSON value (a `str` for a leaf gdb value, a `dict` for a
        nested node).  Raises :class:`KeyError` if *demeter* does not resolve.
        """
        node: Any = self.get_table()
        walked = ""
        for part in demeter.split("."):
            walked = f"{walked}.{part}" if walked else part
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                raise KeyError(
                    f"demeter {demeter!r} not found; stopped at {walked!r} "
                    f"(value is {type(node).__name__}, not a mapping with {part!r})"
                )
        return node

    def find_demeters(self, substring: str) -> list[str]:
        """Return every demeter (dot-path) whose **key** contains *substring*.

        Greps the :meth:`get_table` JSON across all levels and returns the
        valid dot-paths that point at matching keys.  e.g.
        ``find_demeters("uuid")`` yields every ``...uuid`` path in the table.
        Ordering is deterministic (document order of the dicts).
        """
        found: list[str] = []

        def walk(node: Any, prefix: str) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    key = str(key)
                    path = f"{prefix}.{key}" if prefix else key
                    if substring in key:
                        found.append(path)
                    walk(value, path)

        walk(self.get_table(), "")
        return found

    # -- gdb read helpers (frame-independent) ------------------------------- #

    def _read_struct_field(self, field: str) -> str | None:
        """Read a single top-level field value of the captured struct."""
        return self._eval(f"{self.SCANNER_VAR}.{field}")

    def _read_struct(self, expr: str, fields) -> dict:
        """Read ``expr.<f>`` for each *f* into a (possibly nested) dict.

        *fields* may contain dotted member paths (e.g.
        ``"_serialization_header.uuid"``); those are stored as nested JSON via
        :func:`_set_path` so a demeter dot-path lines up with the table.
        """
        out: dict = {}
        for field in fields:
            _set_path(out, field, self._eval(f"{expr}.{field}"))
        return out

    def _build_top_level_table(self) -> dict:
        """Build the top-level field table. Default reads each field with one
        ``-data-evaluate-expression`` (one round-trip per field). Subclasses
        whose fields are type-groupable may override this to read several
        fields per round-trip (e.g. ``DebugUIScanner`` batches them into
        console brace-lists). The returned dict has one key per top-level
        field (same shape as :meth:`_read_struct`).
        """
        return self._read_struct(self.SCANNER_VAR, self._TOP_LEVEL_FIELDS)

    def _parse_value_array(self, text: str) -> list:
        """Parse a console ``$N = {v1, v2, ...}`` value array into a list.

        Splits on top-level commas (respecting nested braces). Returns a list
        of raw value strings. If no brace array is found, returns a single
        element list holding the (``$N = ``-stripped) value, so callers can
        treat both forms uniformly.
        """
        text = text or ""
        m = re.search(r"=\s*\{(.*)\}\s*$", text, re.DOTALL)
        if not m:
            stripped = text.strip()
            if "=" in stripped:
                stripped = stripped.split("=", 1)[1].strip()
            return [stripped] if stripped else []
        parts: list[str] = []
        depth = 0
        cur = ""
        for ch in m.group(1):
            if ch == "{":
                depth += 1
                cur += ch
            elif ch == "}":
                depth -= 1
                cur += ch
            elif ch == "," and depth == 0:
                parts.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur.strip())
        return parts

    @staticmethod
    def _is_null(value: str | None) -> bool:
        """True if a gdb-printed value represents a null pointer / 0."""
        if value is None:
            return True
        text = value.strip()
        if not text:
            return True
        return bool(_NULL_RE.match(text))

    @staticmethod
    def _is_truthy(value: str | None) -> bool:
        """True if a gdb-printed value is a truthy integer/bool (``1``/``true``)."""
        if value is None:
            return False
        text = value.strip().lstrip("0x")
        if text.lower() in ("1", "true"):
            return True
        try:
            return int(text, 0) != 0
        except ValueError:
            return False

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        """Parse a gdb-printed integer (hex or decimal); None if not numeric."""
        if value is None:
            return None
        text = value.strip()
        if not text:
            return None
        try:
            return int(text, 0)
        except ValueError:
            # tolerate values with trailing decorations like "<name>"
            m = re.match(r"^(0x[0-9a-fA-F]+|\d+)", text)
            return int(m.group(1), 0) if m else None

    def table_json(self) -> str:
        """Serialize the table to a JSON string (proves the Liskov invariant)."""
        return json.dumps(self.get_table(), indent=2, sort_keys=False)

    # -- advance ------------------------------------------------------------- #

    def _advance(self, field: str) -> str | None:
        """Advance the scanner via a function-pointer field.

        gdb cannot call a function pointer stored inside a convenience
        variable.  We work around this by casting the pointer to its named
        type before calling, producing a standalone call expression::

            set $SCANNER_VAR = ((FuncType)$SCANNER_VAR.<field>)()

        Advancing mutates the scanner state, so the cached table is invalidated.
        """
        self._table_cache = None  # state changed; the next table must be rebuilt
        self.push_main_frame()
        try:
            self._exec(
                f"set {self.SCANNER_VAR} = "
                f"(({self._FUNC_PTR_TYPE}){self.SCANNER_VAR}.{field})()"
            )
        finally:
            self.pop_frame()
        return self._eval(self.SCANNER_VAR)
