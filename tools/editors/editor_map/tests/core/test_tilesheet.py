"""Tests for tilesheet loading and tile sampling."""

import pytest

from core.tilesheet import Tilesheet, TILE_PX


class TestTilesheet:
    def _make_tilesheet(self, width=16, height=16):
        """Create a test tilesheet with known pixel data."""
        pixels = bytearray(width * height * 4)
        tiles_per_row = width // TILE_PX
        rows = height // TILE_PX
        for ty in range(rows):
            for tx in range(tiles_per_row):
                tile_idx = ty * tiles_per_row + tx
                r = (tile_idx * 37) % 256
                g = (tile_idx * 73) % 256
                b = (tile_idx * 113) % 256
                for py in range(TILE_PX):
                    for px in range(TILE_PX):
                        offset = ((ty * TILE_PX + py) * width
                                  + tx * TILE_PX + px) * 4
                        pixels[offset] = r
                        pixels[offset + 1] = g
                        pixels[offset + 2] = b
                        pixels[offset + 3] = 255
        return Tilesheet(
            width=width, height=height, pixels=bytes(pixels))

    def test_tiles_per_row(self):
        ts = self._make_tilesheet(32, 16)
        assert ts.tiles_per_row == 4

    def test_total_tiles(self):
        ts = self._make_tilesheet(32, 16)
        assert ts.total_tiles == 8

    def test_get_tile_uv_first(self):
        ts = self._make_tilesheet(16, 16)
        uv = ts.get_tile_uv(0)
        assert uv == (0, 0, 8, 8)

    def test_get_tile_uv_second(self):
        ts = self._make_tilesheet(16, 16)
        uv = ts.get_tile_uv(1)
        assert uv == (8, 0, 8, 8)

    def test_get_tile_uv_second_row(self):
        ts = self._make_tilesheet(16, 16)
        uv = ts.get_tile_uv(2)
        assert uv == (0, 8, 8, 8)

    def test_get_tile_uv_out_of_range(self):
        ts = self._make_tilesheet(16, 16)
        assert ts.get_tile_uv(100) is None
        assert ts.get_tile_uv(-1) is None

    def test_get_tile_pixels_size(self):
        ts = self._make_tilesheet(16, 16)
        pixels = ts.get_tile_pixels(0)
        assert pixels is not None
        assert len(pixels) == TILE_PX * TILE_PX * 4

    def test_get_tile_pixels_out_of_range(self):
        ts = self._make_tilesheet(16, 16)
        assert ts.get_tile_pixels(100) is None

    def test_get_tile_pixels_consistent_color(self):
        ts = self._make_tilesheet(16, 16)
        pixels = ts.get_tile_pixels(0)
        r, g, b, a = pixels[0], pixels[1], pixels[2], pixels[3]
        for i in range(0, len(pixels), 4):
            assert pixels[i] == r
            assert pixels[i + 1] == g
            assert pixels[i + 2] == b
            assert pixels[i + 3] == a

    def test_different_tiles_different_colors(self):
        ts = self._make_tilesheet(16, 16)
        p0 = ts.get_tile_pixels(0)
        p1 = ts.get_tile_pixels(1)
        assert p0[:4] != p1[:4]
