"""
Unit tests for the base SelectTool (tools/select_tool.py).
"""

from __future__ import annotations

import unittest

from keybinds.keybind import (
    KeyCombo, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from tools.select_tool import (
    SelectTool,
    _KEY_UP, _KEY_DOWN, _KEY_LEFT, _KEY_RIGHT,
    _KEY_C, _KEY_V,
)
from workspace.movement import WorkspaceMovement


class TestSelectToolConstruction(unittest.TestCase):

    def test_construct_without_movement(self):
        tool = SelectTool()
        self.assertEqual(tool.name, "Select")
        self.assertEqual(tool.icon_label, "S")
        self.assertFalse(tool._is_active)
        self.assertIsNone(tool._movement)
        self.assertEqual(tool._selection, [])
        self.assertIsNone(tool._clipboard)

    def test_construct_with_movement(self):
        movement = WorkspaceMovement()
        tool = SelectTool(movement)
        self.assertIs(tool._movement, movement)

    def test_set_movement(self):
        tool = SelectTool()
        movement = WorkspaceMovement()
        tool.set_movement(movement)
        self.assertIs(tool._movement, movement)


class TestSelectToolBuildKeybinds(unittest.TestCase):

    def test_build_keybinds_without_movement_has_copy_paste(self):
        tool = SelectTool()
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_C, Modifier.CTRL), binds)
        self.assertIn(KeyCombo(_KEY_V, Modifier.CTRL), binds)

    def test_build_keybinds_without_movement_lacks_arrows(self):
        tool = SelectTool()
        binds = tool._build_keybinds()
        self.assertNotIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)

    def test_build_keybinds_with_movement_has_arrows(self):
        tool = SelectTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_LEFT, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_RIGHT, Modifier.NONE), binds)

    def test_build_keybinds_has_z_axis(self):
        tool = SelectTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.CTRL), binds)

    def test_build_keybinds_has_scroll(self):
        tool = SelectTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.NONE), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.SHIFT), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.SHIFT), binds)

    def test_build_keybinds_has_zoom(self):
        tool = SelectTool(WorkspaceMovement())
        binds = tool._build_keybinds()
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_ZOOM_IN, Modifier.ALT_SHIFT), binds)
        self.assertIn(
            KeyCombo(VIRTUAL_KEY_ZOOM_OUT, Modifier.ALT_SHIFT), binds)


class TestSelectToolActivation(unittest.TestCase):

    def test_activate_pushes_overrides(self):
        km = KeybindManager()
        tool = SelectTool(WorkspaceMovement())
        self.assertEqual(len(km._callee_override_stack), 0)
        tool.on_activate(km)
        self.assertTrue(tool._is_active)
        # Tool base pushes once (empty), SelectTool pushes once
        self.assertEqual(len(km._callee_override_stack), 2)

    def test_deactivate_pops_overrides(self):
        km = KeybindManager()
        tool = SelectTool(WorkspaceMovement())
        tool.on_activate(km)
        depth = len(km._callee_override_stack)
        tool.on_deactivate(km)
        self.assertFalse(tool._is_active)
        self.assertEqual(len(km._callee_override_stack), depth - 1)

    def test_deactivate_without_manager_does_not_crash(self):
        tool = SelectTool()
        tool._is_active = True
        tool.on_deactivate(None)
        self.assertFalse(tool._is_active)


class TestSelectToolSelection(unittest.TestCase):

    def test_select_adds_to_selection(self):
        tool = SelectTool()
        tool.select("item_a")
        self.assertIn("item_a", tool.selection)

    def test_select_does_not_duplicate(self):
        tool = SelectTool()
        tool.select("item_a")
        tool.select("item_a")
        self.assertEqual(tool.selection.count("item_a"), 1)

    def test_deselect_removes_from_selection(self):
        tool = SelectTool()
        tool.select("item_a")
        tool.deselect("item_a")
        self.assertNotIn("item_a", tool.selection)

    def test_deselect_nonexistent_does_not_crash(self):
        tool = SelectTool()
        tool.deselect("nonexistent")  # Should not raise

    def test_clear_selection(self):
        tool = SelectTool()
        tool.select("a")
        tool.select("b")
        tool.clear_selection()
        self.assertEqual(tool.selection, [])

    def test_multi_select(self):
        tool = SelectTool()
        tool.select("a")
        tool.select("b")
        tool.select("c")
        self.assertEqual(len(tool.selection), 3)


class TestSelectToolCopyPaste(unittest.TestCase):

    def test_copy_stores_first_selected(self):
        tool = SelectTool()
        tool.select("item_a")
        tool.select("item_b")
        tool.copy()
        self.assertEqual(tool._clipboard, "item_a")

    def test_copy_empty_selection_does_nothing(self):
        tool = SelectTool()
        tool.copy()
        self.assertIsNone(tool._clipboard)

    def test_paste_returns_clipboard(self):
        tool = SelectTool()
        tool.select("item_a")
        tool.copy()
        result = tool.paste()
        self.assertEqual(result, "item_a")

    def test_paste_empty_clipboard_returns_none(self):
        tool = SelectTool()
        result = tool.paste()
        self.assertIsNone(result)


class TestSelectToolCallbacks(unittest.TestCase):

    def test_copy_callback_via_keybind(self):
        movement = WorkspaceMovement()
        tool = SelectTool(movement)
        tool.select("test_item")
        binds = tool._build_keybinds()
        binds[KeyCombo(_KEY_C, Modifier.CTRL)]()
        self.assertEqual(tool._clipboard, "test_item")

    def test_paste_callback_via_keybind(self):
        movement = WorkspaceMovement()
        tool = SelectTool(movement)
        tool.select("test_item")
        tool.copy()
        binds = tool._build_keybinds()
        # paste callback returns clipboard but we just verify no crash
        binds[KeyCombo(_KEY_V, Modifier.CTRL)]()

    def test_arrow_callbacks_move_viewport(self):
        movement = WorkspaceMovement()
        tool = SelectTool(movement)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(_KEY_UP, Modifier.NONE)]()
        self.assertEqual(movement.viewport.center_y, start_y - 1)


if __name__ == "__main__":
    unittest.main()
