"""Tests for editor project configuration loading and saving."""

import json
import pytest
from pathlib import Path

from core.editor_project_config import (
    EditorProjectConfig,
    load_editor_project_config,
    save_editor_project_config,
    EDITOR_CONFIG_RELATIVE_PATH,
)


class TestEditorProjectConfig:
    def test_resolve_tilesheet_empty_path(self, tmp_path):
        config = EditorProjectConfig(tilesheet_path="")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_missing_file(self, tmp_path):
        config = EditorProjectConfig(tilesheet_path="missing.png")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_existing_png(self, tmp_path):
        png_path = tmp_path / "sheet.png"
        png_path.write_bytes(b"\x89PNG")
        config = EditorProjectConfig(tilesheet_path="sheet.png")
        assert config.resolve_tilesheet(tmp_path) == png_path

    def test_resolve_tilesheet_non_png_extension(self, tmp_path):
        jpg_path = tmp_path / "sheet.jpg"
        jpg_path.write_bytes(b"\xff\xd8")
        config = EditorProjectConfig(tilesheet_path="sheet.jpg")
        assert config.resolve_tilesheet(tmp_path) is None

    def test_resolve_tilesheet_nested_path(self, tmp_path):
        nested = tmp_path / "assets" / "world"
        nested.mkdir(parents=True)
        png_path = nested / "tiles.png"
        png_path.write_bytes(b"\x89PNG")
        config = EditorProjectConfig(
            tilesheet_path="assets/world/tiles.png")
        assert config.resolve_tilesheet(tmp_path) == png_path


class TestLoadEditorProjectConfig:
    def test_generates_default_when_missing(self, tmp_path):
        config = load_editor_project_config(tmp_path)
        assert config.tilesheet_path == ""
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["tilesheet"]["path"] == ""

    def test_loads_existing_config(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({
            "tilesheet": {"path": "my/sheet.png"}
        }))
        config = load_editor_project_config(tmp_path)
        assert config.tilesheet_path == "my/sheet.png"

    def test_handles_malformed_json(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text("{bad json")
        config = load_editor_project_config(tmp_path)
        assert config.tilesheet_path == ""

    def test_handles_missing_tilesheet_key(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"other": "data"}))
        config = load_editor_project_config(tmp_path)
        assert config.tilesheet_path == ""


class TestSaveEditorProjectConfig:
    def test_save_creates_file(self, tmp_path):
        config = EditorProjectConfig(tilesheet_path="test.png")
        save_editor_project_config(tmp_path, config)
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["tilesheet"]["path"] == "test.png"

    def test_save_overwrites_existing(self, tmp_path):
        config_path = tmp_path / EDITOR_CONFIG_RELATIVE_PATH
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({
            "tilesheet": {"path": "old.png"}
        }))
        config = EditorProjectConfig(tilesheet_path="new.png")
        save_editor_project_config(tmp_path, config)
        data = json.loads(config_path.read_text())
        assert data["tilesheet"]["path"] == "new.png"

    def test_roundtrip(self, tmp_path):
        original = EditorProjectConfig(
            tilesheet_path="assets/world/tiles.png")
        save_editor_project_config(tmp_path, original)
        loaded = load_editor_project_config(tmp_path)
        assert loaded.tilesheet_path == original.tilesheet_path
