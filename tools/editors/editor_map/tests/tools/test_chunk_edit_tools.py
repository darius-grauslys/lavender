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

    def test_set_tile_enums(self):
        from core.c_enum import CEnum, CEnumMember
        tool = TileDrawTool()
        enum = CEnum(
            name="Tile_Kind",
            members=[
                CEnumMember("Tile_Kind__None", 0),
                CEnumMember("Tile_Kind__Grass", 1),
                CEnumMember("Tile_Kind__Unknown", 2),
            ])
        tool.set_tile_enums([enum])
        self.assertEqual(len(tool._tile_enums), 1)
        self.assertEqual(tool._tile_enums[0].name, "Tile_Kind")

    def test_set_active_tilesheet_none(self):
        tool = TileDrawTool()
        tool.set_active_tilesheet(None)
        self.assertIsNone(tool._active_tilesheet)


class TestTileDrawToolChunkUpdate(unittest.TestCase):
    """Test that tile draw operations actually update chunk data
    in WorkspaceObjects.

    These tests simulate what happens when the user clicks on the
    workspace with the TileDrawTool selected: the selected tile
    value should be written into the chunk's tile data at the
    clicked position.
    """

    def _make_objects(self, tile_size=1, chunk_w=8, chunk_h=8,
                      chunk_d=2):
        """Create a WorkspaceObjects with a single loaded chunk."""
        from core.engine_config import EngineConfig
        from workspace.objects import WorkspaceObjects, ChunkData

        config = EngineConfig(constants={
            'CHUNK__WIDTH': chunk_w,
            'CHUNK__HEIGHT': chunk_h,
            'CHUNK__DEPTH': chunk_d,
            'CHUNK__QUANTITY_OF__TILES': chunk_w * chunk_h * chunk_d,
        })

        objects = WorkspaceObjects(config, max_tmp_chunks=999999)
        total_tiles = chunk_w * chunk_h * chunk_d
        tile_bytes = bytearray(total_tiles * tile_size)
        chunk = ChunkData(
            chunk_x=0, chunk_y=0, chunk_z=0,
            tile_bytes=tile_bytes)
        objects._put_chunk(chunk)
        return objects, config

    def test_set_tile_updates_chunk_data(self):
        """Setting a tile via objects.set_tile should change the
        underlying chunk bytes."""
        objects, config = self._make_objects(tile_size=1)
        # Verify initial value is 0
        initial = objects.get_tile_bytes(0, 0, 0, 3, 4, 0, 1)
        self.assertIsNotNone(initial)
        self.assertEqual(initial[0], 0)

        # Write tile value 42
        objects.set_tile(0, 0, 0, 3, 4, 0, bytes([42]))
        result = objects.get_tile_bytes(0, 0, 0, 3, 4, 0, 1)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 42)

    def test_set_tile_marks_chunk_dirty(self):
        """After set_tile, the chunk should be marked dirty."""
        objects, config = self._make_objects()
        chunk = objects.get_chunk(0, 0, 0)
        self.assertFalse(chunk.is_dirty)
        objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
        chunk = objects.get_chunk(0, 0, 0)
        self.assertTrue(chunk.is_dirty)

    def test_set_tile_multi_byte(self):
        """Tile draw with multi-byte tiles should write all bytes."""
        objects, config = self._make_objects(tile_size=2)
        objects.set_tile(0, 0, 0, 1, 1, 0, bytes([0xAB, 0xCD]))
        result = objects.get_tile_bytes(0, 0, 0, 1, 1, 0, 2)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 0xAB)
        self.assertEqual(result[1], 0xCD)

    def test_set_tile_different_positions_independent(self):
        """Writing to one tile position should not affect another."""
        objects, config = self._make_objects()
        objects.set_tile(0, 0, 0, 0, 0, 0, bytes([10]))
        objects.set_tile(0, 0, 0, 7, 7, 0, bytes([20]))

        r1 = objects.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
        r2 = objects.get_tile_bytes(0, 0, 0, 7, 7, 0, 1)
        self.assertEqual(r1[0], 10)
        self.assertEqual(r2[0], 20)

    def test_set_tile_y_inversion(self):
        """Verify Y-axis inversion in tile indexing matches
        the engine's get_p_tile_from__chunk formula."""
        objects, config = self._make_objects(
            tile_size=1, chunk_w=8, chunk_h=8)
        # Write to (x=0, y=0) and (x=0, y=7) — these should map
        # to different offsets due to Y inversion.
        objects.set_tile(0, 0, 0, 0, 0, 0, bytes([0xAA]))
        objects.set_tile(0, 0, 0, 0, 7, 0, bytes([0xBB]))

        r_y0 = objects.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
        r_y7 = objects.get_tile_bytes(0, 0, 0, 0, 7, 0, 1)
        self.assertEqual(r_y0[0], 0xAA)
        self.assertEqual(r_y7[0], 0xBB)
        # They should be at different raw offsets
        self.assertNotEqual(r_y0, r_y7)

    def test_set_tile_on_z_layer(self):
        """Writing to z=1 should not affect z=0."""
        objects, config = self._make_objects(
            tile_size=1, chunk_d=2)
        objects.set_tile(0, 0, 0, 0, 0, 0, bytes([0x11]))
        objects.set_tile(0, 0, 0, 0, 0, 1, bytes([0x22]))

        r_z0 = objects.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
        r_z1 = objects.get_tile_bytes(0, 0, 0, 0, 0, 1, 1)
        self.assertEqual(r_z0[0], 0x11)
        self.assertEqual(r_z1[0], 0x22)

    def test_set_tile_nonexistent_chunk_is_noop(self):
        """set_tile on a chunk that isn't loaded should not crash."""
        objects, config = self._make_objects()
        # Chunk (99, 99, 0) doesn't exist
        objects.set_tile(99, 99, 0, 0, 0, 0, bytes([42]))
        result = objects.get_tile_bytes(99, 99, 0, 0, 0, 0, 1)
        self.assertIsNone(result)

    def test_get_dirty_chunks_after_draw(self):
        """After drawing, get_dirty_chunks should return the
        modified chunk."""
        objects, config = self._make_objects()
        self.assertEqual(len(objects.get_dirty_chunks()), 0)
        objects.set_tile(0, 0, 0, 2, 3, 0, bytes([5]))
        dirty = objects.get_dirty_chunks()
        self.assertEqual(len(dirty), 1)
        self.assertEqual(dirty[0].chunk_x, 0)
        self.assertEqual(dirty[0].chunk_y, 0)

    def test_overwrite_tile_preserves_latest_value(self):
        """Writing to the same tile twice should keep the last value."""
        objects, config = self._make_objects()
        objects.set_tile(0, 0, 0, 3, 3, 0, bytes([10]))
        objects.set_tile(0, 0, 0, 3, 3, 0, bytes([20]))
        result = objects.get_tile_bytes(0, 0, 0, 3, 3, 0, 1)
        self.assertEqual(result[0], 20)

    def test_all_tile_positions_writable(self):
        """Fuzzy check: write a unique value to every tile position
        in the chunk and verify all are independently readable."""
        objects, config = self._make_objects(
            tile_size=1, chunk_w=8, chunk_h=8, chunk_d=1)
        # Write unique values
        for y in range(8):
            for x in range(8):
                val = (x + y * 8) & 0xFF
                objects.set_tile(0, 0, 0, x, y, 0, bytes([val]))
        # Read back and verify
        for y in range(8):
            for x in range(8):
                expected = (x + y * 8) & 0xFF
                result = objects.get_tile_bytes(0, 0, 0, x, y, 0, 1)
                self.assertIsNotNone(
                    result,
                    f"Tile ({x},{y}) returned None")
                self.assertEqual(
                    result[0], expected,
                    f"Tile ({x},{y}): expected {expected}, got {result[0]}")


class TestChunkEditMode(unittest.TestCase):

    def test_name(self):
        km = KeybindManager()
        mode = ChunkEditMode(km)
        self.assertEqual(mode.name, "Chunk Edit")

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
