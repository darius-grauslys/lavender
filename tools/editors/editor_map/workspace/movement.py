"""
Workspace viewport movement (spec section 4.2).

Manages the camera/viewport position in world coordinates.

Scroll behaviour (spec section 1.1 — Panning Tool):
- Mouse scroll wheel (no shift): vertical panning
    - Scroll up → pan workspace up
    - Scroll down → pan workspace down
- Mouse scroll wheel (shift held): horizontal panning
    - Scroll up → pan workspace left
    - Scroll down → pan workspace right
- Arrow keys: move by 1 tile in the respective direction
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Default tile size in pixels — matches engine TILE_PX (8).
DEFAULT_TILE_PX: int = 8

# How many tiles of movement per unit of scroll-wheel delta.
SCROLL_SENSITIVITY: float = 1.0

# Epsilon for snapping accumulated scroll to the nearest integer.
# Prevents floating-point drift from eating a tile step.
_SCROLL_EPSILON: float = 1e-9


@dataclass
class ViewportState:
    """Current viewport position in tile coordinates."""
    center_x: int = 0
    center_y: int = 0
    center_z: int = 0
    # Sub-tile pixel offset for smooth scrolling
    offset_x: float = 0.0
    offset_y: float = 0.0
    # Display zoom factor (screen-pixels per tile-pixel)
    zoom: float = 1.0
    # Accumulated fractional scroll that hasn't yet become a
    # full tile step.  Allows high-resolution scroll devices
    # to work correctly.
    _scroll_accum_x: float = field(default=0.0, repr=False)
    _scroll_accum_y: float = field(default=0.0, repr=False)


class WorkspaceMovement:
    """Manages workspace viewport movement."""

    def __init__(self, tile_px: int = DEFAULT_TILE_PX):
        self.viewport = ViewportState()
        self._tile_px = tile_px

    # ------------------------------------------------------------------
    # Tile / chunk / Z movement
    # ------------------------------------------------------------------

    def pan_by_tiles(self, dx: int, dy: int) -> None:
        """Pan the viewport by tile units."""
        self.viewport.center_x += dx
        self.viewport.center_y += dy

    def pan_by_chunks(
            self,
            dx: int,
            dy: int,
            chunk_width: int = 8,
            chunk_height: int = 8,
    ) -> None:
        """Pan the viewport by chunk units."""
        self.viewport.center_x += dx * chunk_width
        self.viewport.center_y += dy * chunk_height

    def move_z(self, dz: int) -> None:
        """Move the viewport along the Z axis."""
        self.viewport.center_z += dz

    def go_to(self, x: int, y: int, z: int) -> None:
        """Jump the viewport to specific tile coordinates."""
        self.viewport.center_x = x
        self.viewport.center_y = y
        self.viewport.center_z = z
        self.viewport.offset_x = 0.0
        self.viewport.offset_y = 0.0
        self.viewport._scroll_accum_x = 0.0
        self.viewport._scroll_accum_y = 0.0

    # ------------------------------------------------------------------
    # Pixel-level panning (smooth scrolling)
    # ------------------------------------------------------------------

    def pan_by_pixels(self, dx: float, dy: float) -> None:
        """Pan by pixel offset (for smooth scrolling)."""
        self.viewport.offset_x += dx
        self.viewport.offset_y += dy

    # ------------------------------------------------------------------
    # Scroll-wheel support  (spec section 1.1 Panning Tool)
    # ------------------------------------------------------------------

    def scroll_vertical(self, delta: float) -> None:
        """
        Handle vertical scroll input.

        Called when the mouse scroll wheel moves WITHOUT shift held.
        Positive *delta* scrolls the workspace **up** (viewport
        center_y decreases); negative scrolls **down**.

        The delta is accumulated so that fractional scroll events
        (e.g. from high-resolution trackpads) are not lost.
        """
        self.viewport._scroll_accum_y += delta * SCROLL_SENSITIVITY
        # Snap near-integer accumulator to avoid float drift
        rounded = round(self.viewport._scroll_accum_y)
        if abs(self.viewport._scroll_accum_y - rounded) < _SCROLL_EPSILON:
            self.viewport._scroll_accum_y = float(rounded)
        tiles = math.trunc(self.viewport._scroll_accum_y)
        if tiles != 0:
            self.viewport.center_y -= tiles
            self.viewport._scroll_accum_y -= tiles

    def scroll_horizontal(self, delta: float) -> None:
        """
        Handle horizontal scroll input.

        Called when the mouse scroll wheel moves WITH shift held.
        Positive *delta* scrolls the workspace **left** (viewport
        center_x decreases); negative scrolls **right**.

        The delta is accumulated so that fractional scroll events
        are not lost.
        """
        self.viewport._scroll_accum_x += delta * SCROLL_SENSITIVITY
        # Snap near-integer accumulator to avoid float drift
        rounded = round(self.viewport._scroll_accum_x)
        if abs(self.viewport._scroll_accum_x - rounded) < _SCROLL_EPSILON:
            self.viewport._scroll_accum_x = float(rounded)
        tiles = math.trunc(self.viewport._scroll_accum_x)
        if tiles != 0:
            self.viewport.center_x -= tiles
            self.viewport._scroll_accum_x -= tiles

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def screen_to_tile(
            self,
            screen_x: float,
            screen_y: float,
            workspace_origin_x: float,
            workspace_origin_y: float,
            workspace_w: float,
            workspace_h: float,
    ) -> tuple[int, int]:
        """
        Convert a screen-space pixel position to world tile coordinates.

        Args:
            screen_x, screen_y: Absolute screen position (e.g. mouse pos).
            workspace_origin_x, workspace_origin_y: Top-left of the
                workspace area in screen coordinates.
            workspace_w, workspace_h: Size of the workspace in screen pixels.

        Returns:
            (tile_x, tile_y) in world coordinates.
        """
        zoom = self.viewport.zoom
        scaled_tile = self._tile_px * zoom

        # Pixel offset from workspace center
        center_screen_x = workspace_origin_x + workspace_w * 0.5
        center_screen_y = workspace_origin_y + workspace_h * 0.5

        dx = screen_x - center_screen_x
        dy = screen_y - center_screen_y

        # Account for sub-tile pixel offset
        dx += self.viewport.offset_x * zoom
        dy += self.viewport.offset_y * zoom

        tile_x = self.viewport.center_x + math.floor(dx / scaled_tile)
        tile_y = self.viewport.center_y + math.floor(dy / scaled_tile)

        return (tile_x, tile_y)

    def tile_to_screen(
            self,
            tile_x: int,
            tile_y: int,
            workspace_origin_x: float,
            workspace_origin_y: float,
            workspace_w: float,
            workspace_h: float,
    ) -> tuple[float, float]:
        """
        Convert world tile coordinates to screen-space pixel position
        (top-left corner of the tile).

        Returns:
            (screen_x, screen_y) of the tile's top-left corner.
        """
        zoom = self.viewport.zoom
        scaled_tile = self._tile_px * zoom

        center_screen_x = workspace_origin_x + workspace_w * 0.5
        center_screen_y = workspace_origin_y + workspace_h * 0.5

        rel_x = tile_x - self.viewport.center_x
        rel_y = tile_y - self.viewport.center_y

        sx = center_screen_x + rel_x * scaled_tile - self.viewport.offset_x * zoom
        sy = center_screen_y + rel_y * scaled_tile - self.viewport.offset_y * zoom

        return (sx, sy)

    def get_chunk_grid_params(
            self,
            workspace_origin_x: float,
            workspace_origin_y: float,
            workspace_w: float,
            workspace_h: float,
            chunk_width: int = 8,
            chunk_height: int = 8,
    ) -> tuple[float, float, float, float, float, float]:
        """
        Compute parameters for drawing chunk-aligned grid lines.

        Returns:
            (first_vline_x, vline_step, first_hline_y, hline_step,
             grid_left, grid_top)

            first_vline_x: Screen X of the first vertical grid line
                at or before the workspace left edge.
            vline_step: Screen pixels between vertical grid lines.
            first_hline_y: Screen Y of the first horizontal grid line
                at or before the workspace top edge.
            hline_step: Screen pixels between horizontal grid lines.
            grid_left: Workspace left edge in screen coords.
            grid_top: Workspace top edge in screen coords.
        """
        zoom = self.viewport.zoom
        scaled_tile = self._tile_px * zoom

        vline_step = chunk_width * scaled_tile
        hline_step = chunk_height * scaled_tile

        # Screen position of world tile (0, 0)
        origin_sx, origin_sy = self.tile_to_screen(
            0, 0,
            workspace_origin_x, workspace_origin_y,
            workspace_w, workspace_h)

        # First vertical line at or before workspace left edge
        if vline_step > 0:
            n = math.floor(
                (workspace_origin_x - origin_sx) / vline_step)
            first_vline_x = origin_sx + n * vline_step
        else:
            first_vline_x = workspace_origin_x

        # First horizontal line at or before workspace top edge
        if hline_step > 0:
            n = math.floor(
                (workspace_origin_y - origin_sy) / hline_step)
            first_hline_y = origin_sy + n * hline_step
        else:
            first_hline_y = workspace_origin_y

        return (
            first_vline_x, vline_step,
            first_hline_y, hline_step,
            workspace_origin_x, workspace_origin_y,
        )

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------

    def set_zoom(self, zoom: float) -> None:
        """
        Set the display zoom level.

        Clamped to [0.25, 16.0].
        """
        self.viewport.zoom = max(0.25, min(16.0, zoom))

    def adjust_zoom(self, factor: float) -> None:
        """
        Multiply the current zoom by *factor*.

        Clamped to [0.25, 16.0].
        """
        self.set_zoom(self.viewport.zoom * factor)
