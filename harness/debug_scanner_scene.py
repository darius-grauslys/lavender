"""
debug_scanner_scene.py — Scene scanner explorer (debug_scene.h).

Wraps debug_get_scene_scanner(&game), which returns a DEBUG_Scene_Scanner by
value.  The scanner is captured by value into the gdb convenience variable
``$debug_scene_scanner`` and fields are read with ``.`` member access.

Field layout (see core/include/debug/debug_scene.h):

    typedef struct DEBUG_Scene_Scanner_t {
        Scene_Manager *p_scene_manager;
        Scene *p_scene__running;
        Scene *p_scene__current_in__scan;
        m_DEBUG_Scene_Scanner_Func m_iterate_scene;
        m_DEBUG_Scene_Scanner_Func m_go_to__scene;
    } DEBUG_Scene_Scanner;

Note: debug_scene.h is guarded by ``#ifndef NDEBUG``; the symbols are absent
in release builds, in which case these calls will error at the gdb prompt.
"""

from __future__ import annotations

from .debug_scanner import DebugScannerBase


# Field layout of DEBUG_Scene_Scanner (see core/include/debug/debug_scene.h).
# Module-level so external callers and tests can reference it directly.
DEBUG_SCENE_SCANNER_FIELDS = (
    "p_scene_manager",
    "p_scene__running",
    "p_scene__current_in__scan",
    "m_iterate_scene",
    "m_go_to__scene",
)


class DebugSceneScanner(DebugScannerBase):
    """
    Inspects scene state through debug_scene.h's ``debug_get_scene_scanner``.

    Typical usage (game halted under gdb)::

        ex = DebugSceneScanner(gdbmi)
        ex.get_scanner()                       # captures $debug_scene_scanner
        ex.get_table()                         # nested JSON of scanner state
        ex.get_field("p_scene__running")       # value at a top-level demeter
        ex.iterate_scene()                     # advance via m_iterate_scene
        ex.go_to__scene()                      # trigger via m_go_to__scene
    """

    SCANNER_VAR = "$debug_scene_scanner"

    # m_DEBUG_Scene_Scanner_Func, the type of m_iterate_scene / m_go_to__scene.
    # Used to cast-and-call the function pointer (see _advance).
    _FUNC_PTR_TYPE = "m_DEBUG_Scene_Scanner_Func"

    # debug_get_scene_scanner(&game) returns the struct by value.
    _GET_SCANNER_EXPR = "debug_get_scene_scanner(&game)"

    # Mirror of DEBUG_Scene_Scanner fields (debug_scene.h).
    _TOP_LEVEL_FIELDS = DEBUG_SCENE_SCANNER_FIELDS

    def iterate_scene(self) -> str | None:
        """Advance the scanner via ``m_iterate_scene``."""
        return self._advance("m_iterate_scene")

    def go_to__scene(self) -> str | None:
        """Trigger a scene transition via ``m_go_to__scene``."""
        return self._advance("m_go_to__scene")
