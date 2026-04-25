"""
Container/Inventory Edit mode — PLACEHOLDER (spec section 1.1.4).

Activation shortcut: Ctrl+I
"""

from __future__ import annotations

from modes.editor_mode import EditorMode

import imgui


class InventoryEditMode(EditorMode):
    name = "Container/Inventory Edit"
    shortcut_label = "Ctrl+I"

    def __init__(self, keybind_manager):
        super().__init__(keybind_manager)
        self._tools = []

    def draw_workspace(self, workspace) -> None:
        imgui.text("Container/Inventory Edit — Not yet implemented")
