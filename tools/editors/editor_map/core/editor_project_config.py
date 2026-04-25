"""
Load and manage editor configuration files.

Two levels of configuration:
1. Project-level: ./assets/world/editor.json
   Contains global editor settings (currently unused but reserved).
2. Per-world: ./save/<world_name>/editor.json
   Contains world-specific settings such as the tilesheet path.
   When a world is selected in the file hierarchy, its tilesheet
   becomes the active tilesheet in the editor.

Per-world schema:
{
    "tilesheet": {
        "path": "assets/world/tilesheet.png"
    }
}

Project-level schema:
{
    "version": 1
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


EDITOR_CONFIG_RELATIVE_PATH = Path("assets") / "world" / "editor.json"
WORLD_CONFIG_FILENAME = "editor.json"

DEFAULT_PROJECT_CONFIG = {
    "version": 1
}

DEFAULT_WORLD_CONFIG = {
    "tilesheet": {
        "path": ""
    }
}


@dataclass
class EditorProjectConfig:
    """Parsed project-level editor configuration."""
    version: int = 1

    @property
    def tilesheet_path(self) -> str:
        """
        Deprecated: tilesheet is now per-world (WorldEditorConfig).
        Kept for backward compatibility so callers that still
        reference ``config.tilesheet_path`` get an empty string
        instead of an AttributeError.
        """
        return ""

    def resolve_tilesheet(self, project_dir: Path) -> Optional[Path]:
        """
        Deprecated: tilesheet is now per-world.
        Kept for backward compatibility; always returns None.
        """
        return None


@dataclass
class WorldEditorConfig:
    """Parsed per-world editor configuration."""
    tilesheet_path: str = ""

    def resolve_tilesheet(self, project_dir: Path) -> Optional[Path]:
        """
        Resolve the tilesheet path relative to the project directory.
        Returns the Path if it exists and is a .png file, else None.
        """
        if not self.tilesheet_path:
            return None
        resolved = project_dir / self.tilesheet_path
        if resolved.exists() and resolved.suffix.lower() == '.png':
            return resolved
        return None


def world_config_path(project_dir: Path, world_name: str) -> Path:
    """Get the path to a world's editor.json."""
    return project_dir / "save" / world_name / WORLD_CONFIG_FILENAME


def load_editor_project_config(project_dir: Path) -> EditorProjectConfig:
    """
    Load the project-level editor.json.
    If the file does not exist, generate it with defaults.
    """
    config_path = project_dir / EDITOR_CONFIG_RELATIVE_PATH

    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(DEFAULT_PROJECT_CONFIG, indent=4) + "\n",
            encoding='utf-8')
        return EditorProjectConfig()

    try:
        data = json.loads(
            config_path.read_text(encoding='utf-8', errors='replace'))
    except (json.JSONDecodeError, OSError):
        return EditorProjectConfig()

    version = data.get("version", 1)
    return EditorProjectConfig(version=version)


def save_editor_project_config(
        project_dir: Path,
        config: EditorProjectConfig) -> None:
    """Save the project-level editor config back to editor.json."""
    config_path = project_dir / EDITOR_CONFIG_RELATIVE_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": config.version
    }
    config_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')


def load_world_editor_config(
        project_dir: Path,
        world_name: str) -> WorldEditorConfig:
    """
    Load the per-world editor.json from inside the world folder.
    If the file does not exist, generate it with defaults.
    """
    cfg_path = world_config_path(project_dir, world_name)

    if not cfg_path.exists():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(
            json.dumps(DEFAULT_WORLD_CONFIG, indent=4) + "\n",
            encoding='utf-8')
        return WorldEditorConfig()

    try:
        data = json.loads(
            cfg_path.read_text(encoding='utf-8', errors='replace'))
    except (json.JSONDecodeError, OSError):
        return WorldEditorConfig()

    tilesheet_path = ""
    tilesheet = data.get("tilesheet", {})
    if isinstance(tilesheet, dict):
        tilesheet_path = tilesheet.get("path", "")

    return WorldEditorConfig(tilesheet_path=tilesheet_path)


def save_world_editor_config(
        project_dir: Path,
        world_name: str,
        config: WorldEditorConfig) -> None:
    """Save the per-world editor config back to its editor.json."""
    cfg_path = world_config_path(project_dir, world_name)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tilesheet": {
            "path": config.tilesheet_path
        }
    }
    cfg_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')
