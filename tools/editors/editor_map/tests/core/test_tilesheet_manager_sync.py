"""
Tests that TilesheetManager.sync_from_config loads ALL tilesheets
listed in a world editor config.

The world config's ``tilesheets`` list is the source of truth.
TilesheetManager.sync_from_config (in core/tilesheet_manager.py)
is responsible for loading every entry in that list.
"""

from __future__ import annotations

import json
import random
import struct
import zlib
from pathlib import Path

import pytest

from core.tilesheet_manager import TilesheetManager
from core.editor_project_config import (
    WorldEditorConfig,
    load_world_editor_config,
    save_world_editor_config,
)


def _create_fake_png(path: Path, width: int = 16, height: int = 16) -> None:
    """Create a minimal valid PNG file at *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        img.save(str(path))
        return
    except ImportError:
        pass

    # Fallback: hand-craft a 1x1 RGBA PNG
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return (struct.pack(">I", len(data))
                + c + struct.pack(">I", crc))

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    raw_row = b"\x00\xff\xff\xff\xff"
    compressed = zlib.compress(raw_row)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    path.write_bytes(signature + ihdr + idat + iend)


class TestSyncFromConfigLoadsAll:
    """TilesheetManager.sync_from_config must load every tilesheet
    path present in the world config's tilesheets list."""

    @pytest.mark.parametrize("seed", range(5))
    def test_loads_all_tilesheets_from_config(self, tmp_path, seed):
        """Create a random number (2-8) of tilesheet PNGs, write them
        into a world config, then verify sync_from_config loads all."""
        rng = random.Random(seed)
        count = rng.randint(2, 8)

        # Create fake PNG files with unique names
        ts_paths = []
        for i in range(count):
            rel = f"assets/sheets/sheet_{i}.png"
            abs_path = tmp_path / rel
            _create_fake_png(abs_path)
            ts_paths.append(rel)

        # Save a world config with all tilesheet paths
        cfg = WorldEditorConfig(tilesheets=list(ts_paths))
        save_world_editor_config(tmp_path, "test_world", cfg)

        # Reload to verify persistence
        loaded_cfg = load_world_editor_config(tmp_path, "test_world")
        assert loaded_cfg.tilesheets == ts_paths

        # Sync into TilesheetManager
        mgr = TilesheetManager()
        mgr.sync_from_config(tmp_path, loaded_cfg.tilesheets)

        # Verify ALL tilesheets were loaded
        assert mgr.count == count, (
            f"Expected {count} tilesheets loaded, got {mgr.count}")
        for rel in ts_paths:
            assert mgr.has(rel), (
                f"Tilesheet '{rel}' not found in manager")
            entry = mgr.get(rel)
            assert entry is not None
            assert entry.tilesheet is not None, (
                f"Tilesheet '{rel}' entry exists but tilesheet is None")

    def test_missing_files_are_skipped(self, tmp_path):
        """Paths that don't exist on disk are skipped, but valid
        ones are still loaded."""
        # Create only 2 of 4 files
        existing = []
        missing = []
        for i in range(4):
            rel = f"assets/sheet_{i}.png"
            if i % 2 == 0:
                _create_fake_png(tmp_path / rel)
                existing.append(rel)
            else:
                missing.append(rel)

        all_paths = existing + missing

        mgr = TilesheetManager()
        mgr.sync_from_config(tmp_path, all_paths)

        # Only existing files should be loaded
        assert mgr.count == len(existing)
        for rel in existing:
            assert mgr.has(rel)
        for rel in missing:
            assert not mgr.has(rel)

    def test_sync_removes_stale_entries(self, tmp_path):
        """Entries no longer in the config list are removed."""
        paths = []
        for i in range(3):
            rel = f"assets/sheet_{i}.png"
            _create_fake_png(tmp_path / rel)
            paths.append(rel)

        mgr = TilesheetManager()
        mgr.sync_from_config(tmp_path, paths)
        assert mgr.count == 3

        # Now sync with only the first path
        mgr.sync_from_config(tmp_path, [paths[0]])
        assert mgr.count == 1
        assert mgr.has(paths[0])
        assert not mgr.has(paths[1])
        assert not mgr.has(paths[2])

    def test_sync_idempotent(self, tmp_path):
        """Calling sync twice with the same list doesn't duplicate."""
        paths = []
        for i in range(3):
            rel = f"assets/sheet_{i}.png"
            _create_fake_png(tmp_path / rel)
            paths.append(rel)

        mgr = TilesheetManager()
        mgr.sync_from_config(tmp_path, paths)
        assert mgr.count == 3

        mgr.sync_from_config(tmp_path, paths)
        assert mgr.count == 3
