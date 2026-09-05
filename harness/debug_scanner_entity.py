"""
debug_scanner_entity.py — Entity scanner explorer (debug_entity.h).

Wraps debug_get_entity_scanner(&game), which returns a DEBUG_Entity_Scanner
by value.  The scanner is captured by value into the gdb convenience variable
``$debug_entity_scanner`` and fields are read with ``.`` member access.

Field layout (see core/include/debug/debug_entity.h):

    typedef struct DEBUG_Entity_Scanner_t {
        Entity_Manager *p_entity_manager;
        Entity *p_entity__current;
        m_DEBUG_Entity_Scanner_Func m_next_entity;
    } DEBUG_Entity_Scanner;

Note: debug_entity.h is guarded by ``#ifndef NDEBUG``; the symbols are absent
in release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

from .debug_scanner import DebugScannerBase


# Field layout of DEBUG_Entity_Scanner (see core/include/debug/debug_entity.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_ENTITY_SCANNER_FIELDS = (
    "p_entity_manager",
    "p_entity__current",
    "m_next_entity",
)


class DebugEntityScanner(DebugScannerBase):
    """
    Inspects entity state through debug_entity.h's ``debug_get_entity_scanner``.

    Typical usage (game halted under gdb)::

        ex = DebugEntityScanner(gdbmi)
        ex.get_scanner()                       # captures $debug_entity_scanner
        ex.get_table()                         # nested JSON of scanner state
        ex.get_field("p_entity_manager")       # value at a top-level demeter
        ex.next_entity()                       # advance via m_next_entity
    """

    SCANNER_VAR = "$debug_entity_scanner"

    # m_DEBUG_Entity_Scanner_Func, the type of m_next_entity.
    # Used to cast-and-call the function pointer (see _advance).
    _FUNC_PTR_TYPE = "m_DEBUG_Entity_Scanner_Func"

    # debug_get_entity_scanner(&game) returns the struct by value.
    _GET_SCANNER_EXPR = "debug_get_entity_scanner(&game)"

    # Mirror of DEBUG_Entity_Scanner fields (debug_entity.h).
    _TOP_LEVEL_FIELDS = DEBUG_ENTITY_SCANNER_FIELDS

    def next_entity(self) -> str | None:
        """Advance the scanner via ``m_next_entity``."""
        return self._advance("m_next_entity")
