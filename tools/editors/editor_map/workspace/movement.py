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
        tiles = math.trunc(self.viewport._scroll_accum_x)
        if tiles != 0:
            self.viewport.center_x -= tiles
            self.viewport._scroll_accum_x -= tiles

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
