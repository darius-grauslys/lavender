"""
Global_Space View mode (spec section 1.1.1).

Activation shortcut: Ctrl+G
"""

from __future__ import annotations

from ..modes.editor_mode import EditorMode
from ..tools.select_tool import SelectTool
from ..tools.pan_tool import PanTool
from ..tools.tool import Tool

import imgui


class GlobalSpaceSelectTool(SelectTool):
    name = "Global_Space Select"
    icon_label = "GS"


class GlobalSpacePanTool(PanTool):
    name = "Global_Space Pan"
    icon_label = "GP"


class GoToTool(Tool):
    """Go-To tool: prompts for X, Y, Z and moves workspace."""

    name = "Go-To"
    icon_label = "GT"

    def __init__(self):
        self._goto_x: int = 0
        self._goto_y: int = 0
        self._goto_z: int = 0
        self._show_prompt: bool = False

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
            # workspace movement will read these coords
        imgui.same_line()
        if imgui.button("Cancel##goto"):
            self._show_prompt = False

    @property
    def target_coords(self):
        return (self._goto_x, self._goto_y, self._goto_z)


class GlobalSpaceViewMode(EditorMode):
    name = "Global_Space View"
    shortcut_label = "Ctrl+G"

    def __init__(self, keybind_manager):
        super().__init__(keybind_manager)
        self._tools = [
            GlobalSpaceSelectTool(),
            GlobalSpacePanTool(),
            GoToTool(),
        ]
