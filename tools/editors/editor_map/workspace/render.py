"""
Workspace rendering (spec section 4.2).

Renders the world grid, chunks, tiles, entities as colored
rectangles in the Dear ImGui workspace area.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import imgui

if TYPE_CHECKING:
    from core.engine_config import EngineConfig
    from core.c_enum import CEnum
    from core.tilesheet import Tilesheet
    from core.tile_parser import TileInfo
    from workspace.objects import WorkspaceObjects
    from workspace.movement import WorkspaceMovement


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
        self._tilesheet: Optional[Tilesheet] = None
        self._tilesheet_gl_texture: int = 0
        self._tile_info: Optional[TileInfo] = None
        self._rendering_enabled: bool = False

    def set_tilesheet(self, tilesheet: Optional[Tilesheet]) -> None:
        """Set the tilesheet for rendering. None disables tilesheet rendering."""
        self._tilesheet = tilesheet
        self._rendering_enabled = tilesheet is not None
        if tilesheet is not None:
            self._upload_tilesheet_texture(tilesheet)

    def set_tile_info(self, tile_info: Optional[TileInfo]) -> None:
        """Set tile info for layer-aware rendering."""
        self._tile_info = tile_info

    def _upload_tilesheet_texture(self, tilesheet: Tilesheet) -> None:
        """Upload tilesheet pixel data to an OpenGL texture."""
        try:
            import OpenGL.GL as gl
            if self._tilesheet_gl_texture:
                gl.glDeleteTextures([self._tilesheet_gl_texture])
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                tilesheet.width, tilesheet.height, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tilesheet.pixels)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            self._tilesheet_gl_texture = tex_id
        except Exception:
            self._tilesheet_gl_texture = 0

    def draw(
            self,
            objects: WorkspaceObjects,
            movement: WorkspaceMovement,
            window_pos: Tuple[float, float],
            window_size: Tuple[float, float],
            tile_byte_size: int = 1) -> None:
        """
        Draw the workspace content.

        Renders each tile layer by sampling the tilesheet using
        the tile's render value as a tile index. Falls back to
        colored rectangles when tilesheet rendering is disabled.

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

        # Precompute tilesheet UV info
        use_tilesheet = (
            self._rendering_enabled
            and self._tilesheet is not None
            and self._tilesheet_gl_texture != 0)
        ts_w = self._tilesheet.width if self._tilesheet else 1
        ts_h = self._tilesheet.height if self._tilesheet else 1
        tiles_per_row = self._tilesheet.tiles_per_row if self._tilesheet else 1

        # Determine layer count and bit extraction info
        num_layers = 0
        layer_bit_offsets: List[Tuple[int, int]] = []
        if self._tile_info:
            num_layers = len(self._tile_info.layer_fields)
            bit_offset = 0
            for lf in self._tile_info.layer_fields:
                layer_bit_offsets.append((bit_offset, lf.bit_width))
                bit_offset += lf.bit_width

        for cy_off in range(chunks_y):
            for cx_off in range(chunks_x):
                cx = start_cx + cx_off
                cy = start_cy + cy_off

                chunk = objects.get_chunk(cx, cy, vp.center_z)

                # Screen position of this chunk's top-left
                sx = ox + cx_off * cw * ts
                sy = oy + cy_off * ch * ts

                if chunk:
                    for ly in range(ch):
                        for lx in range(cw):
                            tile_data = objects.get_tile_bytes(
                                cx, cy, vp.center_z,
                                lx, ly, 0, tile_byte_size)

                            px = sx + lx * ts
                            py = sy + ly * ts

                            if not tile_data:
                                draw_list.add_rect_filled(
                                    px, py, px + ts, py + ts,
                                    imgui.get_color_u32_rgba(
                                        0.15, 0.15, 0.15, 1.0))
                                continue

                            tile_int = int.from_bytes(
                                tile_data, byteorder='little')

                            if use_tilesheet and num_layers > 0:
                                for layer_idx in range(num_layers):
                                    bit_off, bit_w = layer_bit_offsets[layer_idx]
                                    mask = (1 << bit_w) - 1
                                    tile_value = (tile_int >> bit_off) & mask

                                    if layer_idx > 0 and tile_value == 0:
                                        continue

                                    tile_row = tile_value // tiles_per_row
                                    tile_col = tile_value % tiles_per_row
                                    u0 = (tile_col * 8) / ts_w
                                    v0 = (tile_row * 8) / ts_h
                                    u1 = ((tile_col + 1) * 8) / ts_w
                                    v1 = ((tile_row + 1) * 8) / ts_h

                                    draw_list.add_image(
                                        self._tilesheet_gl_texture,
                                        (px, py),
                                        (px + ts, py + ts),
                                        uv_a=(u0, v0),
                                        uv_b=(u1, v1))
                            else:
                                value = tile_data[0] if tile_data else 0
                                color = _color_for_value(value)
                                draw_list.add_rect_filled(
                                    px, py, px + ts, py + ts,
                                    imgui.get_color_u32_rgba(*color))

                # Chunk border
                draw_list.add_rect(
                    sx, sy,
                    sx + cw * ts, sy + ch * ts,
                    imgui.get_color_u32_rgba(*CHUNK_BORDER_COLOR))
