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
    "tilesheets": ["assets/world/tilesheet.png"],
    "layers": [],
    "workspace_position": {"x": 0, "y": 0, "z": 0}
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
from typing import List, Optional


EDITOR_CONFIG_RELATIVE_PATH = Path("assets") / "world" / "editor.json"
BUILD_CONFIG_FILENAME = "editor.config"
WORLD_CONFIG_FILENAME = "editor.json"

DEFAULT_PROJECT_CONFIG = {
    "version": 1,
    "max_tmp_chunks": 1024
}

DEFAULT_WORLD_CONFIG = {
    "tilesheets": [],
    "layers": [],
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



@dataclass
class WorldEditorConfig:
    """Parsed per-world editor configuration."""
    tilesheets: list = field(default_factory=list)
    layers: list = field(default_factory=list)
    workspace_x: int = 0
    workspace_y: int = 0
    workspace_z: int = 0

    @property
    def primary_tilesheet_path(self) -> str:
        """Return the first tilesheet path, or '' if none."""
        if self.tilesheets:
            return self.tilesheets[0]
        return ""

    def resolve_tilesheet(self, project_dir: Path, path: str = "") -> Optional[Path]:
        """
        Resolve a tilesheet path relative to the project directory.
        If *path* is empty, uses the primary tilesheet.
        Returns the Path if it exists and is a .png file, else None.
        """
        ts_path = path or self.primary_tilesheet_path
        if not ts_path:
            return None
        resolved = project_dir / ts_path
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

    tilesheets_data = data.get("tilesheets", [])
    if not isinstance(tilesheets_data, list):
        tilesheets_data = []

    # Migrate legacy "tilesheet.path" into tilesheets list
    legacy_tilesheet = data.get("tilesheet", {})
    if isinstance(legacy_tilesheet, dict):
        legacy_path = legacy_tilesheet.get("path", "")
        if legacy_path and legacy_path not in tilesheets_data:
            tilesheets_data.insert(0, legacy_path)

    layers_data = data.get("layers", [])
    if not isinstance(layers_data, list):
        layers_data = []

    ws = data.get("workspace_position", {})
    return WorldEditorConfig(
        tilesheets=tilesheets_data,
        layers=layers_data,
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
        "tilesheets": config.tilesheets,
        "layers": config.layers,
        "workspace_position": {
            "x": config.workspace_x,
            "y": config.workspace_y,
            "z": config.workspace_z,
        }
    }
    cfg_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')
