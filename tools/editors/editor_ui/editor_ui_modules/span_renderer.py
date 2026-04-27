"""9-slice / 1×1 tile-span rendering logic for the work area.

The span indices map to a 3×3 grid:

    0  1  2        top-left,  top,     top-right
    3  4  5        left,      center,  right
    6  7  8        bot-left,  bottom,  bot-right

For a 1×1 element only index 0 from the ``span_1x1`` is used.
For 2×2 the corners are 0, 2, 6, 8.
For NxN (N≥3) edges and center fill as described in the spec.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from tools.editors.editor_ui.editor_ui_modules.constants import GRID_PX

# A tile index is just an int referencing an 8×8 cell in the tileset.
# The tileset is assumed to be a horizontal strip or a grid; we store
# the linear index and let the renderer convert to (u, v).


def tile_uv(
    tile_index: int,
    tileset_cols: int,
    tile_px: int = GRID_PX,
) -> Tuple[int, int]:
    """Convert a linear tile index to pixel (u, v) in the tileset."""
    col = tile_index % tileset_cols
    row = tile_index // tileset_cols
    return col * tile_px, row * tile_px


def build_span_tile_grid(
    tiles_w: int,
    tiles_h: int,
    span_1x1: int,
    span_9: List[int],
    supports_1x1: bool,
    supports_nxn: bool,
) -> List[List[int]]:
    """Return a 2-D grid (rows × cols) of tile indices for the given size.

    Returns an empty list if the configuration cannot produce a valid span.
    """
    if tiles_w <= 0 or tiles_h <= 0:
        return []

    if tiles_w == 1 and tiles_h == 1:
        if not supports_1x1:
            return []
        return [[span_1x1]]

    if not supports_nxn:
        return []

    grid: List[List[int]] = []
    for r in range(tiles_h):
        row: List[int] = []
        for c in range(tiles_w):
            row.append(_pick_9slice(r, c, tiles_w, tiles_h, span_9))
        grid.append(row)
    return grid


def _pick_9slice(
    r: int, c: int, tw: int, th: int, s9: List[int]
) -> int:
    """Pick the correct 9-slice index for position (r, c)."""
    top = r == 0
    bot = r == th - 1
    left = c == 0
    right = c == tw - 1

    if top and left:
        return s9[0]
    if top and right:
        return s9[2]
    if bot and left:
        return s9[6]
    if bot and right:
        return s9[8]
    if top:
        return s9[1]
    if bot:
        return s9[7]
    if left:
        return s9[3]
    if right:
        return s9[5]
    return s9[4]
