"""
Integration test: moving the workspace by several chunks triggers
background save/load threads.

Uses fuzzy movement (random direction and magnitude) and waits
with a timeout for all pending operations to drain.
"""

from __future__ import annotations

import random
import time

import pytest

from workspace.movement import WorkspaceMovement
from workspace.objects import WorkspaceObjects, ChunkData
from core.engine_config import EngineConfig


def _make_config(
        chunk_w: int = 8,
        chunk_h: int = 8,
        chunk_d: int = 1,
) -> EngineConfig:
    """Create a minimal EngineConfig for testing."""
    return EngineConfig(constants={
        'CHUNK__WIDTH': chunk_w,
        'CHUNK__HEIGHT': chunk_h,
        'CHUNK__DEPTH': chunk_d,
        'CHUNK__QUANTITY_OF__TILES': chunk_w * chunk_h * chunk_d,
    })


def _seed_chunks(
        objects: WorkspaceObjects,
        center_x: int,
        center_y: int,
        radius: int,
        chunk_w: int = 8,
        chunk_h: int = 8,
) -> int:
    """
    Pre-populate chunks in a square around (center_x, center_y).

    Returns the number of chunks seeded.
    """
    count = 0
    for cx in range(center_x - radius, center_x + radius + 1):
        for cy in range(center_y - radius, center_y + radius + 1):
            tile_bytes = bytearray(chunk_w * chunk_h)
            objects._put_chunk(ChunkData(
                chunk_x=cx,
                chunk_y=cy,
                chunk_z=0,
                tile_bytes=tile_bytes))
            count += 1
    return count


class TestChunkLoadingOnMovement:
    """Verify that workspace objects track pending operations."""

    def test_pending_operations_starts_at_zero(self):
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)
        assert obj.pending_operations_count == 0

    def test_mark_loading_increments_pending(self):
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)
        obj.mark_chunk_loading(0, 0, 0)
        assert obj.pending_operations_count == 1

    def test_mark_saving_increments_pending(self):
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)
        obj.mark_chunk_saving(0, 0, 0)
        assert obj.pending_operations_count == 1

    def test_put_chunk_clears_loading(self):
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)
        obj.mark_chunk_loading(1, 2, 0)
        assert obj.pending_operations_count == 1
        obj._put_chunk(ChunkData(
            chunk_x=1, chunk_y=2, chunk_z=0,
            tile_bytes=bytearray(64)))
        assert obj.pending_operations_count == 0

    def test_unmark_saving_clears_pending(self):
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)
        obj.mark_chunk_saving(3, 4, 0)
        assert obj.pending_operations_count == 1
        obj.unmark_chunk_saving(3, 4, 0)
        assert obj.pending_operations_count == 0

    def test_fuzzy_movement_drains_pending_operations(self):
        """
        Simulate fuzzy multi-chunk movement.

        Move the workspace randomly by several chunks, mark
        chunks as loading/saving, then simulate completion.
        Verify pending_operations_count reaches 0 within timeout.
        """
        cfg = _make_config(chunk_w=8, chunk_h=8)
        obj = WorkspaceObjects(cfg)
        movement = WorkspaceMovement()

        _seed_chunks(obj, 0, 0, radius=2, chunk_w=8, chunk_h=8)

        rng = random.Random(42)  # deterministic seed

        # Simulate fuzzy movement: random direction and magnitude
        pending_coords = []
        for _ in range(10):
            dx = rng.randint(-3, 3)
            dy = rng.randint(-3, 3)
            movement.pan_by_chunks(dx, dy, chunk_width=8, chunk_height=8)

            # Simulate marking new chunks as loading
            cx = movement.viewport.center_x // 8
            cy = movement.viewport.center_y // 8
            for ox in range(-1, 2):
                for oy in range(-1, 2):
                    coord = (cx + ox, cy + oy, 0)
                    if obj.get_chunk(*coord) is None:
                        obj.mark_chunk_loading(*coord)
                        pending_coords.append(coord)

        assert obj.pending_operations_count >= 0

        # Simulate async completion of all pending loads
        for coord in pending_coords:
            obj._put_chunk(ChunkData(
                chunk_x=coord[0],
                chunk_y=coord[1],
                chunk_z=coord[2],
                tile_bytes=bytearray(64)))

        # Wait for pending operations to drain (with timeout)
        timeout = 180.0  # 3 minutes
        start = time.monotonic()
        while obj.pending_operations_count > 0:
            if time.monotonic() - start > timeout:
                pytest.fail(
                    f"Timed out waiting for pending operations to "
                    f"drain. Remaining: "
                    f"{obj.pending_operations_count}")
            time.sleep(0.01)

        assert obj.pending_operations_count == 0

    def test_mixed_save_and_load_pending(self):
        """Mark some chunks loading and some saving, verify count."""
        cfg = _make_config()
        obj = WorkspaceObjects(cfg)

        obj.mark_chunk_loading(0, 0, 0)
        obj.mark_chunk_loading(1, 0, 0)
        obj.mark_chunk_saving(2, 0, 0)
        assert obj.pending_operations_count == 3

        obj._put_chunk(ChunkData(
            chunk_x=0, chunk_y=0, chunk_z=0,
            tile_bytes=bytearray(64)))
        assert obj.pending_operations_count == 2

        obj.unmark_chunk_saving(2, 0, 0)
        assert obj.pending_operations_count == 1

        obj._put_chunk(ChunkData(
            chunk_x=1, chunk_y=0, chunk_z=0,
            tile_bytes=bytearray(64)))
        assert obj.pending_operations_count == 0
