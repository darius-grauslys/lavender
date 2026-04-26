"""
File HUD menu bar — typical editor menu bar with File and Edit menus.

File:
  - Save (Ctrl+S)
  - Exit (with unsaved-changes confirmation)

Edit:
  - Tile submenu:
    - Tilesheets (opens TilesheetViewer)
    - Layer Editor (placeholder)
    - Kind Editor (opens TileKindEditor)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

import imgui

if TYPE_CHECKING:
    from workspace.objects import WorkspaceObjects
    from core.layer_manager import LayerEntry, LayerManager
    from core.tilesheet_manager import TilesheetManager
    from core.tile_parser import TileLayerField, TileLayerLayout

from core.tile_kind_editor import (
    TileKindEditorState,
    TileKindEntry,
    LogicalTileEntry,
    AnimationTileEntry,
    create_editor_state_from_enum,
    write_tile_kind_header,
    get_tilesheet_map_from_state,
    save_tilesheet_mapping,
    load_tilesheet_mapping,
)
from core.c_enum import CEnum


class FileHUD:
    """Editor menu bar drawn at the very top of the window."""

    # Height consumed by the menu bar (approximate).
    MENU_BAR_HEIGHT: float = 20.0

    def __init__(self) -> None:
        # Callbacks wired by EditorApp
        self.on_save: Optional[Callable[[], None]] = None
        self.on_exit: Optional[Callable[[], None]] = None
        self.on_open_tilesheet_viewer: Optional[Callable[[], None]] = None
        self.on_open_layer_editor: Optional[Callable[[], None]] = None
        self.on_open_kind_editor: Optional[Callable[[], None]] = None

        # Exit confirmation prompt state
        self._show_exit_prompt: bool = False

    @property
    def show_exit_prompt(self) -> bool:
        return self._show_exit_prompt

    def draw(self, objects: Optional[WorkspaceObjects] = None) -> None:
        """Draw the main menu bar and any open prompts."""
        if imgui.begin_main_menu_bar():
            self._draw_file_menu(objects)
            self._draw_edit_menu()
            imgui.end_main_menu_bar()

        if self._show_exit_prompt:
            self._draw_exit_prompt()

    def _draw_file_menu(
            self, objects: Optional[WorkspaceObjects]) -> None:
        """Draw the File menu."""
        if imgui.begin_menu("File"):
            if imgui.menu_item("Save", "Ctrl+S")[0]:
                if self.on_save:
                    self.on_save()

            imgui.separator()

            if imgui.menu_item("Exit")[0]:
                self._try_exit(objects)

            imgui.end_menu()

    def _draw_edit_menu(self) -> None:
        """Draw the Edit menu with Tile submenu."""
        if imgui.begin_menu("Edit"):
            if imgui.begin_menu("Tile"):
                if imgui.menu_item("Tilesheets")[0]:
                    if self.on_open_tilesheet_viewer:
                        self.on_open_tilesheet_viewer()

                if imgui.menu_item("Layer Editor")[0]:
                    if self.on_open_layer_editor:
                        self.on_open_layer_editor()

                if imgui.menu_item("Kind Editor")[0]:
                    if self.on_open_kind_editor:
                        self.on_open_kind_editor()

                imgui.end_menu()
            imgui.end_menu()

    def _try_exit(
            self, objects: Optional[WorkspaceObjects]) -> None:
        """Attempt to exit. Show prompt if there are pending .tmp files."""
        has_pending = False
        if objects is not None:
            has_pending = objects.pending_tmp_count > 0

        if has_pending:
            self._show_exit_prompt = True
        else:
            if self.on_exit:
                self.on_exit()

    def _draw_exit_prompt(self) -> None:
        """Draw the exit confirmation prompt overlay."""
        imgui.open_popup("Exit Confirmation##exit_prompt")

        center = imgui.get_io().display_size
        imgui.set_next_window_position(
            center.x * 0.5, center.y * 0.5,
            imgui.ALWAYS, pivot_x=0.5, pivot_y=0.5)
        imgui.set_next_window_size(400, 130)

        flags = (
            imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )

        if imgui.begin_popup_modal(
                "Exit Confirmation##exit_prompt", flags=flags)[0]:
            imgui.text("You have unsaved changes (.tmp files).")
            imgui.text("Quit without saving?")
            imgui.spacing()
            imgui.separator()
            imgui.spacing()

            if imgui.button("Quit Without Saving", width=180):
                self._show_exit_prompt = False
                imgui.close_current_popup()
                if self.on_exit:
                    self.on_exit()

            imgui.same_line()

            if imgui.button("Cancel", width=100):
                self._show_exit_prompt = False
                imgui.close_current_popup()

            imgui.end_popup()
        else:
            # Popup was closed externally
            self._show_exit_prompt = False


class LayerEditorWindow:
    """Layer Editor sub-window.

    Allows adding/removing tile layers, assigning a tilesheet
    to each layer, and configuring bitfield widths.

    On "OK", writes updated tile_layer.h and tile.h to the
    project directory.
    """

    def __init__(self) -> None:
        self.is_open: bool = False
        # Editing copies — committed on OK, discarded on Cancel
        self._entries: List[_LayerEditEntry] = []
        self._selected_index: int = -1
        self._dirty: bool = False

        # Callbacks set by EditorApp
        self.on_ok: Optional[Callable[[List[_LayerEditEntry]], None]] = None
        self.tilesheet_paths: List[str] = []

    def open(
            self,
            layer_manager: Optional[LayerManager] = None,
            tilesheet_paths: Optional[List[str]] = None,
    ) -> None:
        """Open the editor, populating from the current layer manager."""
        self.is_open = True
        self._entries = []
        self._selected_index = -1
        if tilesheet_paths is not None:
            self.tilesheet_paths = list(tilesheet_paths)
        if layer_manager is not None:
            for entry in layer_manager.layers:
                self._entries.append(_LayerEditEntry(
                    layer_name=entry.layer_name,
                    enum_type_name=entry.enum_type_name,
                    tilesheet_path=entry.tilesheet_path,
                    bit_width=entry.bit_width,
                    logic_bits=entry.logic_bits,
                    animation_bits=entry.animation_bits,
                ))
        self._dirty = False

    def close(self) -> None:
        self.is_open = False
        self._entries = []
        self._selected_index = -1

    def draw(self) -> None:
        if not self.is_open:
            return

        imgui.set_next_window_size(750, 450, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            "Layer Editor##layer_ed", True, flags)

        if not opened:
            self.is_open = False
            imgui.end()
            return

        avail = imgui.get_content_region_available()
        list_width = 220.0

        # --- Left panel: layer list ---
        imgui.begin_child("##le_list", list_width, avail.y - 40,
                          border=True)
        imgui.text("Tile Layers:")
        imgui.separator()

        remove_idx: Optional[int] = None
        for i, entry in enumerate(self._entries):
            is_sel = (i == self._selected_index)
            display = entry.layer_name or f"(layer {i})"
            if imgui.selectable(
                    f"{display}##le_{i}", is_sel)[0]:
                self._selected_index = i

            imgui.same_line(
                imgui.get_content_region_available_width() - 20)
            if imgui.small_button(f"X##le_del_{i}"):
                remove_idx = i

        if remove_idx is not None:
            self._entries.pop(remove_idx)
            if self._selected_index >= len(self._entries):
                self._selected_index = len(self._entries) - 1
            self._dirty = True

        imgui.separator()
        if imgui.button("+ Add Layer##le_add",
                        width=imgui.get_content_region_available_width()):
            idx = len(self._entries)
            self._entries.append(_LayerEditEntry(
                layer_name=f"Tile_Layer__{idx}",
                enum_type_name="Tile_Kind",
                tilesheet_path="",
                bit_width=8,
                logic_bits=0,
                animation_bits=0,
            ))
            self._selected_index = idx
            self._dirty = True

        imgui.end_child()

        imgui.same_line()

        # --- Right panel: properties ---
        imgui.begin_child("##le_props", 0, avail.y - 40, border=True)

        if 0 <= self._selected_index < len(self._entries):
            entry = self._entries[self._selected_index]
            self._draw_layer_properties(entry)
        else:
            imgui.text("Select a layer to edit properties.")

        imgui.end_child()

        # --- Bottom buttons ---
        if imgui.button("OK##le_ok", width=100):
            if self.on_ok:
                self.on_ok(self._entries)
            self.is_open = False
            imgui.end()
            return

        imgui.same_line()
        if imgui.button("Cancel##le_cancel", width=100):
            self.is_open = False
            imgui.end()
            return

        imgui.end()

    def _draw_layer_properties(self, entry: _LayerEditEntry) -> None:
        """Draw editable properties for a single layer."""
        imgui.text("Layer Properties:")
        imgui.separator()

        # Layer name
        changed, new_name = imgui.input_text(
            "Layer Name##le_name", entry.layer_name, 128)
        if changed:
            entry.layer_name = new_name
            self._dirty = True

        # Enum type name
        changed, new_enum = imgui.input_text(
            "Enum Type##le_enum", entry.enum_type_name, 128)
        if changed:
            entry.enum_type_name = new_enum
            self._dirty = True

        # Tilesheet dropdown
        imgui.text("Tilesheet:")
        paths = self.tilesheet_paths
        current_idx = -1
        labels = ["(none)"] + paths
        for i, p in enumerate(paths):
            if p == entry.tilesheet_path:
                current_idx = i + 1
                break
        if current_idx < 0:
            current_idx = 0

        changed, new_idx = imgui.combo(
            "##le_ts", current_idx, labels)
        if changed:
            if new_idx == 0:
                entry.tilesheet_path = ""
            else:
                entry.tilesheet_path = paths[new_idx - 1]
            self._dirty = True

        imgui.spacing()
        imgui.separator()
        imgui.text("Bitfield Configuration:")

        # Bit width (1..32)
        changed, new_bw = imgui.input_int(
            "Bit Width##le_bw", entry.bit_width, 1, 1)
        if changed:
            new_bw = max(1, min(32, new_bw))
            entry.bit_width = new_bw
            # Clamp logic+anim to not exceed bit_width
            total_sub = entry.logic_bits + entry.animation_bits
            if total_sub > new_bw:
                # Reduce animation first, then logic
                excess = total_sub - new_bw
                reduce_anim = min(excess, entry.animation_bits)
                entry.animation_bits -= reduce_anim
                excess -= reduce_anim
                entry.logic_bits -= excess
            self._dirty = True

        # Logic bits (0..8, logic+anim <= bit_width)
        max_logic = min(8, entry.bit_width - entry.animation_bits)
        changed, new_lb = imgui.input_int(
            "Logic Bits##le_lb", entry.logic_bits, 1, 1)
        if changed:
            new_lb = max(0, min(max_logic, new_lb))
            entry.logic_bits = new_lb
            self._dirty = True

        # Animation bits (0..8, logic+anim <= bit_width)
        max_anim = min(8, entry.bit_width - entry.logic_bits)
        changed, new_ab = imgui.input_int(
            "Animation Bits##le_ab", entry.animation_bits, 1, 1)
        if changed:
            new_ab = max(0, min(max_anim, new_ab))
            entry.animation_bits = new_ab
            self._dirty = True

        # Show computed remainder
        remainder = entry.bit_width - entry.logic_bits - entry.animation_bits
        imgui.text(f"Remainder Bits: {remainder}")

        # Validation
        err = _validate_layer_entry(entry)
        if err:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.3, 0.3, 1.0)
            imgui.text(f"Error: {err}")
            imgui.pop_style_color()


class KindEditorWindow:
    """Tile Kind Editor sub-window.

    Displays three side-by-side tables for a single tile layer:
      1. Tile Kinds — enum members with tilesheet preview, rename, delete
      2. Logical Tiles — dropdown references into tile kinds
      3. Animation Tiles — dropdown references into tile kinds

    On "OK", writes the updated _kind.h header and tilesheet mapping
    JSON.  On "Cancel", all changes are discarded.

    Follows the same open/close/draw pattern as LayerEditorWindow.
    """

    def __init__(self) -> None:
        self.is_open: bool = False
        self._state: Optional[TileKindEditorState] = None

        # Source data needed for OK commit
        self._header_path: Optional[Path] = None
        self._guard_macro: str = ""

        # Layer selector
        self._layer_names: List[str] = []
        self._layer_enums: List[CEnum] = []
        self._layer_bit_widths: List[int] = []
        self._layer_logic_bits: List[int] = []
        self._layer_animation_bits: List[int] = []
        self._layer_header_paths: List[Path] = []
        self._layer_guard_macros: List[str] = []
        self._selected_layer_index: int = 0

        # Per-layer tilesheet info
        self._layer_tilesheet_texture_ids: List[int] = []
        self._layer_tilesheet_tile_ws: List[int] = []
        self._layer_tilesheet_tile_hs: List[int] = []
        self._layer_tilesheet_cols: List[int] = []
        self._layer_tilesheet_rows: List[int] = []
        self._layer_tilesheet_img_ws: List[int] = []
        self._layer_tilesheet_img_hs: List[int] = []

        # Active tilesheet (set from per-layer lists)
        self._tilesheet_texture_id: int = 0
        self._tilesheet_tile_w: int = 8
        self._tilesheet_tile_h: int = 8
        self._tilesheet_cols: int = 1
        self._tilesheet_rows: int = 1
        self._tilesheet_img_w: int = 0
        self._tilesheet_img_h: int = 0

        # Tileset picker sub-state
        self._picker_open: bool = False
        self._picker_target_index: int = -1
        self._picker_selected_tile: int = -1
        self._picker_hover_tile: int = -1

        # Callbacks set by EditorApp
        self.on_ok: Optional[Callable[[TileKindEditorState, Path, str], None]] = None

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def open(
            self,
            layer_names: List[str],
            layer_enums: List[CEnum],
            layer_bit_widths: List[int],
            layer_logic_bits: List[int],
            layer_animation_bits: List[int],
            layer_header_paths: List[Path],
            layer_guard_macros: List[str],
            layer_tilesheet_texture_ids: Optional[List[int]] = None,
            layer_tilesheet_tile_ws: Optional[List[int]] = None,
            layer_tilesheet_tile_hs: Optional[List[int]] = None,
            layer_tilesheet_cols: Optional[List[int]] = None,
            layer_tilesheet_rows: Optional[List[int]] = None,
            layer_tilesheet_img_ws: Optional[List[int]] = None,
            layer_tilesheet_img_hs: Optional[List[int]] = None,
    ) -> None:
        """Open the editor for the first available layer."""
        self.is_open = True
        n = len(layer_names)
        self._layer_names = list(layer_names)
        self._layer_enums = list(layer_enums)
        self._layer_bit_widths = list(layer_bit_widths)
        self._layer_logic_bits = list(layer_logic_bits)
        self._layer_animation_bits = list(layer_animation_bits)
        self._layer_header_paths = list(layer_header_paths)
        self._layer_guard_macros = list(layer_guard_macros)

        self._layer_tilesheet_texture_ids = (
            list(layer_tilesheet_texture_ids) if layer_tilesheet_texture_ids
            else [0] * n)
        self._layer_tilesheet_tile_ws = (
            list(layer_tilesheet_tile_ws) if layer_tilesheet_tile_ws
            else [8] * n)
        self._layer_tilesheet_tile_hs = (
            list(layer_tilesheet_tile_hs) if layer_tilesheet_tile_hs
            else [8] * n)
        self._layer_tilesheet_cols = (
            list(layer_tilesheet_cols) if layer_tilesheet_cols
            else [1] * n)
        self._layer_tilesheet_rows = (
            list(layer_tilesheet_rows) if layer_tilesheet_rows
            else [1] * n)
        self._layer_tilesheet_img_ws = (
            list(layer_tilesheet_img_ws) if layer_tilesheet_img_ws
            else [0] * n)
        self._layer_tilesheet_img_hs = (
            list(layer_tilesheet_img_hs) if layer_tilesheet_img_hs
            else [0] * n)

        self._picker_open = False
        self._picker_target_index = -1
        self._picker_selected_tile = -1
        self._picker_hover_tile = -1

        self._selected_layer_index = 0
        self._load_layer(0)

    def close(self) -> None:
        self.is_open = False
        self._state = None
        self._picker_open = False

    def draw(self) -> None:
        """Draw the Kind Editor window (call every frame)."""
        if not self.is_open:
            return

        imgui.set_next_window_size(900, 520, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            "Tile Kind Editor##kind_ed", True, flags)

        if not opened:
            self.is_open = False
            imgui.end()
            return

        # Layer selector dropdown
        if self._layer_names:
            changed, new_idx = imgui.combo(
                "Layer##ke_layer", self._selected_layer_index,
                self._layer_names)
            if changed and new_idx != self._selected_layer_index:
                self._selected_layer_index = new_idx
                self._load_layer(new_idx)

        if self._state is None:
            imgui.text("No layer data loaded.")
            if imgui.button("Cancel##ke_cancel", width=100):
                self.is_open = False
            imgui.end()
            return

        imgui.separator()

        avail = imgui.get_content_region_available()
        table_height = avail.y - 40  # room for OK/Cancel

        # Three tables side by side
        col_width = avail.x / 3.0 - 6

        # --- Table 1: Tile Kinds ---
        imgui.begin_child("##ke_kinds", col_width, table_height,
                          border=True)
        self._draw_tile_kinds_table()
        imgui.end_child()

        imgui.same_line()

        # --- Table 2: Logical Tiles ---
        imgui.begin_child("##ke_logic", col_width, table_height,
                          border=True)
        self._draw_logical_tiles_table()
        imgui.end_child()

        imgui.same_line()

        # --- Table 3: Animation Tiles ---
        imgui.begin_child("##ke_anim", col_width, table_height,
                          border=True)
        self._draw_animation_tiles_table()
        imgui.end_child()

        # --- Bottom buttons ---
        if imgui.button("OK##ke_ok", width=100):
            self._commit()
            self.is_open = False
            imgui.end()
            return

        imgui.same_line()
        if imgui.button("Cancel##ke_cancel", width=100):
            self.is_open = False
            imgui.end()
            return

        imgui.end()

        # Tileset picker overlay (drawn outside the main window)
        if self._picker_open:
            self._draw_tileset_picker()

    # ------------------------------------------------------------------ #
    # Layer loading                                                       #
    # ------------------------------------------------------------------ #

    def _update_tilesheet_for_layer(self, index: int) -> None:
        """Update active tilesheet fields from the per-layer lists."""
        if 0 <= index < len(self._layer_tilesheet_texture_ids):
            self._tilesheet_texture_id = self._layer_tilesheet_texture_ids[index]
            self._tilesheet_tile_w = self._layer_tilesheet_tile_ws[index]
            self._tilesheet_tile_h = self._layer_tilesheet_tile_hs[index]
            self._tilesheet_cols = self._layer_tilesheet_cols[index]
            self._tilesheet_rows = self._layer_tilesheet_rows[index]
            self._tilesheet_img_w = self._layer_tilesheet_img_ws[index]
            self._tilesheet_img_h = self._layer_tilesheet_img_hs[index]
        else:
            self._tilesheet_texture_id = 0
            self._tilesheet_tile_w = 8
            self._tilesheet_tile_h = 8
            self._tilesheet_cols = 1
            self._tilesheet_rows = 1
            self._tilesheet_img_w = 0
            self._tilesheet_img_h = 0

    def _load_layer(self, index: int) -> None:
        """Load a layer's enum into the editing state."""
        if index < 0 or index >= len(self._layer_enums):
            self._state = None
            return

        self._update_tilesheet_for_layer(index)

        enum = self._layer_enums[index]
        header_path = self._layer_header_paths[index]
        tilesheet_map = load_tilesheet_mapping(header_path)

        self._state = create_editor_state_from_enum(
            enum=enum,
            layer_name=self._layer_names[index],
            render_bit_width=self._layer_bit_widths[index],
            logic_bits=self._layer_logic_bits[index],
            animation_bits=self._layer_animation_bits[index],
            tilesheet_map=tilesheet_map,
        )
        self._header_path = header_path
        self._guard_macro = self._layer_guard_macros[index]

    # ------------------------------------------------------------------ #
    # Table 1: Tile Kinds                                                 #
    # ------------------------------------------------------------------ #

    def _draw_tile_kinds_table(self) -> None:
        state = self._state
        assert state is not None

        imgui.text(f"Tile Kinds - {state.layer_name}")
        imgui.separator()

        # Filter
        changed, state.kind_filter = imgui.input_text(
            "##ke_kf", state.kind_filter, 128)

        imgui.begin_child("##ke_kind_list", 0, -30, border=False)

        remove_idx: Optional[int] = None
        filt = state.kind_filter.lower()

        for i, tk in enumerate(state.tile_kinds):
            if filt and filt not in tk.name.lower():
                continue

            imgui.push_id(f"tk_{i}")

            # Tilesheet preview button
            self._draw_tile_preview_button(i, tk)
            imgui.same_line()

            # Editable name
            imgui.push_item_width(
                imgui.get_content_region_available_width() - 30)
            ch, new_name = imgui.input_text(
                "##name", tk.name, 128)
            if ch:
                tk.name = new_name
            imgui.pop_item_width()

            imgui.same_line()
            if imgui.small_button("X##del"):
                remove_idx = i

            imgui.pop_id()

        imgui.end_child()

        if remove_idx is not None:
            state.remove_tile_kind(remove_idx)

        # Add button
        can_add = state.can_add_tile_kind
        if not can_add:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
        if imgui.button("+##ke_add_kind",
                        width=imgui.get_content_region_available_width()):
            if can_add:
                state.add_tile_kind()
        if not can_add:
            imgui.pop_style_var()

    def _draw_tile_preview_button(
            self, index: int, tk: TileKindEntry) -> None:
        """Draw a small button showing the assigned tilesheet tile."""
        btn_size = 24
        tile_idx = tk.tilesheet_tile_index

        if (tile_idx >= 0
                and self._tilesheet_texture_id != 0
                and self._tilesheet_cols > 0):
            # Compute UV coords
            col = tile_idx % self._tilesheet_cols
            row = tile_idx // self._tilesheet_cols
            u0 = col * self._tilesheet_tile_w / max(
                1, self._tilesheet_img_w)
            v0 = row * self._tilesheet_tile_h / max(
                1, self._tilesheet_img_h)
            u1 = u0 + self._tilesheet_tile_w / max(
                1, self._tilesheet_img_w)
            v1 = v0 + self._tilesheet_tile_h / max(
                1, self._tilesheet_img_h)
            if imgui.image_button(
                    self._tilesheet_texture_id,
                    btn_size, btn_size,
                    uv0=(u0, v0), uv1=(u1, v1)):
                self._open_picker(index, tile_idx)
        else:
            if imgui.button(f"[?]##prev_{index}",
                            width=btn_size, height=btn_size):
                self._open_picker(index, tile_idx)

    # ------------------------------------------------------------------ #
    # Table 2: Logical Tiles                                              #
    # ------------------------------------------------------------------ #

    def _draw_logical_tiles_table(self) -> None:
        state = self._state
        assert state is not None

        disabled = state.logic_bits == 0
        header = ("Logical Tiles (disabled)"
                  if disabled else "Logical Tiles")
        imgui.text(header)
        imgui.separator()

        # Filter
        changed, state.logic_filter = imgui.input_text(
            "##ke_lf", state.logic_filter, 128)

        imgui.begin_child("##ke_logic_list", 0, -30, border=False)

        kind_names = [tk.name for tk in state.tile_kinds]
        filt = state.logic_filter.lower()
        remove_idx: Optional[int] = None

        for i, lt in enumerate(state.logical_tiles):
            if filt and filt not in lt.tile_kind_name.lower():
                continue

            imgui.push_id(f"lt_{i}")

            # Dropdown selecting from tile kinds
            current = -1
            for ki, kn in enumerate(kind_names):
                if kn == lt.tile_kind_name:
                    current = ki
                    break
            if current < 0:
                current = 0

            imgui.push_item_width(
                imgui.get_content_region_available_width() - 30)
            ch, new_sel = imgui.combo("##sel", current, kind_names)
            if ch and 0 <= new_sel < len(kind_names):
                lt.tile_kind_name = kind_names[new_sel]
            imgui.pop_item_width()

            imgui.same_line()
            if imgui.small_button("X##ldel"):
                remove_idx = i

            imgui.pop_id()

        imgui.end_child()

        if remove_idx is not None:
            state.remove_logical_tile(remove_idx)

        can_add = state.can_add_logical_tile
        if not can_add:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
        if imgui.button("+##ke_add_logic",
                        width=imgui.get_content_region_available_width()):
            if can_add:
                state.add_logical_tile()
        if not can_add:
            imgui.pop_style_var()

    # ------------------------------------------------------------------ #
    # Table 3: Animation Tiles                                            #
    # ------------------------------------------------------------------ #

    def _draw_animation_tiles_table(self) -> None:
        state = self._state
        assert state is not None

        disabled = state.animation_bits == 0
        header = ("Animation Tiles (disabled)"
                  if disabled else "Animation Tiles")
        imgui.text(header)
        imgui.separator()

        # Filter
        changed, state.animation_filter = imgui.input_text(
            "##ke_af", state.animation_filter, 128)

        imgui.begin_child("##ke_anim_list", 0, -30, border=False)

        kind_names = [tk.name for tk in state.tile_kinds]
        filt = state.animation_filter.lower()
        remove_idx: Optional[int] = None

        for i, at in enumerate(state.animation_tiles):
            if filt and filt not in at.tile_kind_name.lower():
                continue

            imgui.push_id(f"at_{i}")

            current = -1
            for ki, kn in enumerate(kind_names):
                if kn == at.tile_kind_name:
                    current = ki
                    break
            if current < 0:
                current = 0

            imgui.push_item_width(
                imgui.get_content_region_available_width() - 30)
            ch, new_sel = imgui.combo("##sel", current, kind_names)
            if ch and 0 <= new_sel < len(kind_names):
                at.tile_kind_name = kind_names[new_sel]
            imgui.pop_item_width()

            imgui.same_line()
            if imgui.small_button("X##adel"):
                remove_idx = i

            imgui.pop_id()

        imgui.end_child()

        if remove_idx is not None:
            state.remove_animation_tile(remove_idx)

        can_add = state.can_add_animation_tile
        if not can_add:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
        if imgui.button("+##ke_add_anim",
                        width=imgui.get_content_region_available_width()):
            if can_add:
                state.add_animation_tile()
        if not can_add:
            imgui.pop_style_var()

    # ------------------------------------------------------------------ #
    # Tileset Picker                                                      #
    # ------------------------------------------------------------------ #

    def _open_picker(self, kind_index: int, current_tile: int) -> None:
        self._picker_open = True
        self._picker_target_index = kind_index
        self._picker_selected_tile = current_tile
        self._picker_hover_tile = -1

    def _draw_tileset_picker(self) -> None:
        """Draw the tileset picker overlay sub-window."""
        imgui.set_next_window_size(420, 440, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            "Tileset Picker##ts_picker", True, flags)

        if not opened:
            self._picker_open = False
            imgui.end()
            return

        if self._tilesheet_texture_id == 0:
            imgui.text("No tilesheet loaded.")
            if imgui.button("Cancel##pk_cancel", width=100):
                self._picker_open = False
            imgui.end()
            return

        zoom = 2
        cell_w = self._tilesheet_tile_w * zoom
        cell_h = self._tilesheet_tile_h * zoom
        cols = self._tilesheet_cols
        rows = self._tilesheet_rows
        total_tiles = cols * rows

        imgui.text(
            f"Select a tile (current: {self._picker_selected_tile})")
        imgui.separator()

        imgui.begin_child("##pk_grid", 0, -40, border=True)

        grid_hovered = imgui.is_window_hovered()
        draw_list = imgui.get_window_draw_list()
        win_pos = imgui.get_cursor_screen_pos()
        mouse = imgui.get_mouse_position()

        self._picker_hover_tile = -1

        for idx in range(total_tiles):
            col = idx % cols
            row = idx // cols

            x0 = win_pos.x + col * cell_w
            y0 = win_pos.y + row * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h

            # UV
            u0 = col * self._tilesheet_tile_w / max(
                1, self._tilesheet_img_w)
            v0 = row * self._tilesheet_tile_h / max(
                1, self._tilesheet_img_h)
            u1 = u0 + self._tilesheet_tile_w / max(
                1, self._tilesheet_img_w)
            v1 = v0 + self._tilesheet_tile_h / max(
                1, self._tilesheet_img_h)

            draw_list.add_image(
                self._tilesheet_texture_id,
                (x0, y0), (x1, y1),
                (u0, v0), (u1, v1))

            hovered = (x0 <= mouse.x < x1 and y0 <= mouse.y < y1)
            if hovered:
                self._picker_hover_tile = idx
                draw_list.add_rect(
                    x0, y0, x1, y1,
                    imgui.get_color_u32_rgba(1.0, 1.0, 0.0, 1.0), 0, 0, 2)
                if grid_hovered and imgui.is_mouse_clicked(0):
                    self._picker_selected_tile = idx

            if idx == self._picker_selected_tile:
                draw_list.add_rect(
                    x0, y0, x1, y1,
                    imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0), 0, 0, 2)

        # Set dummy to reserve scroll space
        total_h = rows * cell_h
        imgui.dummy(cols * cell_w, total_h)

        imgui.end_child()

        imgui.text(f"Selected: {self._picker_selected_tile}")
        imgui.same_line()

        if imgui.button("OK##pk_ok", width=80):
            self._apply_picker_selection()
            self._picker_open = False

        imgui.same_line()
        if imgui.button("Cancel##pk_cancel2", width=80):
            self._picker_open = False

        imgui.end()

    def _apply_picker_selection(self) -> None:
        """Apply the picker's selected tile to the target tile kind."""
        if (self._state is not None
                and 0 <= self._picker_target_index
                < len(self._state.tile_kinds)):
            self._state.tile_kinds[
                self._picker_target_index
            ].tilesheet_tile_index = self._picker_selected_tile

    # ------------------------------------------------------------------ #
    # Commit                                                              #
    # ------------------------------------------------------------------ #

    def _commit(self) -> None:
        """Write changes to disk and invoke the on_ok callback."""
        if self._state is None or self._header_path is None:
            return

        # Write the _kind.h header
        write_tile_kind_header(
            self._header_path, self._state, self._guard_macro)

        # Save tilesheet mapping JSON
        mapping = get_tilesheet_map_from_state(self._state)
        save_tilesheet_mapping(self._header_path, mapping)

        if self.on_ok:
            self.on_ok(
                self._state, self._header_path, self._guard_macro)


class _LayerEditEntry:
    """Mutable editing copy of a layer entry."""
    __slots__ = (
        'layer_name', 'enum_type_name', 'tilesheet_path',
        'bit_width', 'logic_bits', 'animation_bits',
    )

    def __init__(
            self,
            layer_name: str = "",
            enum_type_name: str = "Tile_Kind",
            tilesheet_path: str = "",
            bit_width: int = 8,
            logic_bits: int = 0,
            animation_bits: int = 0):
        self.layer_name = layer_name
        self.enum_type_name = enum_type_name
        self.tilesheet_path = tilesheet_path
        self.bit_width = bit_width
        self.logic_bits = logic_bits
        self.animation_bits = animation_bits


def _validate_layer_entry(entry: _LayerEditEntry) -> Optional[str]:
    """Return an error string if the entry is invalid."""
    if entry.bit_width < 1 or entry.bit_width > 32:
        return f"bit_width must be 1..32, got {entry.bit_width}"
    if entry.logic_bits < 0 or entry.logic_bits > 8:
        return f"logic_bits must be 0..8, got {entry.logic_bits}"
    if entry.animation_bits < 0 or entry.animation_bits > 8:
        return f"animation_bits must be 0..8, got {entry.animation_bits}"
    if entry.logic_bits + entry.animation_bits > entry.bit_width:
        return (
            f"logic({entry.logic_bits}) + anim({entry.animation_bits}) "
            f"exceeds bit_width({entry.bit_width})")
    return None
