"""
Unit tests for Global Space View mode tools.
"""

from __future__ import annotations

import unittest

from keybinds.keybind import KeyCombo, Modifier
from keybinds.keybind_manager import KeybindManager
from modes.global_space_view import (
    GlobalSpaceSelectTool,
    GlobalSpacePanTool,
    GoToTool,
    GlobalSpaceViewMode,
)
from tools.pan_tool import _KEY_UP, _KEY_DOWN, _KEY_LEFT, _KEY_RIGHT
from workspace.movement import WorkspaceMovement


class TestGlobalSpaceSelectTool(unittest.TestCase):

    def test_name(self):
        tool = GlobalSpaceSelectTool()
        self.assertEqual(tool.name, "Global_Space Select")

    def test_build_keybinds_has_shift_z_axis(self):
        movement = WorkspaceMovement()
        tool = GlobalSpaceSelectTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.SHIFT), binds)

    def test_shift_up_moves_z_up(self):
        movement = WorkspaceMovement()
        tool = GlobalSpaceSelectTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_UP, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_z, start_z + 1)

    def test_shift_down_moves_z_down(self):
        movement = WorkspaceMovement()
        tool = GlobalSpaceSelectTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_z, start_z - 1)

    def test_inherits_base_select_keybinds(self):
        movement = WorkspaceMovement()
        tool = GlobalSpaceSelectTool(movement)
        binds = tool._build_keybinds()
        # Should still have arrow keys from base
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_LEFT, Modifier.NONE), binds)


class TestGlobalSpacePanTool(unittest.TestCase):

    def test_name(self):
        tool = GlobalSpacePanTool()
        self.assertEqual(tool.name, "Global_Space Pan")

    def test_build_keybinds_has_shift_arrows(self):
        movement = WorkspaceMovement()
        tool = GlobalSpacePanTool(movement, gs_width=8, gs_height=8)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_LEFT, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_RIGHT, Modifier.SHIFT), binds)

    def test_shift_up_pans_by_global_space(self):
        movement = WorkspaceMovement()
        tool = GlobalSpacePanTool(movement, gs_width=8, gs_height=8)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(_KEY_UP, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_y, start_y - 8)

    def test_shift_right_pans_by_global_space(self):
        movement = WorkspaceMovement()
        tool = GlobalSpacePanTool(movement, gs_width=16, gs_height=8)
        binds = tool._build_keybinds()
        start_x = movement.viewport.center_x
        binds[KeyCombo(_KEY_RIGHT, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_x, start_x + 16)

    def test_inherits_base_pan_keybinds(self):
        movement = WorkspaceMovement()
        tool = GlobalSpacePanTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)


class TestGoToTool(unittest.TestCase):

    def test_name(self):
        tool = GoToTool()
        self.assertEqual(tool.name, "Go-To")

    def test_construct_without_movement(self):
        tool = GoToTool()
        self.assertIsNone(tool._movement)
        self.assertFalse(tool._show_prompt)

    def test_construct_with_movement(self):
        movement = WorkspaceMovement()
        tool = GoToTool(movement)
        self.assertIs(tool._movement, movement)

    def test_set_movement(self):
        tool = GoToTool()
        movement = WorkspaceMovement()
        tool.set_movement(movement)
        self.assertIs(tool._movement, movement)

    def test_target_coords_default(self):
        tool = GoToTool()
        self.assertEqual(tool.target_coords, (0, 0, 0))

    def test_activate_shows_prompt(self):
        km = KeybindManager()
        tool = GoToTool()
        tool.on_activate(km)
        self.assertTrue(tool._show_prompt)


class TestGlobalSpaceViewMode(unittest.TestCase):

    def test_name(self):
        km = KeybindManager()
        mode = GlobalSpaceViewMode(km)
        self.assertEqual(mode.name, "Global_Space View")

    def test_has_three_tools(self):
        km = KeybindManager()
        mode = GlobalSpaceViewMode(km)
        self.assertEqual(len(mode.tools), 3)

    def test_tools_receive_movement(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = GlobalSpaceViewMode(km, movement=movement)
        self.assertIs(mode._gs_select._movement, movement)
        self.assertIs(mode._gs_pan._movement, movement)
        self.assertIs(mode._goto._movement, movement)

    def test_set_movement_propagates(self):
        km = KeybindManager()
        mode = GlobalSpaceViewMode(km)
        movement = WorkspaceMovement()
        mode.set_movement(movement)
        self.assertIs(mode._gs_select._movement, movement)
        self.assertIs(mode._gs_pan._movement, movement)
        self.assertIs(mode._goto._movement, movement)

    def test_activate_pushes_keybinds(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = GlobalSpaceViewMode(km, movement=movement)
        mode.on_activate()
        # Mode push + tool push (base + tool-specific)
        self.assertGreater(len(km._callee_override_stack), 0)

    def test_deactivate_pops_keybinds(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = GlobalSpaceViewMode(km, movement=movement)
        mode.on_activate()
        mode.on_deactivate()
        # Should be back to empty
        self.assertEqual(len(km._callee_override_stack), 0)


if __name__ == "__main__":
    unittest.main()
