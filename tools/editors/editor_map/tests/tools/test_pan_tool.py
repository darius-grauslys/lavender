"""
Unit tests for the base PanTool (tools/pan_tool.py).
"""

from __future__ import annotations

import unittest

from keybinds.keybind import (
    KeyCombo, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from tools.pan_tool import PanTool, _KEY_UP, _KEY_DOWN, _KEY_LEFT, _KEY_RIGHT
from workspace.movement import WorkspaceMovement


class TestPanToolConstruction(unittest.TestCase):
    """Test PanTool can be constructed with and without movement."""

    def test_construct_without_movement(self):
        tool = PanTool()
        self.assertEqual(tool.name, "Pan")
        self.assertEqual(tool.icon_label, "P")
        self.assertFalse(tool._is_active)
        self.assertIsNone(tool._movement)

    def test_construct_with_movement(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        self.assertIs(tool._movement, movement)

    def test_set_movement(self):
        tool = PanTool()
        movement = WorkspaceMovement()
        tool.set_movement(movement)
        self.assertIs(tool._movement, movement)


class TestPanToolBuildKeybinds(unittest.TestCase):
    """Test _build_keybinds returns expected combos."""

    def test_build_keybinds_without_movement_returns_empty(self):
        tool = PanTool()
        binds = tool._build_keybinds()
        self.assertEqual(binds, {})

    def test_build_keybinds_with_movement_has_arrow_keys(self):
        tool = PanTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_LEFT, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_RIGHT, Modifier.NONE), binds)

    def test_build_keybinds_has_z_axis_movement(self):
        tool = PanTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.CTRL), binds)

    def test_build_keybinds_has_scroll_vertical(self):
        tool = PanTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.NONE), binds)

    def test_build_keybinds_has_scroll_horizontal(self):
        tool = PanTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.SHIFT), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.SHIFT), binds)

    def test_build_keybinds_has_zoom(self):
        tool = PanTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_ZOOM_IN, Modifier.ALT_SHIFT), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_ZOOM_OUT, Modifier.ALT_SHIFT), binds)


class TestPanToolActivation(unittest.TestCase):
    """Test activate/deactivate pushes/pops keybind overrides."""

    def test_activate_pushes_overrides(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        tool = PanTool(movement)

        self.assertEqual(len(km._callee_override_stack), 0)
        tool.on_activate(km)
        self.assertTrue(tool._is_active)
        # Tool base class pushes once, PanTool pushes once more
        self.assertEqual(len(km._callee_override_stack), 2)

    def test_deactivate_pops_overrides(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        tool = PanTool(movement)

        tool.on_activate(km)
        stack_depth = len(km._callee_override_stack)
        tool.on_deactivate(km)
        self.assertFalse(tool._is_active)
        self.assertEqual(len(km._callee_override_stack), stack_depth - 1)

    def test_deactivate_without_manager_does_not_crash(self):
        tool = PanTool(WorkspaceMovement())
        tool._is_active = True
        tool.on_deactivate(None)
        self.assertFalse(tool._is_active)


class TestPanToolCallbacks(unittest.TestCase):
    """Test that keybind callbacks actually move the viewport."""

    def test_arrow_up_pans_up(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(_KEY_UP, Modifier.NONE)]()
        self.assertEqual(movement.viewport.center_y, start_y - 1)

    def test_arrow_down_pans_down(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(_KEY_DOWN, Modifier.NONE)]()
        self.assertEqual(movement.viewport.center_y, start_y + 1)

    def test_arrow_left_pans_left(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_x = movement.viewport.center_x
        binds[KeyCombo(_KEY_LEFT, Modifier.NONE)]()
        self.assertEqual(movement.viewport.center_x, start_x - 1)

    def test_arrow_right_pans_right(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_x = movement.viewport.center_x
        binds[KeyCombo(_KEY_RIGHT, Modifier.NONE)]()
        self.assertEqual(movement.viewport.center_x, start_x + 1)

    def test_ctrl_up_moves_z_up(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_UP, Modifier.CTRL)]()
        self.assertEqual(movement.viewport.center_z, start_z + 1)

    def test_ctrl_down_moves_z_down(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_DOWN, Modifier.CTRL)]()
        self.assertEqual(movement.viewport.center_z, start_z - 1)

    def test_scroll_up_pans_vertically(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE)]()
        self.assertNotEqual(movement.viewport.center_y, start_y)

    def test_zoom_in_increases_zoom(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_zoom = movement.viewport.zoom
        binds[KeyCombo(VIRTUAL_KEY_ZOOM_IN, Modifier.ALT_SHIFT)]()
        self.assertGreater(movement.viewport.zoom, start_zoom)

    def test_zoom_out_decreases_zoom(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        binds = tool._build_keybinds()
        start_zoom = movement.viewport.zoom
        binds[KeyCombo(VIRTUAL_KEY_ZOOM_OUT, Modifier.ALT_SHIFT)]()
        self.assertLess(movement.viewport.zoom, start_zoom)

    def test_workspace_drag_pans_by_pixels(self):
        movement = WorkspaceMovement()
        tool = PanTool(movement)
        start_ox = movement.viewport.offset_x
        start_oy = movement.viewport.offset_y
        tool.on_workspace_drag(5.0, 10.0)
        self.assertEqual(movement.viewport.offset_x, start_ox + 5.0)
        self.assertEqual(movement.viewport.offset_y, start_oy + 10.0)

    def test_workspace_drag_without_movement_does_not_crash(self):
        tool = PanTool()
        tool.on_workspace_drag(5.0, 10.0)  # Should not raise


if __name__ == "__main__":
    unittest.main()
