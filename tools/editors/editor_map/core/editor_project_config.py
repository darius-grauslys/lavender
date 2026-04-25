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
BUILD_CONFIG_FILENAME = "editor.config"
WORLD_CONFIG_FILENAME = "editor.json"

DEFAULT_PROJECT_CONFIG = {
    "version": 1,
    "max_tmp_chunks": 1024
}

DEFAULT_WORLD_CONFIG = {
    "tilesheet": {
        "path": ""
    },
    "workspace_position": {
        "x": 0,
        "y": 0,
        "z": 0
    }
}

DEFAULT_BUILD_CONFIG = {
    "last_world": "",
    "workspace_position": {
        "x": 0,
        "y": 0,
        "z": 0
    }
}


@dataclass
class EditorBuildConfig:
    """Parsed build-level editor configuration.

    Stored at ``./build/editor.config``.
    Tracks the last selected world and workspace position
    so the editor can restore state on startup.
    """
    last_world: str = ""
    workspace_x: int = 0
    workspace_y: int = 0
    workspace_z: int = 0


@dataclass
class EditorProjectConfig:
    """Parsed project-level editor configuration."""
    version: int = 1
    max_tmp_chunks: int = 1024

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
    workspace_x: int = 0
    workspace_y: int = 0
    workspace_z: int = 0

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


def build_config_path(project_dir: Path) -> Path:
    """Get the path to the build-level editor.config."""
    return project_dir / "build" / BUILD_CONFIG_FILENAME


def world_config_path(
        project_dir: Path,
        world_name: str,
        platform: str = "") -> Path:
    """Get the path to a world's editor.json."""
    if platform:
        from core.world_directory import saves_root
        return (saves_root(project_dir, platform)
                / world_name / WORLD_CONFIG_FILENAME)
    return project_dir / "save" / world_name / WORLD_CONFIG_FILENAME


def load_build_config(project_dir: Path) -> EditorBuildConfig:
    """Load the build-level editor.config.

    If the file does not exist, generate it with defaults.
    """
    cfg_path = build_config_path(project_dir)

    if not cfg_path.exists():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(
            json.dumps(DEFAULT_BUILD_CONFIG, indent=4) + "\n",
            encoding='utf-8')
        return EditorBuildConfig()

    try:
        data = json.loads(
            cfg_path.read_text(encoding='utf-8', errors='replace'))
    except (json.JSONDecodeError, OSError):
        return EditorBuildConfig()

    ws = data.get("workspace_position", {})
    return EditorBuildConfig(
        last_world=data.get("last_world", ""),
        workspace_x=ws.get("x", 0),
        workspace_y=ws.get("y", 0),
        workspace_z=ws.get("z", 0),
    )


def save_build_config(
        project_dir: Path,
        config: EditorBuildConfig) -> None:
    """Save the build-level editor.config."""
    cfg_path = build_config_path(project_dir)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "last_world": config.last_world,
        "workspace_position": {
            "x": config.workspace_x,
            "y": config.workspace_y,
            "z": config.workspace_z,
        }
    }
    cfg_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')


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
    max_tmp = data.get("max_tmp_chunks", 1024)
    return EditorProjectConfig(version=version, max_tmp_chunks=max_tmp)


def save_editor_project_config(
        project_dir: Path,
        config: EditorProjectConfig) -> None:
    """Save the project-level editor config back to editor.json."""
    config_path = project_dir / EDITOR_CONFIG_RELATIVE_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": config.version,
        "max_tmp_chunks": config.max_tmp_chunks,
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

    ws = data.get("workspace_position", {})
    return WorldEditorConfig(
        tilesheet_path=tilesheet_path,
        workspace_x=ws.get("x", 0),
        workspace_y=ws.get("y", 0),
        workspace_z=ws.get("z", 0),
    )


def save_world_editor_config(
        project_dir: Path,
        world_name: str,
        config: WorldEditorConfig,
        platform: str = "") -> None:
    """Save the per-world editor config back to its editor.json."""
    cfg_path = world_config_path(project_dir, world_name, platform)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tilesheet": {
            "path": config.tilesheet_path
        },
        "workspace_position": {
            "x": config.workspace_x,
            "y": config.workspace_y,
            "z": config.workspace_z,
        }
    }
    cfg_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')
