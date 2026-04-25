"""
Tilesheet Viewer sub-window.

Displays a list of loaded tilesheets on the left and the
selected tilesheet image centered on the right.

Integrates with TilesheetManager for data and
tilesheet_browser for adding new sheets.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

import imgui

from core.tilesheet import TILE_PX

if TYPE_CHECKING:
    from core.tilesheet_manager import TilesheetManager
    from ui.message_hud import MessageHUD


class TilesheetViewer:
    """Sub-window for viewing and managing tilesheets."""

    def __init__(self) -> None:
        self.is_open: bool = False
        self._pending_add: bool = False
        self._zoom: int = 2

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False
        self._pending_add = False

    def draw(
            self,
            tilesheet_manager: TilesheetManager,
            project_dir: Path,
            world_name: str,
            message_hud: Optional[MessageHUD] = None,
            upload_texture_callback=None) -> None:
        """Draw the tilesheet viewer sub-window.

        Args:
            tilesheet_manager: The tilesheet manager.
            project_dir: Project root directory.
            world_name: Active world name (for browse context).
            message_hud: Optional message HUD for logging.
            upload_texture_callback: Callable(entry) to upload
                GL texture for a newly added tilesheet entry.
        """
        if not self.is_open:
            return

        imgui.set_next_window_size(700, 500, imgui.FIRST_USE_EVER)
        flags = imgui.WINDOW_NO_SAVED_SETTINGS
        expanded, opened = imgui.begin(
            "Tilesheet Viewer##tsv", True, flags)

        if not opened:
            self.is_open = False
            imgui.end()
            return

        avail = imgui.get_content_region_available()
        list_width = 200.0

        # --- Left panel: tilesheet list ---
        imgui.begin_child(
            "##tsv_list", list_width, 0, border=True)

        imgui.text("Tilesheets:")
        imgui.separator()

        remove_path: Optional[str] = None
        entries = tilesheet_manager.entries
        for entry in entries:
            is_active = (
                entry.relative_path == tilesheet_manager.active_path)
            # Truncate display name
            display = entry.relative_path
            if len(display) > 22:
                display = "..." + display[-19:]

            if imgui.selectable(
                    f"{display}##{entry.relative_path}",
                    is_active)[0]:
                tilesheet_manager.active_path = entry.relative_path

            imgui.same_line(
                imgui.get_content_region_available_width() - 20)
            if imgui.small_button(f"X##{entry.relative_path}"):
                remove_path = entry.relative_path

        if remove_path is not None:
            removed = tilesheet_manager.remove(remove_path)
            if removed and removed.gl_texture_id:
                try:
                    import OpenGL.GL as gl
                    gl.glDeleteTextures([removed.gl_texture_id])
                except Exception:
                    pass
            if message_hud:
                message_hud.info(
                    f"Removed tilesheet: {remove_path}")

        imgui.separator()
        if imgui.button("+ Add Sheet +##tsv_add",
                        width=imgui.get_content_region_available_width()):
            self._pending_add = True

        imgui.end_child()

        imgui.same_line()

        # --- Right panel: tilesheet display ---
        imgui.begin_child("##tsv_display", 0, 0, border=True)

        active = tilesheet_manager.active_entry
        if active is None:
            imgui.text("No tilesheet selected.")
        elif active.gl_texture_id == 0:
            imgui.text(f"Tilesheet: {active.relative_path}")
            imgui.text("(GL texture not uploaded)")
        else:
            ts = active.tilesheet
            display_w = ts.width * self._zoom
            display_h = ts.height * self._zoom

            imgui.text(
                f"{active.relative_path}  "
                f"({ts.width}x{ts.height}, "
                f"{ts.total_tiles} tiles)")
            imgui.separator()

            # Center the image in available space
            child_avail = imgui.get_content_region_available()
            pad_x = max(0, (child_avail.x - display_w) * 0.5)
            pad_y = max(0, (child_avail.y - display_h - 30) * 0.5)

            if pad_x > 0:
                imgui.set_cursor_pos_x(
                    imgui.get_cursor_pos_x() + pad_x)
            if pad_y > 0:
                imgui.set_cursor_pos_y(
                    imgui.get_cursor_pos_y() + pad_y)

            imgui.image(
                active.gl_texture_id,
                display_w, display_h,
                uv0=(0, 0), uv1=(1, 1))

        imgui.end_child()

        imgui.end()

        # Handle pending add via browser
        if self._pending_add:
            self._pending_add = False
            self._do_add_tilesheet(
                tilesheet_manager, project_dir, world_name,
                message_hud, upload_texture_callback)

    def _do_add_tilesheet(
            self,
            tilesheet_manager: TilesheetManager,
            project_dir: Path,
            world_name: str,
            message_hud,
            upload_texture_callback) -> None:
        """Open the file browser and add the selected tilesheet."""
        from core.tilesheet_browser import browse_and_set_tilesheet

        rel_path, tilesheet = browse_and_set_tilesheet(
            project_dir, world_name, message_hud)

        if rel_path and tilesheet:
            entry = tilesheet_manager.add(rel_path, tilesheet)
            if upload_texture_callback:
                upload_texture_callback(entry)
            tilesheet_manager.active_path = rel_path
            if message_hud:
                message_hud.info(
                    f"Added tilesheet: {rel_path}")
