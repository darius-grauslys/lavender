"""
Unit tests for Inventory Edit mode (stub).
"""

from __future__ import annotations

import unittest

from keybinds.keybind_manager import KeybindManager
from modes.inventory_edit import InventoryEditMode
from workspace.movement import WorkspaceMovement


class TestInventoryEditMode(unittest.TestCase):

    def test_name(self):
        km = KeybindManager()
        mode = InventoryEditMode(km)
        self.assertEqual(mode.name, "Container/Inventory Edit")

    def test_has_no_tools(self):
        km = KeybindManager()
        mode = InventoryEditMode(km)
        self.assertEqual(len(mode.tools), 0)

    def test_set_movement(self):
        km = KeybindManager()
        mode = InventoryEditMode(km)
        movement = WorkspaceMovement()
        mode.set_movement(movement)
        self.assertIs(mode._movement, movement)

    def test_activate_deactivate_keybind_stack(self):
        km = KeybindManager()
        mode = InventoryEditMode(km)
        mode.on_activate()
        # Mode pushes its (empty) keybinds, no tool push
        self.assertEqual(len(km._callee_override_stack), 1)
        mode.on_deactivate()
        self.assertEqual(len(km._callee_override_stack), 0)


if __name__ == "__main__":
    unittest.main()
