"""
Unit tests for WorkspaceObjects serialization:
- .tmp file creation on set_tile
- Checksum verification
- Auto-save threshold flush
- Chunk loading from disk / empty creation
- Global space deserialization with default config
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.engine_config import EngineConfig
from workspace.objects import (
    ChunkData,
    WorkspaceObjects,
    compute_checksum,
    verify_tmp_checksum,
)
from core.world_directory import (
    chunk_tile_path,
    chunk_tile_tmp_path,
    ensure_chunk_dir,
)


def _default_config(
        chunk_w: int = 8,
        chunk_h: int = 8,
        chunk_d: int = 2) -> EngineConfig:
    return EngineConfig(constants={
        'CHUNK__WIDTH': chunk_w,
        'CHUNK__HEIGHT': chunk_h,
        'CHUNK__DEPTH': chunk_d,
        'CHUNK__QUANTITY_OF__TILES': chunk_w * chunk_h * chunk_d,
    })


class TestChecksum(unittest.TestCase):

    def test_compute_checksum_deterministic(self):
        data = b'\x00\x01\x02\x03'
        c1 = compute_checksum(data)
        c2 = compute_checksum(data)
        self.assertEqual(c1, c2)

    def test_compute_checksum_differs_for_different_data(self):
        c1 = compute_checksum(b'\x00')
        c2 = compute_checksum(b'\x01')
        self.assertNotEqual(c1, c2)

    def test_verify_tmp_checksum_valid(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "t.tmp"
            sha = Path(td) / "t.tmp.sha256"
            data = b'\xAA\xBB\xCC'
            tmp.write_bytes(data)
            sha.write_text(compute_checksum(data), encoding='utf-8')
            self.assertTrue(verify_tmp_checksum(tmp))

    def test_verify_tmp_checksum_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "t.tmp"
            sha = Path(td) / "t.tmp.sha256"
            tmp.write_bytes(b'\xAA\xBB\xCC')
            sha.write_text("bad_checksum", encoding='utf-8')
            self.assertFalse(verify_tmp_checksum(tmp))

    def test_verify_tmp_checksum_missing_files(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "t.tmp"
            self.assertFalse(verify_tmp_checksum(tmp))


class TestTmpFileCreation(unittest.TestCase):
    """Test that set_tile creates .tmp files."""

    def test_set_tile_creates_tmp_file(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=100)

            total = 8 * 8 * 1
            chunk = ChunkData(0, 0, 0, bytearray(total))
            objects._put_chunk(chunk)

            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([42]))

            tmp_path = chunk_tile_tmp_path(
                project, "test_world", 0, 0, 0,
                platform="test_plat")
            self.assertTrue(tmp_path.exists())

            sha_path = tmp_path.with_suffix(
                tmp_path.suffix + ".sha256")
            self.assertTrue(sha_path.exists())

    def test_set_tile_increments_pending_count(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=100)

            chunk = ChunkData(0, 0, 0, bytearray(64))
            objects._put_chunk(chunk)

            self.assertEqual(objects.pending_tmp_count, 0)
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
            self.assertEqual(objects.pending_tmp_count, 1)


class TestAutoSaveThreshold(unittest.TestCase):
    """Test that auto-save triggers at max_tmp_chunks."""

    def test_flush_triggers_at_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=3)

            for i in range(3):
                chunk = ChunkData(i, 0, 0, bytearray(64))
                objects._put_chunk(chunk)

            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
            objects.set_tile(1, 0, 0, 0, 0, 0, bytes([2]))
            self.assertEqual(objects.pending_tmp_count, 2)

            # Third set_tile triggers flush (threshold=3)
            objects.set_tile(2, 0, 0, 0, 0, 0, bytes([3]))
            self.assertEqual(objects.pending_tmp_count, 0)

    def test_flush_promotes_tmp_to_real_file(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=1)

            chunk = ChunkData(0, 0, 0, bytearray(64))
            objects._put_chunk(chunk)

            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([99]))

            real_path = chunk_tile_path(
                project, "test_world", 0, 0, 0,
                platform="test_plat")
            self.assertTrue(real_path.exists())

            tmp_path = chunk_tile_tmp_path(
                project, "test_world", 0, 0, 0,
                platform="test_plat")
            self.assertFalse(tmp_path.exists())

    def test_flush_clears_dirty_flag(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)
            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=1)

            chunk = ChunkData(0, 0, 0, bytearray(64))
            objects._put_chunk(chunk)
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))

            loaded = objects.get_chunk(0, 0, 0)
            self.assertFalse(loaded.is_dirty)


class TestChunkLoadFromDisk(unittest.TestCase):
    """Test loading chunks from disk and empty creation."""

    def test_load_existing_chunk_from_disk(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)

            ensure_chunk_dir(
                project, "test_world", 5, 3, 0,
                platform="test_plat")
            tile_path = chunk_tile_path(
                project, "test_world", 5, 3, 0,
                platform="test_plat")
            tile_data = bytearray(64)
            tile_data[0] = 0xAB
            tile_path.write_bytes(tile_data)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat")

            chunk = objects.get_or_create_chunk(5, 3, 0)
            self.assertIsNotNone(chunk)
            self.assertEqual(chunk.tile_bytes[0], 0xAB)
            self.assertFalse(chunk.is_dirty)

    def test_create_empty_chunk_when_file_missing(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat")

            chunk = objects.get_or_create_chunk(99, 99, 0)
            self.assertIsNotNone(chunk)
            self.assertEqual(chunk.chunk_x, 99)
            self.assertEqual(chunk.chunk_y, 99)
            self.assertFalse(chunk.is_dirty)
            self.assertTrue(all(b == 0 for b in chunk.tile_bytes))

    def test_created_chunk_is_publicly_accessible(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat")

            objects.get_or_create_chunk(10, 20, 0)
            chunk = objects.get_chunk(10, 20, 0)
            self.assertIsNotNone(chunk)


class TestGlobalSpaceDeserialization(unittest.TestCase):
    """Test round-trip serialization with default engine config."""

    def test_round_trip_default_config(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(
                chunk_w=8, chunk_h=8, chunk_d=2)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="round_trip",
                platform="test_plat",
                max_tmp_chunks=9999)

            chunk = ChunkData(
                1, 2, 0,
                bytearray(8 * 8 * 2))
            objects._put_chunk(chunk)

            objects.set_tile(1, 2, 0, 0, 0, 0, bytes([0xAA]))
            objects.set_tile(1, 2, 0, 7, 7, 0, bytes([0xBB]))
            objects.set_tile(1, 2, 0, 3, 3, 1, bytes([0xCC]))

            count = objects.flush_all_tmp()
            self.assertEqual(count, 1)

            objects2 = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="round_trip",
                platform="test_plat")

            chunk2 = objects2.get_or_create_chunk(1, 2, 0)
            self.assertIsNotNone(chunk2)

            r1 = objects2.get_tile_bytes(1, 2, 0, 0, 0, 0, 1)
            self.assertEqual(r1[0], 0xAA)

            r2 = objects2.get_tile_bytes(1, 2, 0, 7, 7, 0, 1)
            self.assertEqual(r2[0], 0xBB)

            r3 = objects2.get_tile_bytes(1, 2, 0, 3, 3, 1, 1)
            self.assertEqual(r3[0], 0xCC)

    def test_round_trip_2d_world(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(
                chunk_w=8, chunk_h=8, chunk_d=1)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="flat_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            chunk = ChunkData(0, 0, 0, bytearray(64))
            objects._put_chunk(chunk)

            for y in range(8):
                for x in range(8):
                    val = (x + y * 8) & 0xFF
                    objects.set_tile(
                        0, 0, 0, x, y, 0, bytes([val]))

            objects.flush_all_tmp()

            objects2 = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="flat_world",
                platform="test_plat")

            objects2.get_or_create_chunk(0, 0, 0)
            for y in range(8):
                for x in range(8):
                    expected = (x + y * 8) & 0xFF
                    result = objects2.get_tile_bytes(
                        0, 0, 0, x, y, 0, 1)
                    self.assertEqual(
                        result[0], expected,
                        f"Tile ({x},{y}): expected {expected}, "
                        f"got {result[0]}")


class TestChecksumFailure(unittest.TestCase):
    """Test that corrupted .tmp files are not promoted."""

    def test_corrupted_tmp_not_promoted(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            config = _default_config(chunk_d=1)

            objects = WorkspaceObjects(
                config,
                project_dir=project,
                world_name="test_world",
                platform="test_plat",
                max_tmp_chunks=9999)

            chunk = ChunkData(0, 0, 0, bytearray(64))
            objects._put_chunk(chunk)
            objects.set_tile(0, 0, 0, 0, 0, 0, bytes([42]))

            tmp_path = chunk_tile_tmp_path(
                project, "test_world", 0, 0, 0,
                platform="test_plat")
            tmp_path.write_bytes(b'\xFF' * 100)

            result = objects.flush_single_tmp(0, 0, 0)
            self.assertFalse(result)

            real_path = chunk_tile_path(
                project, "test_world", 0, 0, 0,
                platform="test_plat")
            self.assertFalse(real_path.exists())


if __name__ == "__main__":
    unittest.main()
