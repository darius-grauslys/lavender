"""
Tests for the Tileset Picker data model.
"""

from __future__ import annotations

from core.tilesheet import Tilesheet, TILE_PX
from core.tileset_picker import TilesetPickerState


def _make_tilesheet(
    width: int = 32, height: int = 32
) -> Tilesheet:
    """Create a synthetic tilesheet for testing."""
    pixels = bytes(width * height * 4)
    return Tilesheet(width=width, height=height, pixels=pixels)


class TestTilesetPickerStateDefaults:
    def test_defaults(self):
        s = TilesetPickerState()
        assert s.tilesheet is None
        assert s.selected_index == -1
        assert s.hovered_index == -1
        assert s.zoom == 2
        assert s.is_open is False
        assert s.has_tilesheet is False
        assert s.tiles_per_row == 0
        assert s.total_tiles == 0

    def test_with_tilesheet(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts)
        assert s.has_tilesheet is True
        assert s.tiles_per_row == 4  # 32 / 8
        assert s.total_tiles == 16  # 4 * 4


class TestTileDisplaySize:
    def test_default_zoom(self):
        s = TilesetPickerState(zoom=2)
        assert s.tile_display_size == 16  # 8 * 2

    def test_zoom_1(self):
        s = TilesetPickerState(zoom=1)
        assert s.tile_display_size == 8

    def test_zoom_3(self):
        ts = _make_tilesheet()
        s = TilesetPickerState(tilesheet=ts, zoom=3)
        assert s.tile_display_size == 24  # 8 * 3


class TestGridDimensions:
    def test_grid_width(self):
        ts = _make_tilesheet(32, 16)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        assert s.grid_width_px == 4 * 16  # 4 cols * 16px

    def test_grid_height(self):
        ts = _make_tilesheet(32, 16)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        assert s.grid_height_px == 2 * 16  # 2 rows * 16px

    def test_no_tilesheet(self):
        s = TilesetPickerState()
        assert s.grid_width_px == 0
        assert s.grid_height_px == 0


class TestOpenForEntry:
    def test_open(self):
        s = TilesetPickerState()
        s.open_for_entry(3, current_tile_index=5)
        assert s.is_open is True
        assert s.callback_target_entry_index == 3
        assert s.selected_index == 5
        assert s.hovered_index == -1

    def test_open_no_preselect(self):
        s = TilesetPickerState()
        s.open_for_entry(0)
        assert s.selected_index == -1


class TestClose:
    def test_close(self):
        s = TilesetPickerState()
        s.open_for_entry(2, 10)
        s.close()
        assert s.is_open is False
        assert s.callback_target_entry_index == -1
        assert s.hovered_index == -1


class TestConfirm:
    def test_confirm_with_selection(self):
        s = TilesetPickerState()
        s.open_for_entry(1, 7)
        result = s.confirm()
        assert result == 7
        assert s.is_open is False

    def test_confirm_no_selection(self):
        s = TilesetPickerState()
        s.open_for_entry(1)
        result = s.confirm()
        assert result is None
        assert s.is_open is False


class TestHitTest:
    def test_top_left_is_index_zero(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        assert s.hit_test(0.0, 0.0) == 0

    def test_second_tile(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Cell size = 16px. Tile (1, 0) starts at x=16
        assert s.hit_test(16.0, 0.0) == 1

    def test_second_row(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Row 1, col 0 → index = 4
        assert s.hit_test(0.0, 16.0) == 4

    def test_second_row_second_col(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Row 1, col 2 → index = 1*4 + 2 = 6
        idx = s.hit_test(2 * 16 + 1, 1 * 16 + 1)
        assert idx == 6

    def test_last_tile(self):
        ts = _make_tilesheet(32, 32)  # 4x4 = 16 tiles
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Last tile: row=3, col=3 → index 15
        idx = s.hit_test(3 * 16 + 1, 3 * 16 + 1)
        assert idx == 15

    def test_out_of_bounds_negative_x(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        assert s.hit_test(-1.0, 0.0) == -1

    def test_out_of_bounds_negative_y(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        assert s.hit_test(0.0, -1.0) == -1

    def test_out_of_bounds_col(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # 4 cols * 16px = 64px, so x=64 is out
        assert s.hit_test(64.0, 0.0) == -1

    def test_out_of_bounds_total(self):
        ts = _make_tilesheet(32, 16)  # 4x2 = 8 tiles
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Row 2 doesn't exist
        assert s.hit_test(0.0, 2 * 16 + 1) == -1

    def test_no_tilesheet(self):
        s = TilesetPickerState()
        assert s.hit_test(0.0, 0.0) == -1

    def test_past_last_tile_bottom(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        # Grid is 64px tall, y=64 is out
        assert s.hit_test(48.0, 64.0) == -1


class TestSelectAt:
    def test_select_valid(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = s.select_at(16.0, 0.0)
        assert idx == 1
        assert s.selected_index == 1

    def test_select_invalid_does_not_change(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        s.selected_index = 5
        idx = s.select_at(-10.0, -10.0)
        assert idx == -1
        # selected_index unchanged on miss
        assert s.selected_index == 5

    def test_select_out_of_bounds_default(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = s.select_at(200.0, 200.0)
        assert idx == -1
        assert s.selected_index == -1


class TestHoverAt:
    def test_hover_valid(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = s.hover_at(32.0, 16.0)
        assert idx == 6  # col=2, row=1 → 1*4+2=6
        assert s.hovered_index == 6

    def test_hover_invalid(self):
        ts = _make_tilesheet(32, 32)
        s = TilesetPickerState(tilesheet=ts, zoom=2)
        idx = s.hover_at(-1.0, -1.0)
        assert idx == -1
        assert s.hovered_index == -1


class TestIndexOrdering:
    """Verify tiles are indexed left-to-right, top-to-bottom."""

    def test_reading_order(self):
        ts = _make_tilesheet(24, 16)  # 3 cols x 2 rows = 6 tiles
        s = TilesetPickerState(tilesheet=ts, zoom=1)
        cell = TILE_PX  # 8

        expected = [
            (0, 0, 0),   # row 0, col 0 → index 0
            (1, 0, 1),   # row 0, col 1 → index 1
            (2, 0, 2),   # row 0, col 2 → index 2
            (0, 1, 3),   # row 1, col 0 → index 3
            (1, 1, 4),   # row 1, col 1 → index 4
            (2, 1, 5),   # row 1, col 2 → index 5
        ]

        for col, row, expected_idx in expected:
            x = col * cell + 1
            y = row * cell + 1
            actual = s.hit_test(float(x), float(y))
            assert actual == expected_idx, (
                f"col={col}, row={row}: "
                f"expected {expected_idx}, got {actual}"
            )
