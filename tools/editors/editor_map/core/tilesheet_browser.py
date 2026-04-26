"""
Tilesheet file browser utility.

Handles opening a native file dialog to select a tilesheet PNG,
validating the selection, converting to a project-relative path,
saving to the per-world editor config, and reloading the tilesheet.

See spec sections 1.4 and 4.5.4.2.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from core.editor_project_config import (
    load_world_editor_config,
    save_world_editor_config,
)
from core.tilesheet import Tilesheet, load_tilesheet

if TYPE_CHECKING:
    from ui.message_hud import MessageHUD


def _open_png_file_dialog(
        message_hud: Optional[MessageHUD] = None,
        default_directory: Optional[Path] = None,
) -> Optional[str]:
    """
    Open a native file browser dialog filtered to .png files.

    Returns the selected absolute path as a string, or None
    if the user cancelled or an error occurred.

    Uses portable_file_dialogs from imgui_bundle for native
    OS file dialogs.
    """
    try:
        from imgui_bundle import portable_file_dialogs as pfd

        start_dir = str(default_directory) if default_directory else ""

        selection = pfd.open_file(
            "Select Tilesheet PNG",
            start_dir,
            ["PNG images", "*.png", "All files", "*.*"],
        ).result()

        if not selection:
            return None
        return selection[0]
    except ImportError:
        if message_hud:
            message_hud.error(
                "Failed to open file dialog: "
                "imgui_bundle.portable_file_dialogs is not available.")
        return None
    except Exception as e:
        if message_hud:
            message_hud.error(
                f"Failed to open file dialog: {e}")
        return None


def _make_project_relative(
        absolute_path: str,
        project_dir: Path,
) -> Optional[str]:
    """
    Convert an absolute path to a project-relative path.

    Returns the relative path string, or None if the path
    cannot be made relative (e.g. on a different drive on Windows).
    """
    try:
        rel = os.path.relpath(absolute_path, str(project_dir))
        return rel
    except ValueError:
        return None


def _validate_png_path(path: Path) -> bool:
    """Validate that the path exists, is a file, and is a .png."""
    return path.exists() and path.is_file() and path.suffix.lower() == ".png"


def browse_and_set_tilesheet(
        project_dir: Path,
        world_name: str,
        message_hud: Optional[MessageHUD] = None,
        platform: str = "",
) -> Tuple[Optional[str], Optional[Tilesheet]]:
    """
    Open a file browser, validate the selection, save to config,
    and reload the tilesheet.

    Args:
        project_dir: The project root directory.
        world_name: The name of the currently selected world.
        message_hud: Optional MessageHUD for logging.

    Returns:
        A tuple of (relative_path, loaded_tilesheet).
        Both are None if the operation was cancelled or failed.
    """
    if not world_name:
        if message_hud:
            message_hud.error(
                "Cannot browse for tilesheet: no world selected.")
        return None, None

    selected = _open_png_file_dialog(message_hud, project_dir)
    if selected is None:
        return None, None

    abs_path = Path(selected)

    if not _validate_png_path(abs_path):
        if message_hud:
            message_hud.error(
                f"Invalid tilesheet file: {selected} "
                f"(must be an existing .png file).")
        return None, None

    rel_path = _make_project_relative(selected, project_dir)
    if rel_path is None:
        if message_hud:
            message_hud.error(
                f"Cannot make path relative to project: {selected}")
        return None, None

    # Normalise to forward slashes for cross-platform consistency
    rel_path = rel_path.replace("\\", "/")

    # Save to per-world config
    config = load_world_editor_config(project_dir, world_name, platform=platform)
    if rel_path not in config.tilesheets:
        config.tilesheets.append(rel_path)
    save_world_editor_config(project_dir, world_name, config, platform=platform)

    # Load the tilesheet
    tilesheet = load_tilesheet(abs_path)
    if tilesheet is None:
        if message_hud:
            message_hud.error(
                f"Failed to load tilesheet image: {rel_path}")
        return rel_path, None

    if message_hud:
        message_hud.info(
            f"Tilesheet set to: {rel_path} "
            f"({tilesheet.total_tiles} tiles)")

    return rel_path, tilesheet


def clear_tilesheet(
        project_dir: Path,
        world_name: str,
        message_hud: Optional[MessageHUD] = None,
        platform: str = "",
) -> None:
    """
    Clear the tilesheet path from the per-world config.

    Args:
        project_dir: The project root directory.
        world_name: The name of the currently selected world.
        message_hud: Optional MessageHUD for logging.
    """
    if not world_name:
        if message_hud:
            message_hud.error(
                "Cannot clear tilesheet: no world selected.")
        return

    config = load_world_editor_config(project_dir, world_name, platform=platform)
    config.tilesheets.clear()
    save_world_editor_config(project_dir, world_name, config, platform=platform)

    if message_hud:
        message_hud.info("All tilesheets cleared.")


