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

from typing import TYPE_CHECKING, Callable, Optional

import imgui

if TYPE_CHECKING:
    from workspace.objects import WorkspaceObjects


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
    """Placeholder Layer Editor sub-window."""

    def __init__(self) -> None:
        self.is_open: bool = False

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def draw(self) -> None:
        if not self.is_open:
            return

        imgui.set_next_window_size(400, 300, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            "Layer Editor##layer_ed", True, flags)

        if not opened:
            self.is_open = False
            imgui.end()
            return

        imgui.text("Layer Editor — Not yet implemented.")
        imgui.end()
