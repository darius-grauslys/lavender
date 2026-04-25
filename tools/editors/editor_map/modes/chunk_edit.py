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
from pathlib import Path
from typing import Callable, Dict, List, Optional

from core.tileset_picker import TilesetPickerState
from core.tilesheet import Tilesheet, TILE_PX

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

    # Fixed width for the tile index button (fits "0000" + padding)
    _INDEX_BTN_WIDTH = 48.0
    # Fixed width for the X (delete) button
    _DELETE_BTN_WIDTH = 24.0

    def __init__(self):
        self._tile_enums: List[CEnum] = []
        self._layer_fields: List[TileLayerField] = []
        self._layer_layouts: List[TileLayerLayout] = []
        self._selected_layer: int = 0
        self._selected_tile_value: int = 0
        self._show_editor: bool = False
        self._editor_state: Optional[TileKindEditorState] = None
        self._project_dir: Optional[Path] = None
        self._on_enum_updated: Optional[Callable] = None
        self._active_tilesheet: Optional[Tilesheet] = None
        self._picker_state: TilesetPickerState = TilesetPickerState()
        self._picker_target_index: int = -1

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

    def set_active_tilesheet(self, tilesheet: Optional[Tilesheet]) -> None:
        """Set the active tilesheet for the tileset picker."""
        self._active_tilesheet = tilesheet
        self._picker_state.tilesheet = tilesheet

    def set_tilesheet_texture_id(self, texture_id: int) -> None:
        """Set the GL texture ID for the tilesheet."""
        self._picker_state.texture_id = texture_id

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

        if self._show_editor:
            self._draw_editor_window()

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

    def _draw_editor_window(self) -> None:
        """Draw the Tile Kind Editor sub-window."""
        if self._editor_state is None:
            return

        state = self._editor_state

        imgui.set_next_window_size(800, 500, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            f"Tile Kind Editor - {state.layer_name}##tke",
            True, flags)

        if not opened:
            self._show_editor = False
            self._editor_state = None
            imgui.end()
            return

        avail_w = imgui.get_content_region_available_width()
        col_w = avail_w / 3.0 - 10

        # --- Table 1: Tile Kinds ---
        imgui.begin_child("##tke_kinds", col_w, -40, border=True)
        imgui.text(f"Tile Kinds - {state.layer_name}")
        imgui.separator()

        _, state.kind_filter = imgui.input_text(
            "##kind_filter", state.kind_filter, 128)

        remove_idx = None
        for i, tk in enumerate(state.tile_kinds):
            if (state.kind_filter
                    and state.kind_filter.lower() not in tk.name.lower()):
                continue
            imgui.push_id(f"tk_{i}")

            # Fixed-width index button (4-digit display)
            idx_label = f"{tk.value:4d}"
            if imgui.button(idx_label, width=self._INDEX_BTN_WIDTH):
                if self._active_tilesheet is not None:
                    self._picker_target_index = i
                    self._picker_state.open_for_entry(
                        i, tk.value)

            imgui.same_line()

            # Name field stretches remaining width
            remaining = (
                imgui.get_content_region_available_width()
                - self._DELETE_BTN_WIDTH
                - imgui.get_style().item_spacing.x)
            name_w = max(80.0, remaining)
            imgui.push_item_width(name_w)
            changed_name, new_name = imgui.input_text(
                "##name", tk.name, 128)
            if changed_name:
                tk.name = new_name
            imgui.pop_item_width()

            imgui.same_line()

            if imgui.button("X##del", width=self._DELETE_BTN_WIDTH):
                remove_idx = i
            imgui.pop_id()

        if remove_idx is not None:
            state.remove_tile_kind(remove_idx)

        imgui.end_child()
        imgui.same_line()

        # --- Table 2: Logical Tiles ---
        imgui.begin_child("##tke_logic", col_w, -40, border=True)
        if state.logic_bits == 0:
            imgui.text("Logical Tiles (disabled)")
        else:
            imgui.text("Logical Tiles")
        imgui.separator()

        _, state.logic_filter = imgui.input_text(
            "##logic_filter", state.logic_filter, 128)

        kind_names = [tk.name for tk in state.tile_kinds]
        logic_remove_idx = None
        for i, lt in enumerate(state.logical_tiles):
            if (state.logic_filter
                    and state.logic_filter.lower()
                    not in lt.tile_kind_name.lower()):
                continue
            imgui.push_id(f"lt_{i}")
            current_idx = 0
            if lt.tile_kind_name in kind_names:
                current_idx = kind_names.index(lt.tile_kind_name)
            remaining = (
                imgui.get_content_region_available_width()
                - self._DELETE_BTN_WIDTH
                - imgui.get_style().item_spacing.x)
            imgui.push_item_width(max(80.0, remaining))
            changed, new_idx = imgui.combo(
                "##lsel", current_idx, kind_names)
            if changed and kind_names:
                lt.tile_kind_name = kind_names[new_idx]
            imgui.pop_item_width()
            imgui.same_line()
            if imgui.button("X##ldel", width=self._DELETE_BTN_WIDTH):
                logic_remove_idx = i
            imgui.pop_id()

        if logic_remove_idx is not None:
            state.remove_logical_tile(logic_remove_idx)

        imgui.end_child()
        imgui.same_line()

        # --- Table 3: Animation Tiles ---
        imgui.begin_child("##tke_anim", col_w, -40, border=True)
        if state.animation_bits == 0:
            imgui.text("Animation Tiles (disabled)")
        else:
            imgui.text("Animation Tiles")
        imgui.separator()

        _, state.animation_filter = imgui.input_text(
            "##anim_filter", state.animation_filter, 128)

        anim_remove_idx = None
        for i, at in enumerate(state.animation_tiles):
            if (state.animation_filter
                    and state.animation_filter.lower()
                    not in at.tile_kind_name.lower()):
                continue
            imgui.push_id(f"at_{i}")
            current_idx = 0
            if at.tile_kind_name in kind_names:
                current_idx = kind_names.index(at.tile_kind_name)
            remaining = (
                imgui.get_content_region_available_width()
                - self._DELETE_BTN_WIDTH
                - imgui.get_style().item_spacing.x)
            imgui.push_item_width(max(80.0, remaining))
            changed, new_idx = imgui.combo(
                "##asel", current_idx, kind_names)
            if changed and kind_names:
                at.tile_kind_name = kind_names[new_idx]
            imgui.pop_item_width()
            imgui.same_line()
            if imgui.button("X##adel", width=self._DELETE_BTN_WIDTH):
                anim_remove_idx = i
            imgui.pop_id()

        if anim_remove_idx is not None:
            state.remove_animation_tile(anim_remove_idx)

        imgui.end_child()

        # Bottom buttons
        if state.can_add_tile_kind:
            if imgui.button("+ Kind"):
                state.add_tile_kind()
        else:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
            imgui.button("+ Kind")
            imgui.pop_style_var()

        imgui.same_line()

        if state.can_add_logical_tile:
            if imgui.button("+ Logic"):
                state.add_logical_tile()
        else:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
            imgui.button("+ Logic")
            imgui.pop_style_var()

        imgui.same_line()

        if state.can_add_animation_tile:
            if imgui.button("+ Anim"):
                state.add_animation_tile()
        else:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
            imgui.button("+ Anim")
            imgui.pop_style_var()

        imgui.same_line(imgui.get_window_width() - 150)

        if imgui.button("OK##tke_ok"):
            self._apply_editor_changes()
            self._show_editor = False
            self._editor_state = None

        imgui.same_line()

        if imgui.button("Cancel##tke_cancel"):
            self._show_editor = False
            self._editor_state = None

        imgui.end()

        # Draw the tileset picker sub-window if open
        if self._picker_state.is_open:
            self._draw_tileset_picker()

    def _draw_tileset_picker(self) -> None:
        """Draw the tileset picker sub-window and handle result."""
        state = self._picker_state

        imgui.set_next_window_size(500, 450, imgui.FIRST_USE_EVER)
        imgui.set_next_window_position(
            imgui.get_io().display_size.x * 0.5,
            imgui.get_io().display_size.y * 0.5,
            imgui.ONCE,
            pivot_x=0.5, pivot_y=0.5)

        flags = (
            imgui.WINDOW_NO_SAVED_SETTINGS
            | imgui.WINDOW_NO_COLLAPSE
        )
        expanded, opened = imgui.begin(
            "Tileset Picker##tsp", True, flags)

        if not opened:
            state.close()
            imgui.end()
            return

        if not state.has_tilesheet:
            imgui.text("No tilesheet loaded.")
            imgui.spacing()
            if imgui.button("Cancel##tsp_cancel", width=80):
                state.close()
            imgui.end()
            return

        # Grid area
        cell = state.tile_display_size
        cols = state.tiles_per_row
        total = state.total_tiles
        rows = (total + cols - 1) // cols if cols > 0 else 0

        bottom_bar_h = 40.0
        avail = imgui.get_content_region_available()
        grid_h = avail.y - bottom_bar_h

        imgui.begin_child(
            "##tsp_grid", width=0, height=grid_h,
            border=True)

        draw_list = imgui.get_window_draw_list()
        cursor_screen = imgui.get_cursor_screen_position()
        origin_x, origin_y = cursor_screen.x, cursor_screen.y

        grid_w_px = cols * cell
        grid_h_px = rows * cell
        if grid_w_px > 0 and grid_h_px > 0:
            imgui.invisible_button("##tsp_grid_btn", grid_w_px, grid_h_px)

            if imgui.is_item_hovered():
                mouse = imgui.get_mouse_position()
                local_x = mouse.x - origin_x
                local_y = mouse.y - origin_y
                state.hover_at(local_x, local_y)
                if imgui.is_mouse_clicked(0):
                    state.select_at(local_x, local_y)
            else:
                state.hovered_index = -1

            # Draw tile cells
            grid_col = imgui.get_color_u32_rgba(0.1, 0.3, 0.3, 0.6)
            hover_col = imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 0.8)
            sel_col = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0)

            has_texture = (
                state.texture_id != 0
                and state.tilesheet is not None)

            # If we have a texture, compute UV step per tile
            if has_texture:
                ts = state.tilesheet
                inv_w = 1.0 / ts.width if ts.width > 0 else 0.0
                inv_h = 1.0 / ts.height if ts.height > 0 else 0.0

            for idx in range(total):
                col = idx % cols
                row = idx // cols
                x0 = origin_x + col * cell
                y0 = origin_y + row * cell
                x1 = x0 + cell
                y1 = y0 + cell

                # Checkerboard background (visible through
                # transparent regions of the tilesheet)
                shade = 0.25 if (col + row) % 2 == 0 else 0.35
                fill = imgui.get_color_u32_rgba(
                    shade, shade, shade, 0.1)
                draw_list.add_rect_filled(x0, y0, x1, y1, fill)

                # Draw the actual tile image if texture available
                if has_texture:
                    tile_col = idx % ts.tiles_per_row
                    tile_row = idx // ts.tiles_per_row
                    uv0_x = tile_col * TILE_PX * inv_w
                    uv0_y = tile_row * TILE_PX * inv_h
                    uv1_x = (tile_col + 1) * TILE_PX * inv_w
                    uv1_y = (tile_row + 1) * TILE_PX * inv_h
                    draw_list.add_image(
                        state.texture_id,
                        (x0, y0), (x1, y1),
                        (uv0_x, uv0_y),
                        (uv1_x, uv1_y))

                # Grid lines
                draw_list.add_rect(x0, y0, x1, y1, grid_col)

                # Hover highlight
                if idx == state.hovered_index:
                    draw_list.add_rect(
                        x0, y0, x1, y1, hover_col, thickness=2.0)

                # Selection highlight
                if idx == state.selected_index:
                    draw_list.add_rect(
                        x0, y0, x1, y1, sel_col, thickness=2.0)

        imgui.end_child()

        # Bottom bar
        if state.selected_index >= 0:
            imgui.text(f"Selected: {state.selected_index}")
        else:
            imgui.text("Selected: (none)")

        imgui.same_line(imgui.get_content_region_available_width() - 170)

        if imgui.button("OK##tsp_ok", width=80):
            result = state.confirm()
            if result is not None and self._editor_state is not None:
                target = self._picker_target_index
                if 0 <= target < len(self._editor_state.tile_kinds):
                    self._editor_state.tile_kinds[target].value = result
            self._picker_target_index = -1

        imgui.same_line()

        if imgui.button("Cancel##tsp_cancel", width=80):
            state.close()
            self._picker_target_index = -1

        imgui.end()

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
        self._tile_select = TileSelectTool(movement)
        self._chunk_pan = ChunkPanTool(movement, chunk_w, chunk_h)
        self._tile_draw = TileDrawTool()
        self._tools = [
            self._tile_select,
            self._chunk_pan,
            self._tile_draw,
        ]

    def set_movement(self, movement: WorkspaceMovement) -> None:
        """Inject movement into tools."""
        self._movement = movement
        self._tile_select.set_movement(movement)
        self._chunk_pan.set_movement(movement)

    def set_active_tilesheet(self, tilesheet: Optional[Tilesheet]) -> None:
        """Set the active tilesheet for the tile draw tool's picker."""
        self._tile_draw.set_active_tilesheet(tilesheet)

    def set_tilesheet_texture_id(self, texture_id: int) -> None:
        """Set the GL texture ID for the tilesheet."""
        self._tile_draw.set_tilesheet_texture_id(texture_id)

    def set_tile_enums(self, enums: List[CEnum]) -> None:
        self._tile_draw.set_tile_enums(enums)

    def set_layer_info(
            self,
            fields: List[TileLayerField],
            layouts: List[TileLayerLayout]) -> None:
        self._tile_draw.set_layer_info(fields, layouts)

    def set_project_dir(self, project_dir: Path) -> None:
        self._tile_draw.set_project_dir(project_dir)

    def set_on_enum_updated(self, callback: Callable) -> None:
        self._tile_draw.set_on_enum_updated(callback)
