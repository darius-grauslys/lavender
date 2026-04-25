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

import imgui
from pathlib import Path
from typing import Callable, List, Optional


class TileSelectTool(SelectTool):
    name = "Tile Select"
    icon_label = "TS"


class ChunkPanTool(PanTool):
    name = "Chunk Pan"
    icon_label = "CP"


class TileDrawTool(Tool):
    """Tile draw tool with tile list and edit sub-window (spec 1.1.2.1.3)."""

    name = "Tile Draw"
    icon_label = "TD"

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
            changed_val, new_val = imgui.input_int("##val", tk.value, 0, 0)
            if changed_val:
                tk.value = max(0, new_val)
            imgui.same_line()
            changed_name, new_name = imgui.input_text(
                "##name", tk.name, 128)
            if changed_name:
                tk.name = new_name
            imgui.same_line()
            if imgui.small_button("X##del"):
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
            changed, new_idx = imgui.combo(
                "##lsel", current_idx, kind_names)
            if changed and kind_names:
                lt.tile_kind_name = kind_names[new_idx]
            imgui.same_line()
            if imgui.small_button("X##ldel"):
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
            changed, new_idx = imgui.combo(
                "##asel", current_idx, kind_names)
            if changed and kind_names:
                at.tile_kind_name = kind_names[new_idx]
            imgui.same_line()
            if imgui.small_button("X##adel"):
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

    def __init__(self, keybind_manager):
        super().__init__(keybind_manager)
        self._tile_draw = TileDrawTool()
        self._tools = [
            TileSelectTool(),
            ChunkPanTool(),
            self._tile_draw,
        ]

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
