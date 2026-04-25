"""
Entity Edit mode (spec section 1.1.3).

Activation shortcut: Ctrl+E
"""

from __future__ import annotations

from typing import Optional

from modes.editor_mode import EditorMode
from tools.select_tool import SelectTool
from tools.pan_tool import PanTool
from tools.tool import Tool
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

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

    def __init__(
            self,
            keybind_manager: KeybindManager,
            movement: Optional[WorkspaceMovement] = None):
        super().__init__(keybind_manager)
        self._movement = movement
        self._entity_select = EntitySelectTool(movement)
        self._entity_pan = EntityPanTool(movement)
        self._create_entity = CreateEntityTool()
        self._tools = [
            self._entity_select,
            self._entity_pan,
            self._create_entity,
        ]

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject movement into tools."""
        self._movement = movement
        self._entity_select.set_movement(movement)
        self._entity_pan.set_movement(movement)
