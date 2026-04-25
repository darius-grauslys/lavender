"""
Chunk Edit mode (spec section 1.1.2).

Activation shortcut: Ctrl+K
"""

from __future__ import annotations

from modes.editor_mode import EditorMode
from tools.select_tool import SelectTool
from tools.pan_tool import PanTool
from tools.tool import Tool
from core.c_enum import CEnum

import imgui
from typing import List, Optional


class TileSelectTool(SelectTool):
    name = "Tile Select"
    icon_label = "TS"


class ChunkPanTool(PanTool):
    name = "Chunk Pan"
    icon_label = "CP"


class TileDrawTool(Tool):
    """Tile draw tool with tile palette (spec section 1.1.2.1.3)."""

    name = "Tile Draw"
    icon_label = "TD"

    def __init__(self):
        self._tile_enums: List[CEnum] = []
        self._selected_layer: int = 0
        self._selected_tile_value: int = 0

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        """Set the available tile enums (one per layer)."""
        self._tile_enums = enums

    def draw_properties(self) -> None:
        if not self._tile_enums:
            imgui.text("No tile types loaded.")
            return

        # Layer selector
        layer_names = [e.name for e in self._tile_enums]
        _, self._selected_layer = imgui.combo(
            "Layer", self._selected_layer, layer_names)

        if self._selected_layer >= len(self._tile_enums):
            return

        enum = self._tile_enums[self._selected_layer]

        # 5-wide scrollable grid of tiles
        imgui.text(f"Tiles ({enum.name}):")
        imgui.begin_child("##tile_palette", 0, 200, border=True)
        col = 0
        for member in enum.members:
            is_selected = member.value == self._selected_tile_value
            if is_selected:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)

            if imgui.button(f"{member.name}##{member.value}", width=120, height=24):
                self._selected_tile_value = member.value

            if is_selected:
                imgui.pop_style_color()

            col += 1
            if col < 5:
                imgui.same_line()
            else:
                col = 0
        imgui.end_child()

    @property
    def selected_tile_value(self) -> int:
        return self._selected_tile_value

    @property
    def selected_layer(self) -> int:
        return self._selected_layer


class ChunkEditMode(EditorMode):
    name = "Chunk Edit"
    shortcut_label = "Ctrl+K"

    def __init__(self, keybind_manager):
        super().__init__(keybind_manager)
        self._tile_draw = TileDrawTool()
        self._tools = [
            TileSelectTool(),
            ChunkPanTool(),
            self._tile_draw,
        ]

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        self._tile_draw.set_tile_enums(enums)
