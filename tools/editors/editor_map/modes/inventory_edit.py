"""
Container/Inventory Edit mode — PLACEHOLDER (spec section 1.1.4).

Activation shortcut: Ctrl+I
"""

from __future__ import annotations

from typing import Optional

from modes.editor_mode import EditorMode
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

import imgui


class InventoryEditMode(EditorMode):
    name = "Container/Inventory Edit"
    shortcut_label = "Ctrl+I"

    def __init__(
            self,
            keybind_manager: KeybindManager,
            movement: Optional[WorkspaceMovement] = None):
        super().__init__(keybind_manager)
        self._movement = movement
        self._tools = []

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject movement (no tools to update in stub)."""
        self._movement = movement

    def draw_workspace(self, workspace) -> None:
        imgui.text("Container/Inventory Edit — Not yet implemented")
