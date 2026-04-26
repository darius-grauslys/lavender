"""Tests for editor project configuration loading and saving."""

import json
import pytest
from pathlib import Path

from core.editor_project_config import (
    EditorProjectConfig,
    WorldEditorConfig,
    load_editor_project_config,
    save_editor_project_config,
    load_world_editor_config,
    save_world_editor_config,
    world_config_path,
    EDITOR_CONFIG_RELATIVE_PATH,
    WORLD_CONFIG_FILENAME,
)


class TestEditorProjectConfig:
    def test_default_version(self):
        config = EditorProjectConfig()
        assert config.version == 1

    def test_no_tilesheet_attributes(self):
        """Project-level config no longer holds tilesheet state.
        tilesheet_path and resolve_tilesheet were removed; tilesheets
        are managed per-world via WorldEditorConfig."""
        config = EditorProjectConfig()
        assert not hasattr(config, 'tilesheet_path')
        assert not hasattr(config, 'resolve_tilesheet')


class TestWorldEditorConfig:
    def test_tilesheets_default_empty(self):
        config = WorldEditorConfig()
        assert config.tilesheets == []

    def test_tilesheets_stores_list(self):
        config = WorldEditorConfig(
            tilesheets=["first.png", "second.png"])
        assert config.tilesheets == ["first.png", "second.png"]

    def test_no_primary_tilesheet_path(self):
        """primary_tilesheet_path was removed."""
        config = WorldEditorConfig()
        assert not hasattr(config, 'primary_tilesheet_path')

    def test_no_resolve_tilesheet(self):
        """resolve_tilesheet was removed."""
        config = WorldEditorConfig()
        assert not hasattr(config, 'resolve_tilesheet')


class TestLoadEditorProjectConfig:
    def test_generates_default_when_missing(self, tmp_path):
        config = load_editor_project_config(tmp_path)
        assert config.version == 1
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["version"] == 1

    def test_loads_existing_config(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"version": 2}))
        config = load_editor_project_config(tmp_path)
        assert config.version == 2

    def test_handles_malformed_json(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text("{bad json")
        config = load_editor_project_config(tmp_path)
        assert config.version == 1

    def test_handles_missing_version_key(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"other": "data"}))
        config = load_editor_project_config(tmp_path)
        assert config.version == 1


class TestSaveEditorProjectConfig:
    def test_save_creates_file(self, tmp_path):
        config = EditorProjectConfig(version=1)
        save_editor_project_config(tmp_path, config)
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["version"] == 1

    def test_save_overwrites_existing(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"version": 1}))
        config = EditorProjectConfig(version=2)
        save_editor_project_config(tmp_path, config)
        data = json.loads(config_path.read_text())
        assert data["version"] == 2

    def test_roundtrip(self, tmp_path):
        original = EditorProjectConfig(version=3)
        save_editor_project_config(tmp_path, original)
        loaded = load_editor_project_config(tmp_path)
        assert loaded.version == original.version


class TestWorldConfigPath:
    def test_world_config_path(self, tmp_path):
        path = world_config_path(tmp_path, "my_world", platform="sdl")
        assert path == (tmp_path / "build" / "sdl" / "saves"
                        / "my_world" / WORLD_CONFIG_FILENAME)


class TestLoadWorldEditorConfig:
    def test_generates_default_when_missing(self, tmp_path):
        # Ensure the world dir exists
        (tmp_path / "build" / "sdl" / "saves" / "test_world").mkdir(parents=True)
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert config.tilesheets == []
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == []
        assert "tilesheet" not in data

    def test_loads_existing_config_with_tilesheets(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheets": ["my/sheet.png"]
        }))
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert config.tilesheets == ["my/sheet.png"]

    def test_migrates_legacy_tilesheet_field(self, tmp_path):
        """Legacy 'tilesheet.path' is migrated into tilesheets list."""
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"}
        }))
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert "my/sheet.png" in config.tilesheets

    def test_legacy_tilesheet_not_duplicated(self, tmp_path):
        """Legacy path already in tilesheets list is not duplicated."""
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"},
            "tilesheets": ["my/sheet.png"]
        }))
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert config.tilesheets.count("my/sheet.png") == 1

    def test_handles_malformed_json(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text("{bad json")
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert config.tilesheets == []

    def test_handles_missing_tilesheet_key(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({"other": "data"}))
        config = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert config.tilesheets == []

    def test_creates_world_dir_if_missing(self, tmp_path):
        config = load_world_editor_config(tmp_path, "new_world", platform="sdl")
        assert config.tilesheets == []
        assert (tmp_path / "build" / "sdl" / "saves"
                / "new_world" / WORLD_CONFIG_FILENAME).exists()


class TestSaveWorldEditorConfig:
    def test_save_creates_file(self, tmp_path):
        config = WorldEditorConfig(tilesheets=["test.png"])
        save_world_editor_config(tmp_path, "test_world", config, platform="sdl")
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == ["test.png"]
        assert "tilesheet" not in data

    def test_save_overwrites_existing(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheets": ["old.png"]
        }))
        config = WorldEditorConfig(tilesheets=["new.png"])
        save_world_editor_config(tmp_path, "test_world", config, platform="sdl")
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == ["new.png"]

    def test_roundtrip(self, tmp_path):
        original = WorldEditorConfig(
            tilesheets=["assets/world/tiles.png", "extra.png"])
        save_world_editor_config(tmp_path, "test_world", original, platform="sdl")
        loaded = load_world_editor_config(tmp_path, "test_world", platform="sdl")
        assert loaded.tilesheets == original.tilesheets

    def test_save_does_not_write_legacy_tilesheet_key(self, tmp_path):
        """Saved JSON must not contain the legacy 'tilesheet' key."""
        config = WorldEditorConfig(tilesheets=["sheet.png"])
        save_world_editor_config(tmp_path, "test_world", config, platform="sdl")
        cfg_path = world_config_path(tmp_path, "test_world", platform="sdl")
        data = json.loads(cfg_path.read_text())
        assert "tilesheet" not in data
