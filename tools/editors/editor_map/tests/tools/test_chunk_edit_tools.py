"""
Unit tests for Chunk Edit mode tools.
"""

from __future__ import annotations

import unittest

from keybinds.keybind import KeyCombo, Modifier
from keybinds.keybind_manager import KeybindManager
from modes.chunk_edit import (
    TileSelectTool,
    ChunkPanTool,
    TileDrawTool,
    ChunkEditMode,
)
from tools.pan_tool import _KEY_UP, _KEY_DOWN, _KEY_LEFT, _KEY_RIGHT
from workspace.movement import WorkspaceMovement


class TestTileSelectTool(unittest.TestCase):

    def test_name(self):
        tool = TileSelectTool()
        self.assertEqual(tool.name, "Tile Select")

    def test_build_keybinds_has_shift_z_axis(self):
        movement = WorkspaceMovement()
        tool = TileSelectTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.SHIFT), binds)

    def test_shift_up_moves_z_up(self):
        movement = WorkspaceMovement()
        tool = TileSelectTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_UP, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_z, start_z + 1)

    def test_shift_down_moves_z_down(self):
        movement = WorkspaceMovement()
        tool = TileSelectTool(movement)
        binds = tool._build_keybinds()
        start_z = movement.viewport.center_z
        binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_z, start_z - 1)

    def test_inherits_base_select_keybinds(self):
        movement = WorkspaceMovement()
        tool = TileSelectTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)


class TestChunkPanTool(unittest.TestCase):

    def test_name(self):
        tool = ChunkPanTool()
        self.assertEqual(tool.name, "Chunk Pan")

    def test_build_keybinds_has_shift_arrows(self):
        movement = WorkspaceMovement()
        tool = ChunkPanTool(movement, chunk_w=8, chunk_h=8)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_DOWN, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_LEFT, Modifier.SHIFT), binds)
        self.assertIn(KeyCombo(_KEY_RIGHT, Modifier.SHIFT), binds)

    def test_shift_up_pans_by_chunk(self):
        movement = WorkspaceMovement()
        tool = ChunkPanTool(movement, chunk_w=8, chunk_h=8)
        binds = tool._build_keybinds()
        start_y = movement.viewport.center_y
        binds[KeyCombo(_KEY_UP, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_y, start_y - 8)

    def test_shift_right_pans_by_chunk_width(self):
        movement = WorkspaceMovement()
        tool = ChunkPanTool(movement, chunk_w=16, chunk_h=8)
        binds = tool._build_keybinds()
        start_x = movement.viewport.center_x
        binds[KeyCombo(_KEY_RIGHT, Modifier.SHIFT)]()
        self.assertEqual(movement.viewport.center_x, start_x + 16)

    def test_inherits_base_pan_keybinds(self):
        movement = WorkspaceMovement()
        tool = ChunkPanTool(movement)
        binds = tool._build_keybinds()
        self.assertIn(KeyCombo(_KEY_UP, Modifier.NONE), binds)
        self.assertIn(KeyCombo(_KEY_UP, Modifier.CTRL), binds)


class TestTileDrawTool(unittest.TestCase):

    def test_name(self):
        tool = TileDrawTool()
        self.assertEqual(tool.name, "Tile Draw")

    def test_selected_tile_value_default(self):
        tool = TileDrawTool()
        self.assertEqual(tool.selected_tile_value, 0)

    def test_selected_layer_default(self):
        tool = TileDrawTool()
        self.assertEqual(tool.selected_layer, 0)


class TestChunkEditMode(unittest.TestCase):

    def test_name(self):
        km = KeybindManager()
        mode = ChunkEditMode(km)
        self.assertEqual(mode.name, "Chunk Edit")

    def test_has_three_tools(self):
        km = KeybindManager()
        mode = ChunkEditMode(km)
        self.assertEqual(len(mode.tools), 3)

    def test_tools_receive_movement(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = ChunkEditMode(km, movement=movement)
        self.assertIs(mode._tile_select._movement, movement)
        self.assertIs(mode._chunk_pan._movement, movement)

    def test_set_movement_propagates(self):
        km = KeybindManager()
        mode = ChunkEditMode(km)
        movement = WorkspaceMovement()
        mode.set_movement(movement)
        self.assertIs(mode._tile_select._movement, movement)
        self.assertIs(mode._chunk_pan._movement, movement)

    def test_activate_deactivate_keybind_stack(self):
        km = KeybindManager()
        movement = WorkspaceMovement()
        mode = ChunkEditMode(km, movement=movement)
        mode.on_activate()
        self.assertGreater(len(km._callee_override_stack), 0)
        mode.on_deactivate()
        self.assertEqual(len(km._callee_override_stack), 0)


if __name__ == "__main__":
    unittest.main()
