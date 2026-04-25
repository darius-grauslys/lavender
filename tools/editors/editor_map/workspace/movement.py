"""
Workspace viewport movement (spec section 4.2).

Manages the camera/viewport position in world coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewportState:
    """Current viewport position in chunk coordinates."""
    center_x: int = 0
    center_y: int = 0
    center_z: int = 0
    # Pixel offset within the current chunk for smooth scrolling
    offset_x: float = 0.0
    offset_y: float = 0.0
    # Zoom level (tiles per screen-pixel)
    zoom: float = 1.0


class WorkspaceMovement:
    """Manages workspace viewport movement."""

    def __init__(self):
        self.viewport = ViewportState()

    def pan_by_tiles(self, dx: int, dy: int) -> None:
        """Pan the viewport by tile units."""
        self.viewport.center_x += dx
        self.viewport.center_y += dy

    def pan_by_chunks(self, dx: int, dy: int, chunk_width: int = 8, chunk_height: int = 8) -> None:
        """Pan the viewport by chunk units."""
        self.viewport.center_x += dx * chunk_width
        self.viewport.center_y += dy * chunk_height

    def move_z(self, dz: int) -> None:
        """Move the viewport along the Z axis."""
        self.viewport.center_z += dz

    def go_to(self, x: int, y: int, z: int) -> None:
        """Jump the viewport to specific chunk coordinates."""
        self.viewport.center_x = x
        self.viewport.center_y = y
        self.viewport.center_z = z
        self.viewport.offset_x = 0.0
        self.viewport.offset_y = 0.0

    def pan_by_pixels(self, dx: float, dy: float) -> None:
        """Pan by pixel offset (for smooth scrolling)."""
        self.viewport.offset_x += dx
        self.viewport.offset_y += dy
