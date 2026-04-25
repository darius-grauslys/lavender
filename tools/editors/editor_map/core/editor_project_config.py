"""
Load and manage the project-local editor configuration file
at ./assets/world/editor.json.

Schema:
{
    "tilesheet": {
        "path": ""
    }
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


EDITOR_CONFIG_RELATIVE_PATH = Path("assets") / "world" / "editor.json"

DEFAULT_CONFIG = {
    "tilesheet": {
        "path": ""
    }
}


@dataclass
class EditorProjectConfig:
    """Parsed editor project configuration."""
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


def load_editor_project_config(project_dir: Path) -> EditorProjectConfig:
    """
    Load editor.json from the project directory.
    If the file does not exist, generate it with defaults.
    """
    config_path = project_dir / EDITOR_CONFIG_RELATIVE_PATH

    if not config_path.exists():
        # Generate default config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4) + "\n",
            encoding='utf-8')
        return EditorProjectConfig()

    try:
        data = json.loads(
            config_path.read_text(encoding='utf-8', errors='replace'))
    except (json.JSONDecodeError, OSError):
        return EditorProjectConfig()

    tilesheet_path = ""
    tilesheet = data.get("tilesheet", {})
    if isinstance(tilesheet, dict):
        tilesheet_path = tilesheet.get("path", "")

    return EditorProjectConfig(tilesheet_path=tilesheet_path)


def save_editor_project_config(
        project_dir: Path,
        config: EditorProjectConfig) -> None:
    """Save the editor project config back to editor.json."""
    config_path = project_dir / EDITOR_CONFIG_RELATIVE_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tilesheet": {
            "path": config.tilesheet_path
        }
    }
    config_path.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding='utf-8')
