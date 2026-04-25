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
    def test_resolve_tilesheet_always_none(self, tmp_path):
        """Project-level config no longer holds tilesheet; always None."""
        config = EditorProjectConfig()
        assert config.resolve_tilesheet(tmp_path) is None

    def test_default_version(self):
        config = EditorProjectConfig()
        assert config.version == 1

    def test_tilesheet_path_backward_compat(self):
        """EditorProjectConfig.tilesheet_path must exist for backward
        compatibility with code that still reads it (e.g. editor_app).
        It should always return an empty string since tilesheet config
        moved to WorldEditorConfig."""
        config = EditorProjectConfig()
        # Must not raise AttributeError
        assert config.tilesheet_path == ""


class TestWorldEditorConfig:
    def test_resolve_tilesheet_empty_path(self, tmp_path):
        config = WorldEditorConfig(tilesheet_path="")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_missing_file(self, tmp_path):
        config = WorldEditorConfig(tilesheet_path="missing.png")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_existing_png(self, tmp_path):
        png_path = tmp_path / "sheet.png"
        png_path.write_bytes(b"\x89PNG")
        config = WorldEditorConfig(tilesheet_path="sheet.png")
        assert config.resolve_tilesheet(tmp_path) == png_path

    def test_resolve_tilesheet_non_png_extension(self, tmp_path):
        jpg_path = tmp_path / "sheet.jpg"
        jpg_path.write_bytes(b"\xff\xd8")
        config = WorldEditorConfig(tilesheet_path="sheet.jpg")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_nested_path(self, tmp_path):
        nested = tmp_path / "assets" / "world"
        nested.mkdir(parents=True)
        png_path = nested / "tiles.png"
        png_path.write_bytes(b"\x89PNG")
        config = WorldEditorConfig(
            tilesheet_path="assets/world/tiles.png")
        assert config.resolve_tilesheet(tmp_path) == png_path


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
        assert config.tilesheet_path == ""
        cfg_path = world_config_path(tmp_path, "test_world")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheet"]["path"] == ""

    def test_loads_existing_config(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"}
        }))
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheet_path == "my/sheet.png"

    def test_handles_malformed_json(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text("{bad json")
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheet_path == ""

    def test_handles_missing_tilesheet_key(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({"other": "data"}))
        config = load_world_editor_config(tmp_path, "test_world")
        assert config.tilesheet_path == ""

    def test_creates_world_dir_if_missing(self, tmp_path):
        config = load_world_editor_config(tmp_path, "new_world")
        assert config.tilesheet_path == ""
        assert (tmp_path / "save" / "new_world" / WORLD_CONFIG_FILENAME).exists()


class TestSaveWorldEditorConfig:
    def test_save_creates_file(self, tmp_path):
        config = WorldEditorConfig(tilesheet_path="test.png")
        save_world_editor_config(tmp_path, "test_world", config)
        cfg_path = world_config_path(tmp_path, "test_world")
        assert cfg_path.exists()
        data = json.loads(cfg_path.read_text())
        assert data["tilesheet"]["path"] == "test.png"

    def test_save_overwrites_existing(self, tmp_path):
        cfg_path = world_config_path(tmp_path, "test_world")
        cfg_path.parent.mkdir(parents=True)
        cfg_path.write_text(json.dumps({
            "tilesheet": {"path": "old.png"}
        }))
        config = WorldEditorConfig(tilesheet_path="new.png")
        save_world_editor_config(tmp_path, "test_world", config)
        data = json.loads(cfg_path.read_text())
        assert data["tilesheet"]["path"] == "new.png"

    def test_roundtrip(self, tmp_path):
        original = WorldEditorConfig(
            tilesheet_path="assets/world/tiles.png")
        save_world_editor_config(tmp_path, "test_world", original)
        loaded = load_world_editor_config(tmp_path, "test_world")
        assert loaded.tilesheet_path == original.tilesheet_path
