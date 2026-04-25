"""
Data model for the Tileset Picker sub-window.

The Tileset Picker displays the loaded tilesheet as a grid of
8x8 pixel tiles. The user clicks a tile to select its index.
Index 0 is the top-left tile, incrementing left-to-right,
top-to-bottom.

This module provides the selection model only; the UI rendering
is handled by the UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from core.tilesheet import Tilesheet, TILE_PX


@dataclass
class TilesetPickerState:
    """
    State for the tileset picker sub-window.

    Attributes:
        tilesheet: The loaded tilesheet to pick from.
        selected_index: Currently selected tile index, or -1 if none.
        hovered_index: Currently hovered tile index, or -1 if none.
        zoom: Display zoom factor (1 = 1:1 pixel mapping).
        is_open: Whether the picker sub-window is currently open.
        callback_target_entry_index: Index into the parent
            TileKindEditorState.tile_kinds list that will receive
            the picked tile index. -1 if not targeting an entry.
    """
    tilesheet: Optional[Tilesheet] = None
    selected_index: int = -1
    hovered_index: int = -1
    zoom: int = 2
    is_open: bool = False
    callback_target_entry_index: int = -1

    @property
    def has_tilesheet(self) -> bool:
        return self.tilesheet is not None

    @property
    def tiles_per_row(self) -> int:
        if self.tilesheet is None:
            return 0
        return self.tilesheet.tiles_per_row

    @property
    def total_tiles(self) -> int:
        if self.tilesheet is None:
            return 0
        return self.tilesheet.total_tiles

    @property
    def tile_display_size(self) -> int:
        """Size of each tile cell in display pixels."""
        return TILE_PX * self.zoom

    @property
    def grid_width_px(self) -> int:
        """Total grid width in display pixels."""
        return self.tiles_per_row * self.tile_display_size

    @property
    def grid_height_px(self) -> int:
        """Total grid height in display pixels."""
        if self.tilesheet is None:
            return 0
        rows = self.tilesheet.height // TILE_PX
        return rows * self.tile_display_size

    def open_for_entry(self, entry_index: int, current_tile_index: int = -1) -> None:
        """
        Open the picker targeting a specific TileKindEntry.

        Args:
            entry_index: Index into TileKindEditorState.tile_kinds
            current_tile_index: Pre-select this tile index if >= 0
        """
        self.is_open = True
        self.callback_target_entry_index = entry_index
        self.selected_index = current_tile_index
        self.hovered_index = -1

    def close(self) -> None:
        """Close the picker without confirming."""
        self.is_open = False
        self.callback_target_entry_index = -1
        self.hovered_index = -1

    def confirm(self) -> Optional[int]:
        """
        Confirm the selection and close.
        Returns the selected tile index, or None if nothing selected.
        """
        result = self.selected_index if self.selected_index >= 0 else None
        self.is_open = False
        self.callback_target_entry_index = -1
        self.hovered_index = -1
        return result

    def hit_test(self, local_x: float, local_y: float) -> int:
        """
        Given a position relative to the grid origin (in display pixels),
        return the tile index at that position, or -1 if out of bounds.
        """
        if not self.has_tilesheet:
            return -1
        cell = self.tile_display_size
        if cell <= 0:
            return -1
        col = int(local_x) // cell
        row = int(local_y) // cell
        if col < 0 or row < 0:
            return -1
        if col >= self.tiles_per_row:
            return -1
        index = row * self.tiles_per_row + col
        if index >= self.total_tiles:
            return -1
        return index

    def select_at(self, local_x: float, local_y: float) -> int:
        """
        Select the tile at the given display-pixel position.
        Returns the selected index or -1.
        """
        idx = self.hit_test(local_x, local_y)
        if idx >= 0:
            self.selected_index = idx
        return idx

    def hover_at(self, local_x: float, local_y: float) -> int:
        """
        Update hover state for the given display-pixel position.
        Returns the hovered index or -1.
        """
        self.hovered_index = self.hit_test(local_x, local_y)
        return self.hovered_index
