"""
Integration tests for the workspace modules.

Tests the full lifecycle:
1. Empty world → empty chunks auto-created for visible area
2. Tile drawing writes .tmp files
3. Auto-save threshold flushes .tmp → real files
4. Moving workspace unloads/loads chunks
5. Moving back verifies data persistence
6. Ctrl+S (flush_all_tmp) saves everything
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.engine_config import EngineConfig
from workspace.movement import WorkspaceMovement
from workspace.objects import WorkspaceObjects, ChunkData
from core.world_directory import (
    chunk_tile_path,
    chunk_tile_tmp_path,
    ensure_world_dir,
)


def _make_config(
        chunk_w: int = 8,
        chunk_h: int = 8,
        chunk_d: int = 1) -> EngineConfig:
    return EngineConfig(constants={
        'CHUNK__WIDTH': chunk_w,
        'CHUNK__HEIGHT': chunk_h,
        'CHUNK__DEPTH': chunk_d,
        'CHUNK__QUANTITY_OF__TILES': chunk_w * chunk_h * chunk_d,
    })


class TestEmptyWorldChunkCreation(unittest.TestCase):
    """When the world directory is empty, visible chunks should be
    auto-created as empty (all-zero) chunks."""

    def test_get_or_create_chunk_creates_empty_for_empty_world(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()
            ensure_world_dir(project, "empty_world", "test_plat")

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="empty_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            # Simulate loading visible area (e.g. 3x3 chunks)
            for cy in range(-1, 2):
                for cx in range(-1, 2):
                    chunk = objects.get_or_create_chunk(cx, cy, 0)
                    self.assertIsNotNone(chunk)
                    self.assertEqual(chunk.chunk_x, cx)
                    self.assertEqual(chunk.chunk_y, cy)
                    self.assertFalse(chunk.is_dirty)
                    self.assertTrue(
                        all(b == 0 for b in chunk.tile_bytes),
                        f"Chunk ({cx},{cy}) should be all zeros")

    def test_empty_chunks_accessible_via_get_chunk(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()
            ensure_world_dir(project, "empty_world", "test_plat")

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="empty_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            objects.get_or_create_chunk(5, 5, 0)
            chunk = objects.get_chunk(5, 5, 0)
            self.assertIsNotNone(chunk)

    def test_empty_chunks_not_dirty(self):
        """Empty auto-created chunks should NOT be dirty and should
        NOT generate .tmp files until modified."""
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()
            ensure_world_dir(project, "empty_world", "test_plat")

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="empty_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            objects.get_or_create_chunk(0, 0, 0)
            self.assertEqual(objects.pending_tmp_count, 0)
            self.assertEqual(len(objects.get_dirty_chunks()), 0)


class TestTileDrawWritesTmp(unittest.TestCase):
    """Drawing a tile should create a .tmp file."""

    def test_set_tile_creates_tmp(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()
            ensure_world_dir(project, "draw_world", "test_plat")

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="draw_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            # Create chunk, then draw
            objects.get_or_create_chunk(0, 0, 0)
            objects.set_tile(0, 0, 0, 3, 3, 0, bytes([42]))

            self.assertEqual(objects.pending_tmp_count, 1)

            tmp_path = chunk_tile_tmp_path(
                project, "draw_world", 0, 0, 0,
                platform="test_plat")
            self.assertTrue(tmp_path.exists())

    def test_tile_value_readable_after_draw(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="draw_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            objects.get_or_create_chunk(0, 0, 0)
            objects.set_tile(0, 0, 0, 5, 5, 0, bytes([0xAB]))

            result = objects.get_tile_bytes(0, 0, 0, 5, 5, 0, 1)
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 0xAB)


class TestAutoSaveThresholdIntegration(unittest.TestCase):
    """When the .tmp threshold is hit, all pending chunks should
    be flushed to real files."""

    def test_threshold_flushes_all(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="threshold_world",
                platform="test_plat",
                max_tmp_chunks=3)

            # Create and modify 3 chunks
            for i in range(3):
                objects.get_or_create_chunk(i, 0, 0)

            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
            objects.set_tile(1, 0, 0, 0, 0, 0, bytes([2]))
            # Third triggers flush
            objects.set_tile(2, 0, 0, 0, 0, 0, bytes([3]))

            self.assertEqual(objects.pending_tmp_count, 0)

            # Verify real files exist
            for i in range(3):
                real_path = chunk_tile_path(
                    project, "threshold_world", i, 0, 0,
                    platform="test_plat")
                self.assertTrue(
                    real_path.exists(),
                    f"Real file for chunk ({i},0,0) should exist")


class TestWorkspaceMovementUnloadLoad(unittest.TestCase):
    """Moving the workspace should conceptually unload far chunks
    and load new ones. When moving back, data should persist."""

    def _make_objects(self, project, config):
        return WorkspaceObjects(
            config,
            project_dir=project,
            world_name="move_world",
            platform="test_plat",
            max_tmp_chunks=9999)

    def test_move_away_and_back_preserves_data(self):
        """Write tiles, flush, simulate moving away (clear in-memory),
        then reload and verify data."""
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = self._make_objects(project, config)

            # Create chunk at origin and write data
            objects.get_or_create_chunk(0, 0, 0)
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([0xAA]))
            objects.set_tile(0, 0, 0, 7, 7, 0, bytes([0xBB]))

            # Flush to disk
            count = objects.flush_all_tmp()
            self.assertEqual(count, 1)

            # Simulate "moving away" — create fresh objects instance
            # (simulates unloading all chunks from memory)
            objects2 = self._make_objects(project, config)

            # Load chunks at a far-away location
            objects2.get_or_create_chunk(100, 100, 0)
            far_chunk = objects2.get_chunk(100, 100, 0)
            self.assertIsNotNone(far_chunk)
            self.assertTrue(
                all(b == 0 for b in far_chunk.tile_bytes),
                "Far chunk should be empty")

            # Original chunk should not be in memory
            self.assertIsNone(objects2.get_chunk(0, 0, 0))

            # "Move back" — load original chunk
            chunk = objects2.get_or_create_chunk(0, 0, 0)
            self.assertIsNotNone(chunk)

            r1 = objects2.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
            self.assertEqual(r1[0], 0xAA)

            r2 = objects2.get_tile_bytes(0, 0, 0, 7, 7, 0, 1)
            self.assertEqual(r2[0], 0xBB)

    def test_multiple_chunks_persist_across_reload(self):
        """Write to multiple chunks, flush, reload all, verify."""
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = self._make_objects(project, config)

            # Write unique data to a 3x3 grid of chunks
            for cy in range(3):
                for cx in range(3):
                    objects.get_or_create_chunk(cx, cy, 0)
                    val = (cx + cy * 3 + 1) & 0xFF
                    objects.set_tile(
                        cx, cy, 0, 0, 0, 0, bytes([val]))

            objects.flush_all_tmp()
            self.assertEqual(objects.pending_tmp_count, 0)

            # Fresh instance
            objects2 = self._make_objects(project, config)

            for cy in range(3):
                for cx in range(3):
                    objects2.get_or_create_chunk(cx, cy, 0)
                    expected = (cx + cy * 3 + 1) & 0xFF
                    result = objects2.get_tile_bytes(
                        cx, cy, 0, 0, 0, 0, 1)
                    self.assertIsNotNone(result)
                    self.assertEqual(
                        result[0], expected,
                        f"Chunk ({cx},{cy}): expected {expected}, "
                        f"got {result[0]}")


class TestCtrlSSaveAll(unittest.TestCase):
    """Test that flush_all_tmp (Ctrl+S equivalent) saves everything."""

    def test_flush_all_saves_pending(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="save_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            # Create and modify several chunks
            for i in range(5):
                objects.get_or_create_chunk(i, 0, 0)
                objects.set_tile(i, 0, 0, 0, 0, 0, bytes([i + 1]))

            self.assertEqual(objects.pending_tmp_count, 5)

            # Ctrl+S equivalent
            count = objects.flush_all_tmp()
            self.assertEqual(count, 5)
            self.assertEqual(objects.pending_tmp_count, 0)

            # Verify all real files exist
            for i in range(5):
                real_path = chunk_tile_path(
                    project, "save_world", i, 0, 0,
                    platform="test_plat")
                self.assertTrue(real_path.exists())

    def test_flush_all_clears_dirty_flags(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="save_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            objects.get_or_create_chunk(0, 0, 0)
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
            self.assertEqual(len(objects.get_dirty_chunks()), 1)

            objects.flush_all_tmp()
            self.assertEqual(len(objects.get_dirty_chunks()), 0)


class TestWorkspaceViewportMovement(unittest.TestCase):
    """Test that viewport movement correctly tracks position
    for chunk loading decisions."""

    def test_go_to_updates_viewport(self):
        movement = WorkspaceMovement()
        movement.go_to(10, 20, 3)
        self.assertEqual(movement.viewport.center_x, 10)
        self.assertEqual(movement.viewport.center_y, 20)
        self.assertEqual(movement.viewport.center_z, 3)

    def test_pan_by_tiles_updates_viewport(self):
        movement = WorkspaceMovement()
        movement.go_to(0, 0, 0)
        movement.pan_by_tiles(5, -3)
        self.assertEqual(movement.viewport.center_x, 5)
        self.assertEqual(movement.viewport.center_y, -3)

    def test_pan_by_chunks_updates_viewport(self):
        movement = WorkspaceMovement()
        movement.go_to(0, 0, 0)
        movement.pan_by_chunks(1, 1, 8, 8)
        self.assertEqual(movement.viewport.center_x, 8)
        self.assertEqual(movement.viewport.center_y, 8)


class TestTileKindNoneRendering(unittest.TestCase):
    """Verify that tile value 0 is treated as empty."""

    def test_empty_chunk_all_zeros(self):
        """Auto-created chunks should have all-zero tile bytes,
        which the renderer should display as dark empty tiles."""
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="none_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            chunk = objects.get_or_create_chunk(0, 0, 0)
            # Every tile should be 0
            for y in range(8):
                for x in range(8):
                    result = objects.get_tile_bytes(
                        0, 0, 0, x, y, 0, 1)
                    self.assertEqual(
                        result[0], 0,
                        f"Tile ({x},{y}) should be 0 (None)")

    def test_drawing_nonzero_over_none(self):
        """Drawing a non-zero tile over a None tile should work."""
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config()

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="none_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            objects.get_or_create_chunk(0, 0, 0)

            # Verify starts as 0
            before = objects.get_tile_bytes(0, 0, 0, 3, 3, 0, 1)
            self.assertEqual(before[0], 0)

            # Draw tile value 5
            objects.set_tile(0, 0, 0, 3, 3, 0, bytes([5]))

            after = objects.get_tile_bytes(0, 0, 0, 3, 3, 0, 1)
            self.assertEqual(after[0], 5)


class TestFullLifecycle(unittest.TestCase):
    """End-to-end: empty world → draw → save → reload → verify."""

    def test_full_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _make_config(chunk_w=8, chunk_h=8, chunk_d=1)
            ensure_world_dir(project, "lifecycle", "test_plat")

            # Phase 1: Create objects, load visible area
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="lifecycle",
                platform="test_plat",
                max_tmp_chunks=9999)

            # Load a 4x4 grid of chunks (simulating visible area)
            for cy in range(4):
                for cx in range(4):
                    chunk = objects.get_or_create_chunk(cx, cy, 0)
                    self.assertIsNotNone(chunk)
                    self.assertFalse(chunk.is_dirty)

            # Phase 2: Draw tiles in some chunks
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([10]))
            objects.set_tile(1, 1, 0, 4, 4, 0, bytes([20]))
            objects.set_tile(3, 3, 0, 7, 7, 0, bytes([30]))

            self.assertEqual(objects.pending_tmp_count, 3)

            # Phase 3: Ctrl+S — flush all
            count = objects.flush_all_tmp()
            self.assertEqual(count, 3)
            self.assertEqual(objects.pending_tmp_count, 0)

            # Phase 4: Simulate restart — fresh objects
            objects2 = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="lifecycle",
                platform="test_plat",
                max_tmp_chunks=9999)

            # Phase 5: Load and verify
            objects2.get_or_create_chunk(0, 0, 0)
            r1 = objects2.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
            self.assertEqual(r1[0], 10)

            objects2.get_or_create_chunk(1, 1, 0)
            r2 = objects2.get_tile_bytes(1, 1, 0, 4, 4, 0, 1)
            self.assertEqual(r2[0], 20)

            objects2.get_or_create_chunk(3, 3, 0)
            r3 = objects2.get_tile_bytes(3, 3, 0, 7, 7, 0, 1)
            self.assertEqual(r3[0], 30)

            # Unmodified chunks should still be all zeros
            objects2.get_or_create_chunk(2, 2, 0)
            r4 = objects2.get_tile_bytes(2, 2, 0, 0, 0, 0, 1)
            self.assertEqual(r4[0], 0)


if __name__ == "__main__":
    unittest.main()
