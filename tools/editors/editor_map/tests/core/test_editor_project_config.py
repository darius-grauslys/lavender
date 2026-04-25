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
    def test_resolve_tilesheet_empty_tilesheets(self, tmp_path):
        config = WorldEditorConfig(tilesheets=[])
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_missing_file(self, tmp_path):
        config = WorldEditorConfig(tilesheets=["missing.png"])
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_existing_png(self, tmp_path):
        png_path = tmp_path / "sheet.png"
        png_path.write_bytes(b"\x89PNG")
        config = WorldEditorConfig(tilesheets=["sheet.png"])
        assert config.resolve_tilesheet(tmp_path) == png_path

    def test_resolve_tilesheet_non_png_extension(self, tmp_path):
        jpg_path = tmp_path / "sheet.jpg"
        jpg_path.write_bytes(b"\xff\xd8")
        config = WorldEditorConfig(tilesheets=["sheet.jpg"])
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_nested_path(self, tmp_path):
        nested = tmp_path / "assets" / "world"
        nested.mkdir(parents=True)
        png_path = nested / "tiles.png"
        png_path.write_bytes(b"\x89PNG")
        config = WorldEditorConfig(
            tilesheets=["assets/world/tiles.png"])
        assert config.resolve_tilesheet(tmp_path) == png_path

    def test_primary_tilesheet_path_empty(self):
        config = WorldEditorConfig(tilesheets=[])
        assert config.primary_tilesheet_path == ""

    def test_primary_tilesheet_path_returns_first(self):
        config = WorldEditorConfig(
            tilesheets=["first.png", "second.png"])
        assert config.primary_tilesheet_path == "first.png"

    def test_resolve_tilesheet_explicit_path(self, tmp_path):
        """resolve_tilesheet with an explicit path argument."""
        png_path = tmp_path / "other.png"
        png_path.write_bytes(b"\x89PNG")
        config = WorldEditorConfig(tilesheets=["first.png"])
        assert config.resolve_tilesheet(tmp_path, "other.png") == png_path


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
        path = world_config_path(tmp_path, "my_world")
        assert path == tmp_path / "save" / "my_world" / WORLD_CONFIG_FILENAME


class TestLoadWorldEditorConfig:
    def test_generates_default_when_missing(self, tmp_path):
        # Ensure the world dir exists
        (tmp_path / "save" / "test_world").mkdir(parents=True)
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheets == []
        assert config.primary_tilesheet_path == ""
        cfg_path = world_config_path(tmp_path, "test_world")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == []
        assert "tilesheet" not in data

    def test_loads_existing_config_with_tilesheets(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheets": ["my/sheet.png"]
        }))
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheets == ["my/sheet.png"]
        assert config.primary_tilesheet_path == "my/sheet.png"

    def test_migrates_legacy_tilesheet_field(self, tmp_path):
        """Legacy 'tilesheet.path' is migrated into tilesheets list."""
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"}
        }))
        config = load_world_editor_config(tmp_path, "test_world")
        assert "my/sheet.png" in config.tilesheets
        assert config.primary_tilesheet_path == "my/sheet.png"

    def test_legacy_tilesheet_not_duplicated(self, tmp_path):
        """Legacy path already in tilesheets list is not duplicated."""
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"},
            "tilesheets": ["my/sheet.png"]
        }))
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheets.count("my/sheet.png") == 1

    def test_handles_malformed_json(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text("{bad json")
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheets == []
        assert config.primary_tilesheet_path == ""

    def test_handles_missing_tilesheet_key(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({"other": "data"}))
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheets == []
        assert config.primary_tilesheet_path == ""

    def test_creates_world_dir_if_missing(self, tmp_path):
        config = load_world_editor_config(tmp_path, "new_world")
        assert config.tilesheets == []
        assert config.primary_tilesheet_path == ""
        assert (tmp_path / "save" / "new_world" / WORLD_CONFIG_FILENAME).exists()


class TestSaveWorldEditorConfig:
    def test_save_creates_file(self, tmp_path):
        config = WorldEditorConfig(tilesheets=["test.png"])
        save_world_editor_config(tmp_path, "test_world", config)
        cfg_path = world_config_path(tmp_path, "test_world")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == ["test.png"]
        assert "tilesheet" not in data

    def test_save_overwrites_existing(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheets": ["old.png"]
        }))
        config = WorldEditorConfig(tilesheets=["new.png"])
        save_world_editor_config(tmp_path, "test_world", config)
        data = json.loads(cfg_path.read_text())
        assert data["tilesheets"] == ["new.png"]

    def test_roundtrip(self, tmp_path):
        original = WorldEditorConfig(
            tilesheets=["assets/world/tiles.png", "extra.png"])
        save_world_editor_config(tmp_path, "test_world", original)
        loaded = load_world_editor_config(tmp_path, "test_world")
        assert loaded.tilesheets == original.tilesheets
        assert loaded.primary_tilesheet_path == "assets/world/tiles.png"

    def test_save_does_not_write_legacy_tilesheet_key(self, tmp_path):
        """Saved JSON must not contain the legacy 'tilesheet' key."""
        config = WorldEditorConfig(tilesheets=["sheet.png"])
        save_world_editor_config(tmp_path, "test_world", config)
        cfg_path = world_config_path(tmp_path, "test_world")
        data = json.loads(cfg_path.read_text())
        assert "tilesheet" not in data
