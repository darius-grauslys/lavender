"""
Entity Edit mode (spec section 1.1.3).

Activation shortcut: Ctrl+E
"""

from __future__ import annotations

from modes.editor_mode import EditorMode
from tools.select_tool import SelectTool
from tools.pan_tool import PanTool
from tools.tool import Tool

import imgui


class EntitySelectTool(SelectTool):
    name = "Entity Select"
    icon_label = "ES"


class EntityPanTool(PanTool):
    name = "Entity Pan"
    icon_label = "EP"


class CreateEntityTool(Tool):
    """Create entity tool (spec section 1.1.3.1.3)."""

    name = "Create Entity"
    icon_label = "CE"

    def __init__(self):
        self._has_hitbox: bool = False
        self._has_inventory: bool = False
        self._entity_kind_index: int = 0

    def draw_properties(self) -> None:
        imgui.text("Create Entity")
        _, self._entity_kind_index = imgui.input_int(
            "Entity Kind##create", self._entity_kind_index)
        _, self._has_hitbox = imgui.checkbox(
            "Has Hitbox##create", self._has_hitbox)
        _, self._has_inventory = imgui.checkbox(
            "Has Inventory##create", self._has_inventory)


class EntityEditMode(EditorMode):
    name = "Entity Edit"
    shortcut_label = "Ctrl+E"

    def __init__(self, keybind_manager):
        super().__init__(keybind_manager)
        self._tools = [
            EntitySelectTool(),
            EntityPanTool(),
            CreateEntityTool(),
        ]
