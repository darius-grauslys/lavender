"""
Chunk Edit mode (spec section 1.1.2).

Activation shortcut: Ctrl+K
"""

from __future__ import annotations

from modes.editor_mode import EditorMode
from tools.select_tool import SelectTool
from tools.pan_tool import PanTool
from tools.tool import Tool
from core.c_enum import CEnum, CEnumMember
from core.tile_parser import TileLayerField, TileLayerLayout
from core.tile_kind_editor import (
    TileKindEditorState,
    create_editor_state_from_enum,
    write_tile_kind_header,
)
from keybinds.keybind import (
    KeyCombo, KeybindCallback, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from workspace.movement import WorkspaceMovement

import imgui
import math as _math
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


# GLFW key constants (stable values).
_KEY_UP = 265
_KEY_DOWN = 264
_KEY_LEFT = 263
_KEY_RIGHT = 262


class TileSelectTool(SelectTool):
    """Tile selection tool.

    Shift+Up/Down moves Z axis.
    """
    name = "Tile Select"
    icon_label = "TS"

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        binds = super()._build_keybinds()
        if self._movement is not None:
            m = self._movement
            binds[KeyCombo(_KEY_UP, Modifier.SHIFT)] = \
                m.make_move_z_up()
            binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)] = \
                m.make_move_z_down()
        return binds


class ChunkPanTool(PanTool):
    """Chunk pan tool.

    Arrow keys move by 1 tile (inherited).
    Shift+Arrow keys move by 1 chunk.
    Ctrl+Up / Ctrl+Down move along Z axis (inherited).
    """
    name = "Chunk Pan"
    icon_label = "CP"

    def __init__(
            self,
            movement: Optional[WorkspaceMovement] = None,
            chunk_w: int = 8,
            chunk_h: int = 8):
        super().__init__(movement)
        self._chunk_w = chunk_w
        self._chunk_h = chunk_h

    def _build_keybinds(self) -> Dict[KeyCombo, KeybindCallback]:
        binds = super()._build_keybinds()
        if self._movement is not None:
            m = self._movement
            binds[KeyCombo(_KEY_UP, Modifier.SHIFT)] = \
                m.make_pan_chunk_up(self._chunk_w, self._chunk_h)
            binds[KeyCombo(_KEY_DOWN, Modifier.SHIFT)] = \
                m.make_pan_chunk_down(self._chunk_w, self._chunk_h)
            binds[KeyCombo(_KEY_LEFT, Modifier.SHIFT)] = \
                m.make_pan_chunk_left(self._chunk_w, self._chunk_h)
            binds[KeyCombo(_KEY_RIGHT, Modifier.SHIFT)] = \
                m.make_pan_chunk_right(self._chunk_w, self._chunk_h)
        return binds


class TileDrawTool(Tool):
    """Tile draw tool with tile list and edit sub-window (spec 1.1.2.1.3)."""

    name = "Tile Draw"
    icon_label = "TD"

    def __init__(self, objects=None, tile_byte_size: int = 1):
        self._objects = objects
        self._tile_byte_size = tile_byte_size
        self._is_dragging: bool = False
        self._tile_enums: List[CEnum] = []
        self._layer_fields: List[TileLayerField] = []
        self._layer_layouts: List[TileLayerLayout] = []
        self._selected_layer: int = 0
        self._selected_tile_value: int = 0
        self._show_editor: bool = False
        self._editor_state: Optional[TileKindEditorState] = None
        self._project_dir: Optional[Path] = None
        self._on_enum_updated: Optional[Callable] = None

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        """Set the available tile enums (one per layer)."""
        self._tile_enums = enums

    def set_layer_info(
            self,
            fields: List[TileLayerField],
            layouts: List[TileLayerLayout]) -> None:
        """Set tile layer field and layout info."""
        self._layer_fields = fields
        self._layer_layouts = layouts

    def set_project_dir(self, project_dir: Path) -> None:
        self._project_dir = project_dir

    def set_on_enum_updated(self, callback: Callable) -> None:
        """Set callback invoked after enum is written to disk."""
        self._on_enum_updated = callback

    def set_objects(self, objects) -> None:
        """Inject the workspace objects store."""
        self._objects = objects

    def set_tile_byte_size(self, size: int) -> None:
        """Set sizeof(Tile) for the project."""
        self._tile_byte_size = size

    def on_workspace_click(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Draw the selected tile at the clicked world position."""
        if self._objects is None:
            return
        cw = 8  # Will be overridden by mode
        ch = 8
        if hasattr(self, '_chunk_w'):
            cw = self._chunk_w
        if hasattr(self, '_chunk_h'):
            ch = self._chunk_h

        import math
        tile_x = int(math.floor(world_x))
        tile_y = int(math.floor(world_y))

        # Chunk coordinates
        cx = tile_x // cw if tile_x >= 0 else -(-tile_x // cw) - (1 if tile_x % cw else 0)
        cy = tile_y // ch if tile_y >= 0 else -(-tile_y // ch) - (1 if tile_y % ch else 0)

        # Local tile within chunk
        lx = tile_x - cx * cw
        ly = tile_y - cy * ch

        # Build tile bytes from selected value
        val = self._selected_tile_value
        tile_bytes = val.to_bytes(self._tile_byte_size, byteorder='little')

        # Ensure chunk exists
        chunk = self._objects.get_or_create_chunk(cx, cy, world_z)
        if chunk is None:
            return

        self._objects.set_tile(
            cx, cy, world_z, lx, ly, 0, tile_bytes)

    def on_workspace_drag_begin(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Start drag-painting: place first tile and begin drag."""
        self._is_dragging = True
        self.on_workspace_click(world_x, world_y, world_z)

    def on_workspace_drag_update(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Continue drag-painting: place tile at current position."""
        if self._is_dragging:
            self.on_workspace_click(world_x, world_y, world_z)

    def on_workspace_drag_end(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """End drag-painting."""
        if self._is_dragging:
            self.on_workspace_click(world_x, world_y, world_z)
        self._is_dragging = False

    def draw_properties(self) -> None:
        if not self._tile_enums:
            imgui.text("No tile types loaded.")
            return

        # Layer selector
        layer_names = [e.name for e in self._tile_enums]
        _, self._selected_layer = imgui.combo(
            "Layer", self._selected_layer, layer_names)

        if self._selected_layer >= len(self._tile_enums):
            return

        enum = self._tile_enums[self._selected_layer]

        # Scrollable list with "- Edit -" at top
        imgui.text(f"Tiles ({enum.name}):")
        imgui.begin_child("##tile_palette", 0, 200, border=True)

        if imgui.selectable("- Edit -##edit_tile_kinds", False)[0]:
            if not self._show_editor or self._editor_state is None:
                self._open_editor()
            else:
                # If already open for a different layer, reopen
                current_layer_name = (
                    self._layer_fields[self._selected_layer].field_name
                    if self._selected_layer < len(self._layer_fields)
                    else f"layer_{self._selected_layer}")
                if self._editor_state.layer_name != current_layer_name:
                    self._open_editor()

        imgui.separator()

        for member in enum.members:
            is_selected = member.value == self._selected_tile_value
            clicked, _ = imgui.selectable(
                f"{member.name} ({member.value})##{member.value}",
                is_selected)
            if clicked:
                self._selected_tile_value = member.value

        imgui.end_child()

    def _open_editor(self) -> None:
        """Open the Tile Kind Editor sub-window."""
        if self._selected_layer >= len(self._tile_enums):
            return
        enum = self._tile_enums[self._selected_layer]
        lf = (self._layer_fields[self._selected_layer]
              if self._selected_layer < len(self._layer_fields) else None)
        ll = (self._layer_layouts[self._selected_layer]
              if self._selected_layer < len(self._layer_layouts) else None)

        layer_name = lf.field_name if lf else f"layer_{self._selected_layer}"
        bit_width = lf.bit_width if lf else 8
        logic_bits = ll.logic_bits if ll else 0
        anim_bits = ll.animation_bits if ll else 0

        self._editor_state = create_editor_state_from_enum(
            enum, layer_name, bit_width, logic_bits, anim_bits)
        self._show_editor = True

    def _apply_editor_changes(self) -> None:
        """Write the edited enum back to the project _kind.h file."""
        if self._editor_state is None or self._project_dir is None:
            return

        state = self._editor_state
        filename = state.enum_type_name.lower() + ".h"
        filepath = (
            self._project_dir / "include" / "types" / "implemented"
            / "world" / filename)

        guard_macro = "DEFINE_" + state.enum_type_name.upper()
        write_tile_kind_header(filepath, state, guard_macro)

        if self._on_enum_updated:
            self._on_enum_updated()

    @property
    def selected_tile_value(self) -> int:
        return self._selected_tile_value

    @property
    def selected_layer(self) -> int:
        return self._selected_layer


class TileRectTool(Tool):
    """Tile rectangle fill tool.

    Click-and-drag to define a rectangle. On release, fills the
    rectangle with the selected tile value.

    Tool properties:
    - Layer selector (same as TileDraw)
    - Fill checkbox (default on). When off, reveals an edge
      thickness field for hollow rectangles.
    """

    name = "Tile Rect"
    icon_label = "TR"

    def __init__(self, objects=None, tile_byte_size: int = 1):
        self._objects = objects
        self._tile_byte_size = tile_byte_size
        self._tile_enums: List[CEnum] = []
        self._layer_fields: List[TileLayerField] = []
        self._layer_layouts: List[TileLayerLayout] = []
        self._selected_layer: int = 0
        self._selected_tile_value: int = 0
        self._fill: bool = True
        self._edge_thickness: int = 1

        # Drag state
        self._drag_start_x: Optional[int] = None
        self._drag_start_y: Optional[int] = None
        self._drag_end_x: Optional[int] = None
        self._drag_end_y: Optional[int] = None
        self._drag_z: int = 0
        self._is_dragging: bool = False

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        self._tile_enums = enums

    def set_layer_info(
            self,
            fields: List[TileLayerField],
            layouts: List[TileLayerLayout]) -> None:
        self._layer_fields = fields
        self._layer_layouts = layouts

    def set_objects(self, objects) -> None:
        self._objects = objects

    def set_tile_byte_size(self, size: int) -> None:
        self._tile_byte_size = size

    @property
    def selected_tile_value(self) -> int:
        return self._selected_tile_value

    @property
    def selected_layer(self) -> int:
        return self._selected_layer

    @property
    def fill(self) -> bool:
        return self._fill

    @property
    def edge_thickness(self) -> int:
        return self._edge_thickness

    @property
    def is_dragging(self) -> bool:
        return self._is_dragging

    @property
    def drag_rect(self) -> Optional[tuple]:
        """Return (min_x, min_y, max_x, max_y) or None."""
        if (self._drag_start_x is None
                or self._drag_end_x is None):
            return None
        x0 = min(self._drag_start_x, self._drag_end_x)
        y0 = min(self._drag_start_y, self._drag_end_y)
        x1 = max(self._drag_start_x, self._drag_end_x)
        y1 = max(self._drag_start_y, self._drag_end_y)
        return (x0, y0, x1, y1)

    def on_workspace_click(
            self, world_x: float, world_y: float,
            world_z: int) -> None:
        """Single click: fill a 1x1 rect."""
        import math as _math
        tx = int(_math.floor(world_x))
        ty = int(_math.floor(world_y))
        self._fill_rect(tx, ty, tx, ty, world_z)

    def on_workspace_drag_begin(
            self, world_x: float, world_y: float,
            world_z: int) -> None:
        import math as _math
        self._drag_start_x = int(_math.floor(world_x))
        self._drag_start_y = int(_math.floor(world_y))
        self._drag_end_x = self._drag_start_x
        self._drag_end_y = self._drag_start_y
        self._drag_z = world_z
        self._is_dragging = True

    def on_workspace_drag_update(
            self, world_x: float, world_y: float,
            world_z: int) -> None:
        if not self._is_dragging:
            return
        import math as _math
        self._drag_end_x = int(_math.floor(world_x))
        self._drag_end_y = int(_math.floor(world_y))

    def on_workspace_drag_end(
            self, world_x: float, world_y: float,
            world_z: int) -> None:
        if not self._is_dragging:
            return
        import math as _math
        self._drag_end_x = int(_math.floor(world_x))
        self._drag_end_y = int(_math.floor(world_y))
        rect = self.drag_rect
        if rect:
            self._fill_rect(
                rect[0], rect[1], rect[2], rect[3],
                self._drag_z)
        self._is_dragging = False
        self._drag_start_x = None
        self._drag_start_y = None
        self._drag_end_x = None
        self._drag_end_y = None

    def _fill_rect(
            self, x0: int, y0: int, x1: int, y1: int,
            z: int) -> None:
        """Fill a rectangle of tiles."""
        if self._objects is None:
            return
        cw = getattr(self, '_chunk_w', 8)
        ch = getattr(self, '_chunk_h', 8)

        val = self._selected_tile_value
        tile_bytes = val.to_bytes(
            self._tile_byte_size, byteorder='little')

        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if not self._fill:
                    # Hollow rect: only draw edges
                    in_interior = (
                        tx >= x0 + self._edge_thickness
                        and tx <= x1 - self._edge_thickness
                        and ty >= y0 + self._edge_thickness
                        and ty <= y1 - self._edge_thickness)
                    if in_interior:
                        continue

                cx = (tx // cw if tx >= 0
                      else -(-tx // cw) - (1 if tx % cw else 0))
                cy = (ty // ch if ty >= 0
                      else -(-ty // ch) - (1 if ty % ch else 0))
                lx = tx - cx * cw
                ly = ty - cy * ch

                chunk = self._objects.get_or_create_chunk(cx, cy, z)
                if chunk is None:
                    continue
                self._objects.set_tile(
                    cx, cy, z, lx, ly, 0, tile_bytes)

    def draw_overlay(
            self,
            workspace,
            draw_list=None,
            movement=None,
            window_pos=None,
            window_size=None) -> None:
        """Draw a preview rectangle while dragging."""
        if not self._is_dragging or draw_list is None or movement is None:
            return
        rect = self.drag_rect
        if rect is None or window_pos is None or window_size is None:
            return

        x0, y0, x1, y1 = rect
        # Convert world-tile corners to screen coordinates
        sx0, sy0 = movement.tile_to_screen(
            x0, y0,
            window_pos[0], window_pos[1],
            window_size[0], window_size[1])
        # x1+1, y1+1 because the rect is inclusive of the last tile
        sx1, sy1 = movement.tile_to_screen(
            x1 + 1, y1 + 1,
            window_pos[0], window_pos[1],
            window_size[0], window_size[1])

        # Semi-transparent fill
        fill_col = imgui.get_color_u32_rgba(0.3, 0.6, 1.0, 0.25)
        draw_list.add_rect_filled(sx0, sy0, sx1, sy1, fill_col)

        # Outline
        outline_col = imgui.get_color_u32_rgba(0.3, 0.6, 1.0, 0.9)
        draw_list.add_rect(
            sx0, sy0, sx1, sy1, outline_col, thickness=2.0)

        # Dimensions label
        w_tiles = x1 - x0 + 1
        h_tiles = y1 - y0 + 1
        label = f"{w_tiles}x{h_tiles}"
        draw_list.add_text(sx0 + 2, sy0 - 16, outline_col, label)

    def draw_properties(self) -> None:
        if not self._tile_enums:
            imgui.text("No tile types loaded.")
            return

        # Layer selector
        layer_names = [e.name for e in self._tile_enums]
        _, self._selected_layer = imgui.combo(
            "Layer##tr", self._selected_layer, layer_names)

        if self._selected_layer >= len(self._tile_enums):
            return

        enum = self._tile_enums[self._selected_layer]

        # Tile list
        imgui.text(f"Tiles ({enum.name}):")
        imgui.begin_child("##tr_palette", 0, 150, border=True)
        for member in enum.members:
            is_selected = member.value == self._selected_tile_value
            clicked, _ = imgui.selectable(
                f"{member.name} ({member.value})##tr_{member.value}",
                is_selected)
            if clicked:
                self._selected_tile_value = member.value
        imgui.end_child()

        imgui.separator()

        # Fill checkbox
        _, self._fill = imgui.checkbox("Fill##tr_fill", self._fill)

        if not self._fill:
            imgui.same_line()
            imgui.push_item_width(80)
            changed, new_val = imgui.input_int(
                "Edge##tr_edge", self._edge_thickness, 1, 1)
            if changed:
                self._edge_thickness = max(1, new_val)
            imgui.pop_item_width()


class ChunkEditMode(EditorMode):
    name = "Chunk Edit"
    shortcut_label = "Ctrl+K"

    def __init__(
            self,
            keybind_manager: KeybindManager,
            movement: Optional[WorkspaceMovement] = None,
            chunk_w: int = 8,
            chunk_h: int = 8):
        super().__init__(keybind_manager)
        self._movement = movement
        self._chunk_w = chunk_w
        self._chunk_h = chunk_h
        self._tile_select = TileSelectTool(movement)
        self._chunk_pan = ChunkPanTool(movement, chunk_w, chunk_h)
        self._tile_draw = TileDrawTool()
        self._tile_draw._chunk_w = chunk_w
        self._tile_draw._chunk_h = chunk_h
        self._tile_rect = TileRectTool()
        self._tile_rect._chunk_w = chunk_w
        self._tile_rect._chunk_h = chunk_h
        self._tools = [
            self._tile_select,
            self._chunk_pan,
            self._tile_draw,
            self._tile_rect,
        ]

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject movement into tools."""
        self._movement = movement
        self._tile_select.set_movement(movement)
        self._chunk_pan.set_movement(movement)

    def set_objects(self, objects) -> None:
        """Inject workspace objects into tile tools."""
        self._tile_draw.set_objects(objects)
        self._tile_rect.set_objects(objects)

    def set_tile_byte_size(self, size: int) -> None:
        """Set sizeof(Tile) for tile tools."""
        self._tile_draw.set_tile_byte_size(size)
        self._tile_rect.set_tile_byte_size(size)

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        self._tile_draw.set_tile_enums(enums)
        self._tile_rect.set_tile_enums(enums)

    def set_layer_info(
            self,
            fields: List[TileLayerField],
            layouts: List[TileLayerLayout]) -> None:
        self._tile_draw.set_layer_info(fields, layouts)
        self._tile_rect.set_layer_info(fields, layouts)

    def set_project_dir(self, project_dir: Path) -> None:
        self._tile_draw.set_project_dir(project_dir)

    def set_on_enum_updated(self, callback: Callable) -> None:
        self._tile_draw.set_on_enum_updated(callback)
