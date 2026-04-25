"""
Tilesheet loading and tile sampling.

A tilesheet is a PNG image composed of 8x8 pixel tiles arranged
in a grid. Tile index 0 is the top-left tile, index 1 is the
next tile to the right, wrapping to the next row.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

TILE_PX = 8  # Each tile is 8x8 pixels


@dataclass
class Tilesheet:
    """
    A loaded tilesheet image.

    Stores raw RGBA pixel data and provides tile sampling.
    """
    width: int
    height: int
    pixels: bytes  # RGBA pixel data, row-major
    tiles_per_row: int = 0
    total_tiles: int = 0

    def __post_init__(self):
        self.tiles_per_row = self.width // TILE_PX
        rows = self.height // TILE_PX
        self.total_tiles = self.tiles_per_row * rows

    def get_tile_uv(self, tile_index: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the pixel rectangle (x, y, w, h) for a tile index.
        Returns None if the index is out of range.
        """
        if tile_index < 0 or tile_index >= self.total_tiles:
            return None
        row = tile_index // self.tiles_per_row
        col = tile_index % self.tiles_per_row
        return (col * TILE_PX, row * TILE_PX, TILE_PX, TILE_PX)

    def get_tile_pixels(self, tile_index: int) -> Optional[bytes]:
        """
        Extract the 8x8 RGBA pixel data for a tile index.
        Returns 8*8*4 = 256 bytes, or None if out of range.
        """
        uv = self.get_tile_uv(tile_index)
        if uv is None:
            return None
        tx, ty, tw, th = uv
        result = bytearray()
        for row in range(th):
            src_offset = ((ty + row) * self.width + tx) * 4
            result.extend(
                self.pixels[src_offset:src_offset + tw * 4])
        return bytes(result)


def load_tilesheet(filepath: Path) -> Optional[Tilesheet]:
    """
    Load a tilesheet PNG file.
    Returns a Tilesheet object or None on failure.

    Uses PIL/Pillow if available, otherwise falls back to PyPNG.
    """
    if not filepath.exists():
        return None

    try:
        from PIL import Image
        img = Image.open(filepath).convert('RGBA')
        width, height = img.size
        pixels = img.tobytes()
        return Tilesheet(
            width=width,
            height=height,
            pixels=pixels)
    except ImportError:
        pass
    except Exception:
        return None

    # Fallback: try pypng
    try:
        import png
        reader = png.Reader(filename=str(filepath))
        w, h, rows, metadata = reader.asRGBA8()
        pixel_data = bytearray()
        for row in rows:
            pixel_data.extend(row)
        return Tilesheet(
            width=w,
            height=h,
            pixels=bytes(pixel_data))
    except ImportError:
        pass
    except Exception:
        return None

    return None
