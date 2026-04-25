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
from typing import TYPE_CHECKING, Callable, List, Optional

import imgui

if TYPE_CHECKING:
    from workspace.objects import WorkspaceObjects
    from core.layer_manager import LayerEntry, LayerManager
    from core.tilesheet_manager import TilesheetManager
    from core.tile_parser import TileLayerField, TileLayerLayout


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
