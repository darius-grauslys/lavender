"""
Base selection tool (spec section 1.1 — Selection Tool).

Each mode's select tool inherits from this and defines
what constitutes a valid selection.

Default keybind overrides when active:
- Ctrl+C: copy selection
- Ctrl+V: paste selection
- Arrow keys: move selection by 1 tile
- Scroll wheel (no modifier): vertical pan
- Shift + Scroll wheel: horizontal pan
- Alt + Scroll wheel: zoom in/out
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tools.tool import Tool
from keybinds.keybind import (
    KeyCombo, KeybindCallback, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

# GLFW key constants (stable values, avoids hard import).
_KEY_UP = 265
_KEY_DOWN = 264
_KEY_LEFT = 263
_KEY_RIGHT = 262
_KEY_C = 67
_KEY_V = 86


class SelectTool(Tool):
    """Base selection tool with multi-select and copy/paste."""

    name = "Select"
    icon_label = "S"

    def __init__(self, movement: Optional[WorkspaceMovement] = None):
        self._selection: List[Any] = []
        self._clipboard: Optional[Any] = None
        self._is_active: bool = False
        self._movement: Optional[WorkspaceMovement] = movement

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject the workspace movement controller."""
        self._movement = movement

    # ------------------------------------------------------------------
    # Keybind construction
    # ------------------------------------------------------------------

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        """Return keybind overrides for the select tool.

        Provides:
        - Ctrl+C / Ctrl+V for copy/paste
        - Arrow keys to move selection (stub — subclasses refine)
        - Scroll / shift-scroll / alt-scroll for pan and zoom
        """
        binds: Dict[KeyCombo, KeybindCallback] = {
            KeyCombo(_KEY_C, Modifier.CTRL): lambda: self.copy(),
            KeyCombo(_KEY_V, Modifier.CTRL): lambda: self.paste(),
        }

        if self._movement is not None:
            m = self._movement
            # Arrow keys — move selection by 1 tile
            binds[KeyCombo(_KEY_UP, Modifier.NONE)] = \
                m.make_pan_tile_up()
            binds[KeyCombo(_KEY_DOWN, Modifier.NONE)] = \
                m.make_pan_tile_down()
            binds[KeyCombo(_KEY_LEFT, Modifier.NONE)] = \
                m.make_pan_tile_left()
            binds[KeyCombo(_KEY_RIGHT, Modifier.NONE)] = \
                m.make_pan_tile_right()
            # Scroll — vertical pan
            binds[KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE)] = \
                m.make_scroll_up()
            binds[KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.NONE)] = \
                m.make_scroll_down()
            # Shift + scroll — horizontal pan
            binds[KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.SHIFT)] = \
                m.make_scroll_left()
            binds[KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.SHIFT)] = \
                m.make_scroll_right()
            # Alt + scroll — zoom
            binds[KeyCombo(VIRTUAL_KEY_ZOOM_IN, Modifier.ALT)] = \
                m.make_zoom_in()
            binds[KeyCombo(VIRTUAL_KEY_ZOOM_OUT, Modifier.ALT)] = \
                m.make_zoom_out()

        return binds

    # ------------------------------------------------------------------
    # Activation / deactivation
    # ------------------------------------------------------------------

    def on_activate(self, keybind_manager: KeybindManager) -> None:
        """Push select keybind overrides."""
        super().on_activate(keybind_manager)
        self._is_active = True
        keybind_manager.push_override(self._build_keybinds())

    def on_deactivate(self, keybind_manager=None) -> None:
        """Pop select keybind overrides."""
        self._is_active = False
        if keybind_manager is not None:
            keybind_manager.pop_override()

    @property
    def selection(self) -> List[Any]:
        return self._selection

    def clear_selection(self) -> None:
        self._selection.clear()

    def select(self, obj: Any) -> None:
        """Add an object to the selection."""
        if obj not in self._selection:
            self._selection.append(obj)

    def deselect(self, obj: Any) -> None:
        if obj in self._selection:
            self._selection.remove(obj)

    def copy(self) -> None:
        """Copy the first selected element to clipboard."""
        if self._selection:
            self._clipboard = self._selection[0]

    def paste(self) -> Optional[Any]:
        """Return the clipboard contents for pasting."""
        return self._clipboard
