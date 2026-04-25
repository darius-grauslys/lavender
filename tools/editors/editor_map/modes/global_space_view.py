"""
Global_Space View mode (spec section 1.1.1).

Activation shortcut: Ctrl+G

Tool keybind behaviour:
- Global_Space Select:
    Arrow keys → move selection by 1 tile
    Shift+Up / Shift+Down → move Z axis
    Ctrl+C / Ctrl+V → copy / paste global space
- Global_Space Pan:
    Arrow keys → move by 1 tile
    Shift+Arrow keys → move by 1 global space
    Ctrl+Up / Ctrl+Down → move along Z axis
    Scroll wheel → vertical pan
    Shift+Scroll → horizontal pan
    Alt+Shift+Scroll → zoom
"""

from __future__ import annotations

from typing import Dict, Optional

from modes.editor_mode import EditorMode
from tools.select_tool import SelectTool
from tools.pan_tool import PanTool
from tools.tool import Tool
from keybinds.keybind import (
    KeyCombo, KeybindCallback, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

import imgui

# GLFW key constants (stable values).
_KEY_UP = 265
_KEY_DOWN = 264
_KEY_LEFT = 263
_KEY_RIGHT = 262


class GlobalSpaceSelectTool(SelectTool):
    """Selection tool for Global Spaces.

    Overrides Shift+Up/Down to move Z axis.
    """
    name = "Global_Space Select"
    icon_label = "GS"

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        binds = super()._build_keybinds()
        if self._movement is not None:
            m = self._movement
            binds[KeyCombo(_KEY_UP, Modifier.SHIFT)] = m.make_move_z_up()
            binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)] = \
                m.make_move_z_down()
        return binds


class GlobalSpacePanTool(PanTool):
    """Pan tool for Global Space View.

    Shift+Arrow keys move by whole global spaces.
    """
    name = "Global_Space Pan"
    icon_label = "GP"

    def __init__(
            self,
            movement: Optional[WorkspaceMovement] = None,
            gs_width: int = 8,
            gs_height: int = 8):
        super().__init__(movement)
        self._gs_width = gs_width
        self._gs_height = gs_height

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        binds = super()._build_keybinds()
        if self._movement is not None:
            m = self._movement
            binds[KeyCombo(_KEY_UP, Modifier.SHIFT)] = \
                m.make_pan_global_space_up(
                    self._gs_width, self._gs_height)
            binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)] = \
                m.make_pan_global_space_down(
                    self._gs_width, self._gs_height)
            binds[KeyCombo(_KEY_LEFT, Modifier.SHIFT)] = \
                m.make_pan_global_space_left(
                    self._gs_width, self._gs_height)
            binds[KeyCombo(_KEY_RIGHT, Modifier.SHIFT)] = \
                m.make_pan_global_space_right(
                    self._gs_width, self._gs_height)
        return binds


class GoToTool(Tool):
    """Go-To tool: prompts for X, Y, Z and moves workspace."""

    name = "Go-To"
    icon_label = "GT"

    def __init__(self, movement: Optional[WorkspaceMovement] = None):
        self._goto_x: int = 0
        self._goto_y: int = 0
        self._goto_z: int = 0
        self._show_prompt: bool = False
        self._movement: Optional[WorkspaceMovement] = movement

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject the workspace movement controller."""
        self._movement = movement

    def on_activate(self, keybind_manager) -> None:
        super().on_activate(keybind_manager)
        self._show_prompt = True

    def draw_properties(self) -> None:
        if not self._show_prompt:
            return
        imgui.text("Go To Chunk Coordinates:")
        _, self._goto_x = imgui.input_int("X##goto", self._goto_x)
        _, self._goto_y = imgui.input_int("Y##goto", self._goto_y)
        _, self._goto_z = imgui.input_int("Z##goto", self._goto_z)
        if imgui.button("OK##goto"):
            self._show_prompt = False
            if self._movement is not None:
                self._movement.go_to(
                    self._goto_x, self._goto_y, self._goto_z)
        imgui.same_line()
        if imgui.button("Cancel##goto"):
            self._show_prompt = False

    @property
    def target_coords(self):
        return (self._goto_x, self._goto_y, self._goto_z)


class GlobalSpaceViewMode(EditorMode):
    name = "Global_Space View"
    shortcut_label = "Ctrl+G"

    def __init__(
            self,
            keybind_manager: KeybindManager,
            movement: Optional[WorkspaceMovement] = None,
            gs_width: int = 8,
            gs_height: int = 8):
        super().__init__(keybind_manager)
        self._movement = movement
        self._gs_select = GlobalSpaceSelectTool(movement)
        self._gs_pan = GlobalSpacePanTool(movement, gs_width, gs_height)
        self._goto = GoToTool(movement)
        self._tools = [self._gs_select, self._gs_pan, self._goto]

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject movement into all tools."""
        self._movement = movement
        self._gs_select.set_movement(movement)
        self._gs_pan.set_movement(movement)
        self._goto.set_movement(movement)
