"""
debug_input_driver.py — Drive the in-game Input through gdb.

Mirrors every signature in core/include/debug/drive_input.h (plus
``debug_drop_input__flag`` from drive_input.c, which isn't declared in the
header but is the natural companion to ``debug_drive_input__flag``).

Each helper:
  1. pushes the "main" (innermost) frame via push_main_frame(),
  2. resolves &game as the Game *p_game argument,
  3. issues the corresponding ``call ...`` through gdb,
  4. pops back to the caller's frame via pop_frame().

Vector__3i32 args are passed as C compound literals, e.g.
(Vector__3i32){10, 20, 5} (a bare brace initializer isn't valid as a C
function argument).
"""

from __future__ import annotations

from .gdb_frame_controller import GDBFrameController
from .lavender_debug import (
    Input_Flags__u32,
    _extract_call_value,
    _vector__3i32_literal,
)


class DebugInputDriver(GDBFrameController):
    """
    Drives the in-game Input through gdb by invoking the debug_drive_*
    functions declared in drive_input.h.
    """

    # -- per-signature helpers (drive_input.h) ------------------------------ #

    def drive_input__flag(self, input_flag: Input_Flags__u32) -> None:
        """debug_drive_input__flag(&game, input_flag)"""
        self.push_main_frame()
        try:
            self._call(
                f"debug_drive_input__flag(&game, {int(input_flag)})"
            )
        finally:
            self.pop_frame()

    def drop_input__flag(self, input_flag: Input_Flags__u32) -> None:
        """debug_drop_input__flag(&game, input_flag)

        Clears a flag. Implemented in drive_input.c though not declared in
        drive_input.h; provided here so input can be toggled off again.
        """
        self.push_main_frame()
        try:
            self._call(
                f"debug_drop_input__flag(&game, {int(input_flag)})"
            )
        finally:
            self.pop_frame()

    def drive_input__mouse_pos(self, x: int, y: int, z: int = 0) -> None:
        """debug_drive_input__mouse_pos(&game, (Vector__3i32){x, y, z})"""
        self.push_main_frame()
        try:
            vec = _vector__3i32_literal(x, y, z)
            self._call(
                f"debug_drive_input__mouse_pos(&game, {vec})"
            )
        finally:
            self.pop_frame()

    def dispatch_click(self, x: int, y: int, z: int = 0) -> str | None:
        """debug_dispatch_click(&game, (Vector__3i32){x, y, z}) -> Process *

        Returns the hex address of the spawned Process * (e.g. ``0x5555...``)
        or ``None`` if it could not be extracted.  The address lets you set a
        breakpoint on the spawned ``m_debug_process__click``; the documented
        workflow is to breakpoint ``complete_process()`` instead.

        With the ``call`` CLI form the return value only appears in the
        console stream (``$N = (Process *) 0x...``), so it is parsed out here.
        """
        self.push_main_frame()
        try:
            vec = _vector__3i32_literal(x, y, z)
            resp = self._call(
                f"debug_dispatch_click(&game, {vec})"
            )
            return _extract_call_value(resp)
        finally:
            self.pop_frame()
