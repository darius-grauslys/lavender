"""
debug_scanner_input.py — Input scanner (debug_input.h) with batched GDB calls.

Wraps ``debug_get_input_scanner(&game)``, which returns a DEBUG_Input_Scanner
by value.  The scanner is captured by value into the gdb convenience variable
``$debug_input_scanner`` and its state is presented as a flat JSON table of
the current input state (flags + mouse position/delta).

Unlike the entity, scene, and UI scanners, the input scanner does **not**
iterate over a collection — it reads a single snapshot of the Input state.
Therefore ``_enrich_table`` is a no-op (the default from DebugScannerBase
applies), and the top-level fields are the entire table.

Field layout (see ``core/include/debug/debug_input.h``)::

    typedef struct DEBUG_Input_Scanner_t {
        Input           *p_input;
        u32              current_flags;        // Input_Flags__u32 bitmask
        u32              pressed_flags;        // newly pressed this frame
        Vector__3i32     mouse_pos;
        Vector__3i32     mouse_delta;
        m_DEBUG_Input_Scanner_Func m_refresh;
    } DEBUG_Input_Scanner;

``current_flags`` mirrors the ``INPUT_*`` macros in ``platform_defaults.h``
(and the ``Input_Flags__u32`` enum in ``lavender_debug.py``).
"""

from __future__ import annotations

from .debug_scanner import DebugScannerBase


# Field layout of DEBUG_Input_Scanner (see core/include/debug/debug_input.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_INPUT_SCANNER_FIELDS = (
    "p_input",
    "current_flags",
    "pressed_flags",
    "mouse_pos",
    "mouse_delta",
    "m_refresh",
)


class DebugInputScanner(DebugScannerBase):
    """Input scanner — reads the current Input state via ``debug_get_input_scanner``.

    Typical usage (game halted under gdb)::

        ex = DebugInputScanner(gdbmi)
        ex.get_scanner()
        ex.get_table()      # flat table — no enrichment needed

    The table is a snapshot of the *current* input state.  It is **not**
    historical — each ``get_scanner()`` call recaptures from the live target.
    """

    SCANNER_VAR = "$debug_input_scanner"
    _FUNC_PTR_TYPE = "m_DEBUG_Input_Scanner_Func"
    _GET_SCANNER_EXPR = "debug_get_input_scanner(&game)"
    _TOP_LEVEL_FIELDS = DEBUG_INPUT_SCANNER_FIELDS

    # No _enrich_table override — the input scanner has no nested iteration.
    # The base class no-op is correct here.
