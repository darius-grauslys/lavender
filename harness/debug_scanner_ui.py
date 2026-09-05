"""
debug_scanner_ui.py — UI scanner (debug_ui.h).

Wraps debug_get_ui_scanner(&game), which returns a DEBUG_UI_Scanner by value.
The scanner is captured by value into the gdb convenience variable
``$debug_ui_scanner`` and its state is presented as a nested JSON table.

Field layout (see core/include/debug/debug_ui.h):

    typedef struct DEBUG_UI_Scanner_t {
        UI_Context     *p_ui_context;
        UI_Manager     *p_ui_manager__current;
        UI_Element    **p_ptr_ui_element__current;
        m_DEBUG_UI_Scanner_Func m_next_manager;
        m_DEBUG_UI_Scanner_Func m_next_element;
    } DEBUG_UI_Scanner;

This is the "iterating manager" scanner: the UI context owns a *by-value*
array of UI_Mangers, and each manager owns a *pointer* array of UI_Elements.
``get_table()`` therefore maps **by ui_manager**, then **sub-maps each
ui_manager to each ui_element**::

    {
      "p_ui_context": "0x...",
      "p_ui_manager__current": "0x...",
      "p_ptr_ui_element__current": "0x...",
      "m_next_manager": "0x... <adv_manager>",
      "m_next_element": "0x... <adv_element>",
      "ui_managers": {
        "0": {
          "_serialization_header": {"uuid": "0x..."},
          "pM_ptr_array_of__ui_elements": "0x...",
          "max_quantity_of__ui_elements": "128",
          "ui_elements": {
            "0": {"_serialization_header": {"uuid": "0x..."}, ...},
            "1": {"_serialization_header": {"uuid": "0x..."}, ...}
          }
        },
        "2": {...}
      }
    }

The scanner only *presents* the gdb state as JSON; it does not interpret it.
This nested shape is what makes later UUID-by-UUID lookups (see TODOS.md, item
3) possible via ``find_demeters("uuid")`` / ``get_field("...uuid")``.

Note: debug_ui.h is guarded by ``#ifndef NDEBUG``; the symbols are absent in
release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

from .debug_scanner import DebugScannerBase


# Field layout of DEBUG_UI_Scanner (see core/include/debug/debug_ui.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_UI_SCANNER_FIELDS = (
    "p_ui_context",
    "p_ui_manager__current",
    "p_ptr_ui_element__current",
    "m_next_manager",
    "m_next_element",
)

# Fields we present for each UI_Manager (see UI_Manager_t in defines.h).
# "_serialization_header.uuid" is a chained member; it is stored as nested JSON
# so the demeter path "ui_managers.<i>._serialization_header.uuid" resolves.
UI_MANAGER_FIELDS = (
    "_serialization_header.uuid",
    "pM_ui_element_pool",
    "pM_ptr_array_of__ui_elements",
    "p_ui_element__focused",
    "max_quantity_of__ui_elements",
    "ui_manager_flags__u8",
)

# Fields we present for each UI_Element (see UI_Element_t in defines.h).
UI_ELEMENT_FIELDS = (
    "_serialization_header.uuid",
    "p_parent",
    "p_child",
    "p_next",
    "ui_flags",
    "the_kind_of_ui_element__this_is",
)

# Sentinel for a deallocated serialization header (defines.h):
#   #define IDENTIFIER__UNKNOWN__u32 (uint32_t)(-1)
_IDENT_UNKNOWN__U32 = "(Identifier__u32)-1"


class DebugUIScanner(DebugScannerBase):
    """
    Inspects UI state through debug_ui.h's ``debug_get_ui_scanner``.

    Typical usage (game halted under gdb, e.g. in the render loop)::

        ex = DebugUIScanner(gdbmi)
        ex.get_scanner()                      # captures $debug_ui_scanner
        ex.get_table()                        # nested JSON of the whole UI state
        ex.get_fields()                       # top-level field names
        ex.get_field("ui_managers.0.pM_ptr_array_of__ui_elements")
        ex.find_demeters("uuid")              # every "...uuid" demeter
        ex.next_element()                     # advance via m_next_element
        ex.next_manager()                     # advance via m_next_manager

    The scanner is captured by value into the gdb convenience variable
    ``$debug_ui_scanner`` (debug_get_ui_scanner returns a struct).  ``get_table``
    reads it with ``-data-evaluate-expression`` (``_eval``), the reliable way to
    get a value back as JSON.
    """

    SCANNER_VAR = "$debug_ui_scanner"

    # m_DEBUG_UI_Scanner_Func, the type of m_next_manager / m_next_element.
    # Used to cast-and-call the function pointer (see _advance).
    _FUNC_PTR_TYPE = "m_DEBUG_UI_Scanner_Func"

    # debug_get_ui_scanner(&game) returns the struct by value.
    _GET_SCANNER_EXPR = "debug_get_ui_scanner(&game)"

    # Mirror of DEBUG_UI_Scanner fields (debug_ui.h).
    _TOP_LEVEL_FIELDS = DEBUG_UI_SCANNER_FIELDS

    # UI_Context.ui_managers is a by-value array of this size (defines.h:
    #   #define MAX_QUANTITY_OF__UI_MANAGERS 8).
    MAX_QUANTITY_OF__UI_MANAGERS = 8

    # -- enrichment: ui_managers -> ui_elements ---------------------------- #

    def _enrich_table(self, table: dict) -> None:
        """Attach the ``ui_managers`` nested map to the top-level table.

        Each present (allocated) manager is keyed by its index into
        ``p_ui_context->ui_managers`` and sub-maps its ``ui_elements`` (keyed
        by index into the manager's ``pM_ptr_array_of__ui_elements``).
        """
        table["ui_managers"] = self._scan_managers(table)

    def _scan_managers(self, table: dict) -> dict:
        ctx = f"{self.SCANNER_VAR}.p_ui_context"
        if self._is_null(table.get("p_ui_context")):
            return {}
        managers: dict = {}
        for i in range(self.MAX_QUANTITY_OF__UI_MANAGERS):
            mgr_expr = f"{ctx}->ui_managers[{i}]"
            allocated = self._eval(
                f"{mgr_expr}._serialization_header.uuid != {_IDENT_UNKNOWN__U32}"
            )
            if not self._is_truthy(allocated):
                continue
            managers[str(i)] = self._scan_manager(mgr_expr)
        return managers

    def _scan_manager(self, mgr_expr: str) -> dict:
        mgr = self._read_struct(mgr_expr, UI_MANAGER_FIELDS)
        mgr["ui_elements"] = self._scan_elements(mgr_expr, mgr)
        return mgr

    def _scan_elements(self, mgr_expr: str, mgr: dict) -> dict:
        max_qty = self._to_int(mgr.get("max_quantity_of__ui_elements"))
        if max_qty is None or max_qty <= 0:
            return {}
        elements: dict = {}
        for j in range(max_qty):
            el_expr = f"{mgr_expr}.pM_ptr_array_of__ui_elements[{j}]"
            if self._is_null(self._eval(el_expr)):
                continue
            elements[str(j)] = self._read_struct(el_expr, UI_ELEMENT_FIELDS)
        return elements

    # -- advancement -------------------------------------------------------- #

    def next_element(self) -> str | None:
        """Advance the scanner via ``m_next_element``."""
        return self._advance("m_next_element")

    def next_manager(self) -> str | None:
        """Advance the scanner via ``m_next_manager``."""
        return self._advance("m_next_manager")
