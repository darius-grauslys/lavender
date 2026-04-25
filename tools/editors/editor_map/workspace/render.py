"""
Workspace rendering (spec section 4.2).

Renders the world grid, chunks, tiles, entities as colored
rectangles in the Dear ImGui workspace area.

Tile rendering strategy:
- For each visible tile position, read the raw tile bytes from
  the chunk data in WorkspaceObjects.
- Interpret the tile bytes as a little-endian integer.
- For each tile layer (from layer 0 upward), extract the layer's
  render value using the bit offset and bit width from TileInfo.
- Value 0 (Tile_Kind__None) on the base layer renders as a dark
  rectangle (RGB 0.15, 0.15, 0.15). On non-base layers, value 0
  is skipped (transparent).
- Non-zero values are used as a tile index into the tilesheet to
  compute UV coordinates for textured rendering.
- When no tilesheet is available, a deterministic hash-based color
  is used as a fallback.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import imgui

if TYPE_CHECKING:
    from core.engine_config import EngineConfig
    from core.c_enum import CEnum
    from core.tilesheet import Tilesheet
    from core.tile_parser import TileInfo, TileLayerField
    from core.layer_manager import LayerManager
    from workspace.objects import WorkspaceObjects
    from workspace.movement import WorkspaceMovement


# Tile pixel size in the source tilesheet (always 8x8).
_TILESHEET_TILE_PX = 8

# Color for Tile_Kind__None (value 0) on the base layer.
_NONE_COLOR = (0.15, 0.15, 0.15, 1.0)


def _color_for_value(value: int) -> Tuple[float, float, float, float]:
    """Generate a deterministic color from a tile value."""
    if value == 0:
        return _NONE_COLOR
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
        # Display size of each tile in screen pixels (before zoom).
        self._tile_size_px = tile_size_px
        # Legacy single tilesheet (fallback for layer 0)
        self._tilesheet: Optional[Tilesheet] = None
        self._tilesheet_gl_texture: int = 0
        self._tile_info: Optional[TileInfo] = None
        self._rendering_enabled: bool = False
        # Per-layer tilesheet mapping: layer_index -> (Tilesheet, gl_tex_id)
        self._layer_tilesheets: Dict[int, Tuple[Tilesheet, int]] = {}
        self._layer_manager: Optional[LayerManager] = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_tilesheet(
            self,
            tilesheet: Optional[Tilesheet],
            gl_texture_id: int = 0) -> None:
        """Set the tilesheet for rendering.

        Args:
            tilesheet: The loaded tilesheet, or None to disable.
            gl_texture_id: Pre-uploaded GL texture handle. If 0 and
                a tilesheet is provided, the renderer will attempt
                to upload it.
        """
        self._tilesheet = tilesheet
        self._rendering_enabled = tilesheet is not None
        if gl_texture_id:
            self._tilesheet_gl_texture = gl_texture_id
        elif tilesheet is not None:
            self._upload_tilesheet_texture(tilesheet)

    def set_tilesheet_gl_texture(self, gl_texture_id: int) -> None:
        """Update the GL texture handle without changing the tilesheet."""
        self._tilesheet_gl_texture = gl_texture_id

    def set_tile_info(self, tile_info: Optional[TileInfo]) -> None:
        """Set tile info for layer-aware rendering."""
        self._tile_info = tile_info

    def set_layer_manager(self, layer_manager: Optional[LayerManager]) -> None:
        """Set the layer manager for per-layer tilesheet lookup."""
        self._layer_manager = layer_manager

    def set_layer_tilesheet(
            self,
            layer_index: int,
            tilesheet: Optional[Tilesheet],
            gl_texture_id: int = 0) -> None:
        """Set the tilesheet for a specific tile layer.

        Args:
            layer_index: The tile layer index.
            tilesheet: The tilesheet, or None to clear.
            gl_texture_id: Pre-uploaded GL texture handle.
        """
        if tilesheet is None:
            self._layer_tilesheets.pop(layer_index, None)
        else:
            if gl_texture_id == 0:
                gl_texture_id = self._try_upload_texture(tilesheet)
            self._layer_tilesheets[layer_index] = (tilesheet, gl_texture_id)

    def clear_layer_tilesheets(self) -> None:
        """Remove all per-layer tilesheet assignments."""
        self._layer_tilesheets.clear()

    def _try_upload_texture(self, tilesheet: Tilesheet) -> int:
        """Attempt to upload a tilesheet to GL. Returns tex id or 0."""
        try:
            import OpenGL.GL as gl
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                gl.GL_NEAREST)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                gl.GL_NEAREST)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                tilesheet.width, tilesheet.height, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tilesheet.pixels)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            return int(tex_id)
        except Exception:
            return 0

    def _upload_tilesheet_texture(self, tilesheet: Tilesheet) -> None:
        """Upload tilesheet pixel data to an OpenGL texture."""
        try:
            import OpenGL.GL as gl
            if self._tilesheet_gl_texture:
                gl.glDeleteTextures([self._tilesheet_gl_texture])
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                gl.GL_NEAREST)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                gl.GL_NEAREST)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                tilesheet.width, tilesheet.height, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tilesheet.pixels)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            self._tilesheet_gl_texture = int(tex_id)
        except Exception:
            self._tilesheet_gl_texture = 0

    # ------------------------------------------------------------------
    # Main draw entry point
    # ------------------------------------------------------------------

    def draw(
            self,
            objects: WorkspaceObjects,
            movement: WorkspaceMovement,
            window_pos: Tuple[float, float],
            window_size: Tuple[float, float],
            tile_byte_size: int = 1) -> None:
        """
        Draw tiles for all visible chunks.

        Uses *movement* to convert world tile coordinates to screen
        positions so that rendering is consistent with the viewport
        pan/zoom state.

        Tiles are rendered layer-by-layer (layer 0 first, topmost
        layer last) so that upper layers composite on top.

        Args:
            objects: The workspace object store.
            movement: The viewport / camera state.
            window_pos: Top-left of the workspace window (screen).
            window_size: Size of the workspace window (screen).
            tile_byte_size: ``sizeof(Tile)`` for the project.
        """
        draw_list = imgui.get_window_draw_list()
        cw = self._config.chunk_width
        ch = self._config.chunk_height
        vp = movement.viewport
        zoom = vp.zoom

        # Scaled tile size on screen
        scaled_tile = movement._tile_px * zoom

        # Determine the range of world-tile coordinates visible in
        # the workspace window.
        tl_tx, tl_ty = movement.screen_to_tile(
            window_pos[0], window_pos[1],
            window_pos[0], window_pos[1],
            window_size[0], window_size[1])
        br_tx, br_ty = movement.screen_to_tile(
            window_pos[0] + window_size[0],
            window_pos[1] + window_size[1],
            window_pos[0], window_pos[1],
            window_size[0], window_size[1])

        # Expand by 1 tile on each side to avoid popping
        tl_tx -= 1
        tl_ty -= 1
        br_tx += 1
        br_ty += 1

        # Convert tile range to chunk range
        min_cx = math.floor(tl_tx / cw)
        min_cy = math.floor(tl_ty / ch)
        max_cx = math.floor(br_tx / cw)
        max_cy = math.floor(br_ty / ch)

        current_z = vp.center_z

        # Precompute per-layer tilesheet UV helpers
        # Each layer can have its own tilesheet; fall back to the
        # global tilesheet when no per-layer sheet is assigned.
        # layer_ts_info: list of (use_ts, ts_w, ts_h, tiles_per_row, gl_tex)
        layer_ts_info: List[Tuple[bool, float, float, int, int]] = []

        # Precompute layer bit extraction info
        num_layers = 0
        layer_bit_info: List[Tuple[int, int]] = []  # (bit_offset, mask)
        if self._tile_info:
            num_layers = len(self._tile_info.layer_fields)
            bit_offset = 0
            for li, lf in enumerate(self._tile_info.layer_fields):
                mask = (1 << lf.bit_width) - 1
                layer_bit_info.append((bit_offset, mask))
                bit_offset += lf.bit_width

                # Determine tilesheet for this layer
                lts, lgl = None, 0
                if li in self._layer_tilesheets:
                    lts, lgl = self._layer_tilesheets[li]
                if lts is None and self._tilesheet is not None:
                    lts = self._tilesheet
                    lgl = self._tilesheet_gl_texture

                if lts is not None and lgl != 0:
                    layer_ts_info.append((
                        True,
                        float(lts.width),
                        float(lts.height),
                        lts.tiles_per_row,
                        lgl))
                else:
                    layer_ts_info.append((False, 1.0, 1.0, 1, 0))

        # Legacy fallback info for non-layer-aware path
        use_tilesheet = (
            self._rendering_enabled
            and self._tilesheet is not None
            and self._tilesheet_gl_texture != 0)
        ts_w = float(self._tilesheet.width) if self._tilesheet else 1.0
        ts_h = float(self._tilesheet.height) if self._tilesheet else 1.0
        tiles_per_row = (
            self._tilesheet.tiles_per_row if self._tilesheet else 1)
        gl_tex = self._tilesheet_gl_texture

        none_col = imgui.get_color_u32_rgba(*_NONE_COLOR)

        # Iterate over visible chunks
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                chunk = objects.get_chunk(cx, cy, current_z)
                if chunk is None:
                    # Auto-create empty chunks for the visible area
                    chunk = objects.get_or_create_chunk(
                        cx, cy, current_z)

                # Screen position of this chunk's top-left tile (0,0)
                chunk_world_x = cx * cw
                chunk_world_y = cy * ch

                for ly in range(ch):
                    for lx in range(cw):
                        world_tx = chunk_world_x + lx
                        world_ty = chunk_world_y + ly

                        # Convert world tile to screen position
                        px, py = movement.tile_to_screen(
                            world_tx, world_ty,
                            window_pos[0], window_pos[1],
                            window_size[0], window_size[1])

                        px2 = px + scaled_tile
                        py2 = py + scaled_tile

                        # Cull tiles fully outside the window
                        if (px2 < window_pos[0]
                                or px > window_pos[0] + window_size[0]
                                or py2 < window_pos[1]
                                or py > window_pos[1] + window_size[1]):
                            continue

                        tile_data = objects.get_tile_bytes(
                            cx, cy, current_z,
                            lx, ly, 0, tile_byte_size)

                        if not tile_data:
                            # No data — draw dark empty
                            draw_list.add_rect_filled(
                                px, py, px2, py2, none_col)
                            continue

                        tile_int = int.from_bytes(
                            tile_data, byteorder='little')

                        if num_layers > 0 and layer_ts_info:
                            self._draw_tile_layers_multi(
                                draw_list, tile_int,
                                num_layers, layer_bit_info,
                                layer_ts_info, none_col,
                                px, py, px2, py2)
                        else:
                            # Fallback: use first byte as value
                            value = tile_data[0] if tile_data else 0
                            if value == 0:
                                draw_list.add_rect_filled(
                                    px, py, px2, py2, none_col)
                            else:
                                color = _color_for_value(value)
                                draw_list.add_rect_filled(
                                    px, py, px2, py2,
                                    imgui.get_color_u32_rgba(*color))

                # Chunk border
                chunk_sx, chunk_sy = movement.tile_to_screen(
                    chunk_world_x, chunk_world_y,
                    window_pos[0], window_pos[1],
                    window_size[0], window_size[1])
                chunk_ex = chunk_sx + cw * scaled_tile
                chunk_ey = chunk_sy + ch * scaled_tile
                draw_list.add_rect(
                    chunk_sx, chunk_sy, chunk_ex, chunk_ey,
                    imgui.get_color_u32_rgba(*CHUNK_BORDER_COLOR))

    # ------------------------------------------------------------------
    # Per-tile layer rendering
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_tile_layers_multi(
            draw_list,
            tile_int: int,
            num_layers: int,
            layer_bit_info: List[Tuple[int, int]],
            layer_ts_info: List[Tuple[bool, float, float, int, int]],
            none_col: int,
            px: float, py: float,
            px2: float, py2: float) -> None:
        """Render all layers for a single tile position.

        Each layer samples from its own tilesheet (via layer_ts_info).
        Layers are drawn bottom-to-top (index 0 first).
        Value 0 on the base layer draws a dark rectangle;
        value 0 on upper layers is skipped (transparent).
        """
        for layer_idx in range(num_layers):
            bit_offset, mask = layer_bit_info[layer_idx]
            tile_value = (tile_int >> bit_offset) & mask

            if tile_value == 0:
                if layer_idx == 0:
                    draw_list.add_rect_filled(
                        px, py, px2, py2, none_col)
                continue

            use_ts, ts_w, ts_h, tiles_per_row, gl_tex = \
                layer_ts_info[layer_idx]

            if not use_ts:
                # No tilesheet for this layer — use fallback color
                color = _color_for_value(tile_value)
                draw_list.add_rect_filled(
                    px, py, px2, py2,
                    imgui.get_color_u32_rgba(*color))
                continue

            tile_row = tile_value // tiles_per_row
            tile_col = tile_value % tiles_per_row
            u0 = (tile_col * _TILESHEET_TILE_PX) / ts_w
            v0 = (tile_row * _TILESHEET_TILE_PX) / ts_h
            u1 = ((tile_col + 1) * _TILESHEET_TILE_PX) / ts_w
            v1 = ((tile_row + 1) * _TILESHEET_TILE_PX) / ts_h

            draw_list.add_image(
                gl_tex,
                (px, py), (px2, py2),
                uv_a=(u0, v0), uv_b=(u1, v1))

    @staticmethod
    def _draw_tile_layers(
            draw_list,
            tile_int: int,
            num_layers: int,
            layer_bit_info: List[Tuple[int, int]],
            tiles_per_row: int,
            ts_w: float,
            ts_h: float,
            gl_tex: int,
            none_col: int,
            px: float, py: float,
            px2: float, py2: float) -> None:
        """Legacy: render all layers using a single tilesheet.

        Kept for backward compatibility. Prefer _draw_tile_layers_multi.
        """
        for layer_idx in range(num_layers):
            bit_offset, mask = layer_bit_info[layer_idx]
            tile_value = (tile_int >> bit_offset) & mask

            if tile_value == 0:
                if layer_idx == 0:
                    draw_list.add_rect_filled(
                        px, py, px2, py2, none_col)
                continue

            tile_row = tile_value // tiles_per_row
            tile_col = tile_value % tiles_per_row
            u0 = (tile_col * _TILESHEET_TILE_PX) / ts_w
            v0 = (tile_row * _TILESHEET_TILE_PX) / ts_h
            u1 = ((tile_col + 1) * _TILESHEET_TILE_PX) / ts_w
            v1 = ((tile_row + 1) * _TILESHEET_TILE_PX) / ts_h

            draw_list.add_image(
                gl_tex,
                (px, py), (px2, py2),
                uv_a=(u0, v0), uv_b=(u1, v1))
