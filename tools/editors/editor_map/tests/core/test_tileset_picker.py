"""Tests for the Tileset Picker data model."""

import pytest

from core.tilesheet import Tilesheet, TILE_PX
from core.tileset_picker import TilesetPickerState


def _make_tilesheet(width=32, height=32):
    """Create a test tilesheet."""
    pixels = bytes(width * height * 4)
    return Tilesheet(width=width, height=height, pixels=pixels)


class TestTilesetPickerState:
    def test_no_tilesheet(self):
        state = TilesetPickerState()
        assert not state.has_tilesheet
        assert state.tiles_per_row == 0
        assert state.total_tiles == 0
        assert state.grid_width_px == 0
        assert state.grid_height_px == 0

    def test_with_tilesheet(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts)
        assert state.has_tilesheet
        assert state.tiles_per_row == 4  # 32 / 8
        assert state.total_tiles == 16  # 4 * 4

    def test_tile_display_size(self):
        ts = _make_tilesheet()
        state = TilesetPickerState(tilesheet=ts, zoom=3)
        assert state.tile_display_size == 24  # 8 * 3

    def test_grid_dimensions(self):
        ts = _make_tilesheet(32, 16)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        assert state.grid_width_px == 4 * 16  # 4 tiles * 16px
        assert state.grid_height_px == 2 * 16  # 2 rows * 16px

    def test_hit_test_top_left(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        assert state.hit_test(0, 0) == 0

    def test_hit_test_second_tile(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        # Second tile starts at x=16 (8px * zoom=2)
        assert state.hit_test(16, 0) == 1

    def test_hit_test_second_row(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        # Second row starts at y=16
        assert state.hit_test(0, 16) == 4  # tiles_per_row=4

    def test_hit_test_out_of_bounds_negative(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        assert state.hit_test(-1, 0) == -1
        assert state.hit_test(0, -1) == -1

    def test_hit_test_out_of_bounds_right(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        # Grid is 64px wide (4 tiles * 16px)
        assert state.hit_test(64, 0) == -1

    def test_hit_test_out_of_bounds_bottom(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        # Grid is 64px tall (4 rows * 16px)
        assert state.hit_test(0, 64) == -1

    def test_hit_test_no_tilesheet(self):
        state = TilesetPickerState()
        assert state.hit_test(0, 0) == -1

    def test_select_at(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = state.select_at(16, 0)
        assert idx == 1
        assert state.selected_index == 1

    def test_select_at_out_of_bounds(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = state.select_at(200, 200)
        assert idx == -1
        assert state.selected_index == -1

    def test_hover_at(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = state.hover_at(32, 16)
        assert idx == 6  # col=2, row=1 -> 1*4+2=6
        assert state.hovered_index == 6

    def test_open_for_entry(self):
        ts = _make_tilesheet()
        state = TilesetPickerState(tilesheet=ts)
        state.open_for_entry(3, current_tile_index=5)
        assert state.is_open
        assert state.callback_target_entry_index == 3
        assert state.selected_index == 5

    def test_close(self):
        ts = _make_tilesheet()
        state = TilesetPickerState(tilesheet=ts)
        state.open_for_entry(3)
        state.close()
        assert not state.is_open
        assert state.callback_target_entry_index == -1

    def test_confirm_with_selection(self):
        ts = _make_tilesheet()
        state = TilesetPickerState(tilesheet=ts)
        state.open_for_entry(3)
        state.selected_index = 7
        result = state.confirm()
        assert result == 7
        assert not state.is_open

    def test_confirm_without_selection(self):
        ts = _make_tilesheet()
        state = TilesetPickerState(tilesheet=ts)
        state.open_for_entry(3)
        result = state.confirm()
        assert result is None
        assert not state.is_open

    def test_last_tile_index(self):
        ts = _make_tilesheet(32, 32)
        state = TilesetPickerState(tilesheet=ts, zoom=2)
        # Last tile: index 15, at col=3, row=3
        # Position: x=3*16=48, y=3*16=48
        assert state.hit_test(48, 48) == 15
        # One pixel past last tile
        assert state.hit_test(48, 64) == -1
