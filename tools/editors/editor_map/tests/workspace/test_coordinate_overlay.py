"""
Tests for workspace coordinate conversion and chunk grid alignment.

Verifies that screen_to_tile, tile_to_screen, and
get_chunk_grid_params produce correct results for various
viewport states.
"""

from __future__ import annotations

import math
import pytest

from workspace.movement import WorkspaceMovement, DEFAULT_TILE_PX


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _make_movement(
        center_x: int = 0,
        center_y: int = 0,
        zoom: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
) -> WorkspaceMovement:
    m = WorkspaceMovement()
    m.viewport.center_x = center_x
    m.viewport.center_y = center_y
    m.viewport.zoom = zoom
    m.viewport.offset_x = offset_x
    m.viewport.offset_y = offset_y
    return m


# Workspace area: 160x160 screen pixels, origin at (100, 50)
WS_OX, WS_OY = 100.0, 50.0
WS_W, WS_H = 160.0, 160.0
# Center of workspace in screen coords
WS_CX = WS_OX + WS_W * 0.5   # 180
WS_CY = WS_OY + WS_H * 0.5   # 130


# ------------------------------------------------------------------ #
# screen_to_tile
# ------------------------------------------------------------------ #

class TestScreenToTile:
    """Verify screen → tile coordinate conversion."""

    def test_center_of_workspace_is_viewport_center(self):
        """Mouse at workspace center → viewport center tile."""
        m = _make_movement(center_x=5, center_y=10)
        tx, ty = m.screen_to_tile(WS_CX, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 5
        assert ty == 10

    def test_one_tile_right_of_center(self):
        """Mouse one tile-width to the right of center."""
        m = _make_movement(center_x=0, center_y=0)
        tile_px = DEFAULT_TILE_PX  # 8
        tx, ty = m.screen_to_tile(
            WS_CX + tile_px, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 1
        assert ty == 0

    def test_one_tile_below_center(self):
        m = _make_movement(center_x=0, center_y=0)
        tile_px = DEFAULT_TILE_PX
        tx, ty = m.screen_to_tile(
            WS_CX, WS_CY + tile_px, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 0
        assert ty == 1

    def test_negative_direction(self):
        """Mouse one tile left and up from center → (-1, -1)."""
        m = _make_movement(center_x=0, center_y=0)
        tile_px = DEFAULT_TILE_PX
        # Just inside the (-1, -1) tile
        tx, ty = m.screen_to_tile(
            WS_CX - 1, WS_CY - 1, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == -1
        assert ty == -1

    def test_zoom_2x(self):
        """At 2x zoom each tile is 16 screen pixels wide."""
        m = _make_movement(center_x=0, center_y=0, zoom=2.0)
        scaled = DEFAULT_TILE_PX * 2  # 16
        tx, ty = m.screen_to_tile(
            WS_CX + scaled, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 1
        assert ty == 0

    def test_zoom_half(self):
        """At 0.5x zoom each tile is 4 screen pixels wide."""
        m = _make_movement(center_x=0, center_y=0, zoom=0.5)
        scaled = DEFAULT_TILE_PX * 0.5  # 4
        tx, ty = m.screen_to_tile(
            WS_CX + scaled, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 1
        assert ty == 0

    def test_with_offset(self):
        """Sub-tile offset shifts the mapping."""
        m = _make_movement(center_x=0, center_y=0, offset_x=4.0)
        # offset_x=4 means the viewport is shifted 4 pixels right,
        # so the center of the screen shows tile 0 shifted.
        # At center screen, dx=0, but offset adds 4*zoom=4 pixels.
        # floor((0 + 4) / 8) = floor(0.5) = 0 → still tile 0
        tx, ty = m.screen_to_tile(WS_CX, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 0
        assert ty == 0

        # 4 pixels left of center: dx=-4, +offset 4 → 0 → tile 0
        tx2, _ = m.screen_to_tile(
            WS_CX - 4, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx2 == 0

        # 5 pixels left of center: dx=-5, +offset 4 → -1 → tile -1
        tx3, _ = m.screen_to_tile(
            WS_CX - 5, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx3 == -1

    def test_after_scroll_movement(self):
        """After scrolling, screen_to_tile reflects new center."""
        m = _make_movement()
        m.scroll_vertical(3.0)  # center_y -= 3
        assert m.viewport.center_y == -3
        tx, ty = m.screen_to_tile(WS_CX, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 0
        assert ty == -3

    def test_after_pan_by_tiles(self):
        m = _make_movement()
        m.pan_by_tiles(5, -2)
        tx, ty = m.screen_to_tile(WS_CX, WS_CY, WS_OX, WS_OY, WS_W, WS_H)
        assert tx == 5
        assert ty == -2


# ------------------------------------------------------------------ #
# tile_to_screen
# ------------------------------------------------------------------ #

class TestTileToScreen:
    """Verify tile → screen coordinate conversion."""

    def test_center_tile_maps_to_workspace_center(self):
        m = _make_movement(center_x=5, center_y=10)
        sx, sy = m.tile_to_screen(5, 10, WS_OX, WS_OY, WS_W, WS_H)
        assert sx == pytest.approx(WS_CX)
        assert sy == pytest.approx(WS_CY)

    def test_roundtrip_screen_tile_screen(self):
        """screen→tile→screen should return the tile's top-left."""
        m = _make_movement(center_x=3, center_y=7, zoom=2.0)
        # Pick an arbitrary screen point
        test_sx, test_sy = WS_CX + 20, WS_CY - 10
        tx, ty = m.screen_to_tile(
            test_sx, test_sy, WS_OX, WS_OY, WS_W, WS_H)
        # Convert back — should get the top-left of that tile
        sx, sy = m.tile_to_screen(
            tx, ty, WS_OX, WS_OY, WS_W, WS_H)
        # The returned screen pos should be <= the input
        # (top-left of the tile containing the point)
        scaled = DEFAULT_TILE_PX * 2.0
        assert sx <= test_sx < sx + scaled
        assert sy <= test_sy < sy + scaled

    def test_adjacent_tiles_differ_by_tile_size(self):
        m = _make_movement(center_x=0, center_y=0, zoom=1.0)
        sx0, sy0 = m.tile_to_screen(0, 0, WS_OX, WS_OY, WS_W, WS_H)
        sx1, sy1 = m.tile_to_screen(1, 0, WS_OX, WS_OY, WS_W, WS_H)
        sx2, sy2 = m.tile_to_screen(0, 1, WS_OX, WS_OY, WS_W, WS_H)
        assert sx1 - sx0 == pytest.approx(DEFAULT_TILE_PX)
        assert sy1 == pytest.approx(sy0)
        assert sy2 - sy0 == pytest.approx(DEFAULT_TILE_PX)
        assert sx2 == pytest.approx(sx0)


# ------------------------------------------------------------------ #
# Chunk grid alignment
# ------------------------------------------------------------------ #

class TestChunkGridParams:
    """Verify chunk grid lines align with actual chunk boundaries."""

    def test_grid_lines_pass_through_origin(self):
        """With viewport at (0,0), a grid line should pass through
        the screen position of world tile (0,0)."""
        m = _make_movement(center_x=0, center_y=0)
        chunk_w, chunk_h = 8, 8
        (fvx, vstep, fhy, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, chunk_w, chunk_h)

        # Screen position of tile (0, 0)
        origin_sx, origin_sy = m.tile_to_screen(
            0, 0, WS_OX, WS_OY, WS_W, WS_H)

        # origin_sx should be reachable from fvx by integer steps
        if vstep > 0:
            n = (origin_sx - fvx) / vstep
            assert n == pytest.approx(round(n), abs=1e-6)

        if hstep > 0:
            n = (origin_sy - fhy) / hstep
            assert n == pytest.approx(round(n), abs=1e-6)

    def test_grid_step_equals_chunk_size_in_pixels(self):
        """Grid step should be chunk_dim * tile_px * zoom."""
        m = _make_movement(zoom=2.0)
        chunk_w, chunk_h = 8, 8
        (_, vstep, _, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, chunk_w, chunk_h)
        expected_v = chunk_w * DEFAULT_TILE_PX * 2.0
        expected_h = chunk_h * DEFAULT_TILE_PX * 2.0
        assert vstep == pytest.approx(expected_v)
        assert hstep == pytest.approx(expected_h)

    def test_first_line_is_at_or_before_workspace_edge(self):
        """First grid line should be at or before the workspace edge."""
        m = _make_movement(center_x=37, center_y=21)
        (fvx, vstep, fhy, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, 8, 8)
        assert fvx <= WS_OX + 1e-6
        assert fhy <= WS_OY + 1e-6

    def test_grid_aligned_after_scroll(self):
        """After scrolling, grid lines still align to chunk boundaries."""
        m = _make_movement()
        m.scroll_vertical(16.0)  # Move 16 tiles (2 chunks of 8)
        chunk_w, chunk_h = 8, 8
        (fvx, vstep, fhy, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, chunk_w, chunk_h)

        # Tile (0, 0) should still be on a grid line
        origin_sx, origin_sy = m.tile_to_screen(
            0, 0, WS_OX, WS_OY, WS_W, WS_H)

        if vstep > 0:
            n = (origin_sx - fvx) / vstep
            assert n == pytest.approx(round(n), abs=1e-6)

        if hstep > 0:
            n = (origin_sy - fhy) / hstep
            assert n == pytest.approx(round(n), abs=1e-6)

    def test_grid_aligned_after_pan_by_chunks(self):
        """After panning by chunks, grid lines remain aligned."""
        m = _make_movement()
        m.pan_by_chunks(3, -2, chunk_width=8, chunk_height=8)
        (fvx, vstep, fhy, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, 8, 8)

        # Chunk boundary at (0,0) should be on a grid line
        origin_sx, origin_sy = m.tile_to_screen(
            0, 0, WS_OX, WS_OY, WS_W, WS_H)

        if vstep > 0:
            n = (origin_sx - fvx) / vstep
            assert n == pytest.approx(round(n), abs=1e-6)

        if hstep > 0:
            n = (origin_sy - fhy) / hstep
            assert n == pytest.approx(round(n), abs=1e-6)

    def test_non_square_chunks(self):
        """Grid works with non-square chunk dimensions."""
        m = _make_movement()
        chunk_w, chunk_h = 16, 4
        (_, vstep, _, hstep, _, _) = m.get_chunk_grid_params(
            WS_OX, WS_OY, WS_W, WS_H, chunk_w, chunk_h)
        assert vstep == pytest.approx(chunk_w * DEFAULT_TILE_PX)
        assert hstep == pytest.approx(chunk_h * DEFAULT_TILE_PX)
