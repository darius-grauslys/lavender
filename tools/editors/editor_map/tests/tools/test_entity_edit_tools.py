"""
Unit tests for Entity Edit mode tools.
"""

from __future__ import annotations

import unittest

from keybinds.keybind import KeyCombo, Modifier
from keybinds.keybind_manager import KeybindManager
from modes.entity_edit import (
    EntitySelectTool,
    EntityPanTool,
    CreateEntityTool,
    EntityEditMode,
)
from tools.pan_tool import _KEY_UP, _KEY_DOWN
from workspace.movement import WorkspaceMovement


class TestEntitySelectTool(unittest.TestCase):

    def test_name(self):
        tool = EntitySelectTool()
        self.assertEqual(tool.name, "Entity Select")

    def test_build_keybinds_with_movement(self):
        movement = WorkspaceMovement()
        tool = EntitySelectTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)

    def test_build_keybinds_without_movement_has_copy_paste(self):
        tool = EntitySelectTool()
        binds = tool._build_keybinds()
        from tools.select_tool import _KEY_C
        self.assertIn(KeyCombo(_KEY_C, Modifier.CTRL), binds)


class TestEntityPanTool(unittest.TestCase):

    def test_name(self):
        tool = EntityPanTool()
        self.assertEqual(tool.name, "Entity Pan")

    def test_build_keybinds_with_movement(self):
        movement = WorkspaceMovement()
        tool = EntityPanTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)


class TestCreateEntityTool(unittest.TestCase):

    def test_name(self):
        tool = CreateEntityTool()
        self.assertEqual(tool.name, "Create Entity")

    def test_default_state(self):
        tool = CreateEntityTool()
        self.assertFalse(tool._has_hitbox)
        self.assertFalse(tool._has_inventory)
        self.assertEqual(tool._entity_kind_index, 0)


class TestEntityEditMode(unittest.TestCase):

    def test_name(self):
        km = KeybindManager()
        mode = EntityEditMode(km)
        self.assertEqual(mode.name, "Entity Edit")

    def test_has_three_tools(self):
        km = KeybindManager()
        mode = EntityEditMode(km)
        self.assertEqual(len(mode.tools), 3)

    def test_tools_receive_movement(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = EntityEditMode(km, movement=movement)
        self.assertIs(mode._entity_select._movement, movement)
        self.assertIs(mode._entity_pan._movement, movement)

    def test_set_movement_propagates(self):
        km = KeybindManager()
        mode = EntityEditMode(km)
        movement = WorkspaceMovement()
        mode.set_movement(movement)
        self.assertIs(mode._entity_select._movement, movement)
        self.assertIs(mode._entity_pan._movement, movement)

    def test_activate_deactivate_keybind_stack(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = EntityEditMode(km, movement=movement)
        mode.on_activate()
        self.assertGreater(len(km._callee_override_stack), 0)
        mode.on_deactivate()
        self.assertEqual(len(km._callee_override_stack), 0)


if __name__ == "__main__":
    unittest.main()
