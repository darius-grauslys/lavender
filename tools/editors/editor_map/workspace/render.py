"""
Workspace rendering (spec section 4.2).

Renders the world grid, chunks, tiles, entities as colored
rectangles in the Dear ImGui workspace area.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import imgui

if TYPE_CHECKING:
    from ..core.engine_config import EngineConfig
    from ..core.c_enum import CEnum
    from .objects import WorkspaceObjects
    from .movement import WorkspaceMovement


# Simple color palette for tile kinds (hash-based)
def _color_for_value(value: int) -> Tuple[float, float, float, float]:
    """Generate a deterministic color from a tile value."""
    if value == 0:
        return (0.15, 0.15, 0.15, 1.0)  # None/empty = dark
    # Simple hash to color
    r = ((value * 137) % 256) / 255.0
    g = ((value * 59 + 97) % 256) / 255.0
    b = ((value * 211 + 43) % 256) / 255.0
    return (max(0.2, r), max(0.2, g), max(0.2, b), 1.0)


SELECTION_COLOR = (0.6, 0.2, 0.8, 1.0)  # Purple per spec
SELECTION_THICKNESS = 3.0
GRID_COLOR = (0.3, 0.3, 0.3, 0.5)
CHUNK_BORDER_COLOR = (0.5, 0.5, 0.0, 0.8)


class WorkspaceRenderer:
    """Renders the workspace grid and objects."""

    def __init__(
            self,
            config: EngineConfig,
            tile_size_px: int = 16):
        self._config = config
        self._tile_size_px = tile_size_px

    def draw(
            self,
            objects: WorkspaceObjects,
            movement: WorkspaceMovement,
            window_pos: Tuple[float, float],
            window_size: Tuple[float, float],
            tile_byte_size: int = 1) -> None:
        """
        Draw the workspace content.

        Args:
            objects: The workspace object store
            movement: The viewport state
            window_pos: Top-left of the workspace window in screen coords
            window_size: Size of the workspace window
            tile_byte_size: sizeof(Tile) for the project
        """
        draw_list = imgui.get_window_draw_list()
        vp = movement.viewport
        cw = self._config.chunk_width
        ch = self._config.chunk_height
        ts = self._tile_size_px

        # How many chunks fit on screen
        chunks_x = int(window_size[0] / (cw * ts)) + 2
        chunks_y = int(window_size[1] / (ch * ts)) + 2

        # Starting chunk
        start_cx = vp.center_x - chunks_x // 2
        start_cy = vp.center_y - chunks_y // 2

        ox = window_pos[0] - vp.offset_x
        oy = window_pos[1] - vp.offset_y

        for cy_off in range(chunks_y):
            for cx_off in range(chunks_x):
                cx = start_cx + cx_off
                cy = start_cy + cy_off

                chunk = objects.get_chunk(cx, cy, vp.center_z)

                # Screen position of this chunk's top-left
                sx = ox + cx_off * cw * ts
                sy = oy + cy_off * ch * ts

                if chunk:
                    # Draw tiles as colored rectangles
                    for ly in range(ch):
                        for lx in range(cw):
                            # Read first byte(s) to determine tile kind
                            tile_data = objects.get_tile_bytes(
                                cx, cy, vp.center_z,
                                lx, ly, 0, tile_byte_size)
                            value = 0
                            if tile_data:
                                # Use first byte as a simple kind indicator
                                value = tile_data[0]

                            color = _color_for_value(value)
                            px = sx + lx * ts
                            py = sy + ly * ts
                            draw_list.add_rect_filled(
                                px, py, px + ts, py + ts,
                                imgui.get_color_u32_rgba(*color))

                # Chunk border
                draw_list.add_rect(
                    sx, sy,
                    sx + cw * ts, sy + ch * ts,
                    imgui.get_color_u32_rgba(*CHUNK_BORDER_COLOR))
