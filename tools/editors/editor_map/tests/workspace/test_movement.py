"""
Tests for workspace viewport movement.

Covers: pan_by_tiles, pan_by_chunks, move_z, go_to,
        pan_by_pixels, scroll_vertical, scroll_horizontal,
        set_zoom, adjust_zoom.
"""

from __future__ import annotations

from workspace.movement import (
    DEFAULT_TILE_PX,
    SCROLL_SENSITIVITY,
    ViewportState,
    WorkspaceMovement,
)


# ── ViewportState defaults ────────────────────────────────────

class TestViewportStateDefaults:
    def test_defaults(self):
        v = ViewportState()
        assert v.center_x == 0
        assert v.center_y == 0
        assert v.center_z == 0
        assert v.offset_x == 0.0
        assert v.offset_y == 0.0
        assert v.zoom == 1.0
        assert v._scroll_accum_x == 0.0
        assert v._scroll_accum_y == 0.0


# ── pan_by_tiles ──────────────────────────────────────────────

class TestPanByTiles:
    def test_pan_right_and_down(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(3, 5)
        assert m.viewport.center_x == 3
        assert m.viewport.center_y == 5

    def test_pan_left_and_up(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(-2, -4)
        assert m.viewport.center_x == -2
        assert m.viewport.center_y == -4

    def test_pan_accumulates(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(1, 1)
        m.pan_by_tiles(2, 3)
        assert m.viewport.center_x == 3
        assert m.viewport.center_y == 4

    def test_pan_zero(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(5, 5)
        m.pan_by_tiles(0, 0)
        assert m.viewport.center_x == 5
        assert m.viewport.center_y == 5


# ── pan_by_chunks ─────────────────────────────────────────────

class TestPanByChunks:
    def test_default_chunk_size(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(1, 1)
        assert m.viewport.center_x == 8
        assert m.viewport.center_y == 8

    def test_custom_chunk_size(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(2, 3, chunk_width=16, chunk_height=16)
        assert m.viewport.center_x == 32
        assert m.viewport.center_y == 48

    def test_negative_chunks(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(-1, -2)
        assert m.viewport.center_x == -8
        assert m.viewport.center_y == -16


# ── move_z ────────────────────────────────────────────────────

class TestMoveZ:
    def test_move_up(self):
        m = WorkspaceMovement()
        m.move_z(1)
        assert m.viewport.center_z == 1

    def test_move_down(self):
        m = WorkspaceMovement()
        m.move_z(-3)
        assert m.viewport.center_z == -3

    def test_accumulates(self):
        m = WorkspaceMovement()
        m.move_z(2)
        m.move_z(3)
        assert m.viewport.center_z == 5


# ── go_to ─────────────────────────────────────────────────────

class TestGoTo:
    def test_go_to_resets_offsets(self):
        m = WorkspaceMovement()
        m.pan_by_pixels(10.5, 20.3)
        m.go_to(100, 200, 5)
        assert m.viewport.center_x == 100
        assert m.viewport.center_y == 200
        assert m.viewport.center_z == 5
        assert m.viewport.offset_x == 0.0
        assert m.viewport.offset_y == 0.0

    def test_go_to_resets_scroll_accumulators(self):
        m = WorkspaceMovement()
        m.scroll_vertical(0.3)
        m.scroll_horizontal(0.7)
        m.go_to(0, 0, 0)
        assert m.viewport._scroll_accum_x == 0.0
        assert m.viewport._scroll_accum_y == 0.0

    def test_go_to_negative_coords(self):
        m = WorkspaceMovement()
        m.go_to(-50, -100, -2)
        assert m.viewport.center_x == -50
        assert m.viewport.center_y == -100
        assert m.viewport.center_z == -2


# ── pan_by_pixels ─────────────────────────────────────────────

class TestPanByPixels:
    def test_positive_offset(self):
        m = WorkspaceMovement()
        m.pan_by_pixels(3.5, 7.2)
        assert abs(m.viewport.offset_x - 3.5) < 1e-9
        assert abs(m.viewport.offset_y - 7.2) < 1e-9

    def test_accumulates(self):
        m = WorkspaceMovement()
        m.pan_by_pixels(1.0, 2.0)
        m.pan_by_pixels(0.5, 0.5)
        assert abs(m.viewport.offset_x - 1.5) < 1e-9
        assert abs(m.viewport.offset_y - 2.5) < 1e-9


# ── scroll_vertical ───────────────────────────────────────────

class TestScrollVertical:
    """Positive delta → workspace up → center_y decreases."""

    def test_single_tick_up(self):
        m = WorkspaceMovement()
        m.scroll_vertical(1.0)
        assert m.viewport.center_y == -1

    def test_single_tick_down(self):
        m = WorkspaceMovement()
        m.scroll_vertical(-1.0)
        assert m.viewport.center_y == 1

    def test_multiple_ticks(self):
        m = WorkspaceMovement()
        m.scroll_vertical(3.0)
        assert m.viewport.center_y == -3

    def test_fractional_accumulation(self):
        """Three 0.4 ticks = 1.2 → 1 tile moved, 0.2 remaining."""
        m = WorkspaceMovement()
        m.scroll_vertical(0.4)
        assert m.viewport.center_y == 0
        m.scroll_vertical(0.4)
        assert m.viewport.center_y == 0
        m.scroll_vertical(0.4)
        assert m.viewport.center_y == -1
        assert abs(m.viewport._scroll_accum_y - 0.2) < 1e-5

    def test_fractional_negative_accumulation(self):
        m = WorkspaceMovement()
        m.scroll_vertical(-0.6)
        assert m.viewport.center_y == 0
        m.scroll_vertical(-0.6)
        assert m.viewport.center_y == 1
        assert abs(m.viewport._scroll_accum_y - (-0.2)) < 1e-5

    def test_zero_delta_no_change(self):
        m = WorkspaceMovement()
        m.scroll_vertical(0.0)
        assert m.viewport.center_y == 0
        assert m.viewport._scroll_accum_y == 0.0

    def test_does_not_affect_x(self):
        m = WorkspaceMovement()
        m.scroll_vertical(5.0)
        assert m.viewport.center_x == 0


# ── scroll_horizontal ─────────────────────────────────────────

class TestScrollHorizontal:
    """Positive delta → workspace left → center_x decreases."""

    def test_single_tick_left(self):
        m = WorkspaceMovement()
        m.scroll_horizontal(1.0)
        assert m.viewport.center_x == -1

    def test_single_tick_right(self):
        m = WorkspaceMovement()
        m.scroll_horizontal(-1.0)
        assert m.viewport.center_x == 1

    def test_multiple_ticks(self):
        m = WorkspaceMovement()
        m.scroll_horizontal(4.0)
        assert m.viewport.center_x == -4

    def test_fractional_accumulation(self):
        m = WorkspaceMovement()
        m.scroll_horizontal(0.5)
        assert m.viewport.center_x == 0
        m.scroll_horizontal(0.5)
        assert m.viewport.center_x == -1
        assert abs(m.viewport._scroll_accum_x) < 1e-5

    def test_does_not_affect_y(self):
        m = WorkspaceMovement()
        m.scroll_horizontal(5.0)
        assert m.viewport.center_y == 0


# ── combined scroll ───────────────────────────────────────────

class TestScrollCombined:
    def test_independent_axes(self):
        m = WorkspaceMovement()
        m.scroll_vertical(2.0)
        m.scroll_horizontal(3.0)
        assert m.viewport.center_y == -2
        assert m.viewport.center_x == -3

    def test_mixed_directions(self):
        m = WorkspaceMovement()
        m.scroll_vertical(1.0)
        m.scroll_vertical(-2.0)
        m.scroll_horizontal(-1.0)
        m.scroll_horizontal(3.0)
        assert m.viewport.center_y == 1
        assert m.viewport.center_x == -2


# ── set_zoom ──────────────────────────────────────────────────

class TestSetZoom:
    def test_normal_zoom(self):
        m = WorkspaceMovement()
        m.set_zoom(2.0)
        assert abs(m.viewport.zoom - 2.0) < 1e-9

    def test_clamp_low(self):
        m = WorkspaceMovement()
        m.set_zoom(0.1)
        assert abs(m.viewport.zoom - 0.25) < 1e-9

    def test_clamp_high(self):
        m = WorkspaceMovement()
        m.set_zoom(32.0)
        assert abs(m.viewport.zoom - 16.0) < 1e-9

    def test_boundary_low(self):
        m = WorkspaceMovement()
        m.set_zoom(0.25)
        assert abs(m.viewport.zoom - 0.25) < 1e-9

    def test_boundary_high(self):
        m = WorkspaceMovement()
        m.set_zoom(16.0)
        assert abs(m.viewport.zoom - 16.0) < 1e-9


# ── adjust_zoom ───────────────────────────────────────────────

class TestAdjustZoom:
    def test_zoom_in(self):
        m = WorkspaceMovement()
        m.set_zoom(2.0)
        m.adjust_zoom(2.0)
        assert abs(m.viewport.zoom - 4.0) < 1e-9

    def test_zoom_out(self):
        m = WorkspaceMovement()
        m.set_zoom(4.0)
        m.adjust_zoom(0.5)
        assert abs(m.viewport.zoom - 2.0) < 1e-9

    def test_clamp_on_adjust(self):
        m = WorkspaceMovement()
        m.set_zoom(10.0)
        m.adjust_zoom(5.0)
        assert abs(m.viewport.zoom - 16.0) < 1e-9


# ── arrow key simulation ─────────────────────────────────────

class TestArrowKeySimulation:
    """Simulate arrow keys: move by 1 tile (spec section 1.1)."""

    def test_arrow_up(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(0, -1)
        assert m.viewport.center_y == -1

    def test_arrow_down(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(0, 1)
        assert m.viewport.center_y == 1

    def test_arrow_left(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(-1, 0)
        assert m.viewport.center_x == -1

    def test_arrow_right(self):
        m = WorkspaceMovement()
        m.pan_by_tiles(1, 0)
        assert m.viewport.center_x == 1

    def test_sequence_of_arrows(self):
        """right, right, up, left, down → (1, 0)."""
        m = WorkspaceMovement()
        m.pan_by_tiles(1, 0)
        m.pan_by_tiles(1, 0)
        m.pan_by_tiles(0, -1)
        m.pan_by_tiles(-1, 0)
        m.pan_by_tiles(0, 1)
        assert m.viewport.center_x == 1
        assert m.viewport.center_y == 0


# ── shift+arrow chunk pan simulation ─────────────────────────

class TestShiftArrowChunkPan:
    """Shift+Arrow moves by whole chunks (spec section 1.1)."""

    def test_shift_right(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(1, 0)
        assert m.viewport.center_x == 8

    def test_shift_left(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(-1, 0)
        assert m.viewport.center_x == -8

    def test_shift_up(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(0, -1)
        assert m.viewport.center_y == -8

    def test_shift_down(self):
        m = WorkspaceMovement()
        m.pan_by_chunks(0, 1)
        assert m.viewport.center_y == 8


# ── rapid scroll simulation ──────────────────────────────────

class TestRapidScrollSimulation:
    """Simulate rapid scroll wheel events in sequence."""

    def test_rapid_scroll_up_10_ticks(self):
        m = WorkspaceMovement()
        for _ in range(10):
            m.scroll_vertical(1.0)
        assert m.viewport.center_y == -10

    def test_rapid_scroll_down_then_up(self):
        m = WorkspaceMovement()
        for _ in range(5):
            m.scroll_vertical(-1.0)
        for _ in range(3):
            m.scroll_vertical(1.0)
        assert m.viewport.center_y == 2  # net: -5 + 3 = -2 → y=2

    def test_high_resolution_trackpad_many_small_deltas(self):
        """Simulate 20 tiny scroll events of 0.1 each → 2 tiles."""
        m = WorkspaceMovement()
        for _ in range(20):
            m.scroll_vertical(0.1)
        assert m.viewport.center_y == -2
        assert abs(m.viewport._scroll_accum_y) < 1e-5
