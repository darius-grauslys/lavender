"""
Tests for the tilesheet file browser utility.

Tests use temporary directories and mock the native file dialog
to avoid GUI interaction.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import zlib
from pathlib import Path
from unittest.mock import patch

from core.tilesheet_browser import (
    _make_project_relative,
    _validate_png_path,
    browse_and_set_tilesheet,
    clear_tilesheet,
    load_tilesheet_for_world,
)
from core.editor_project_config import (
    WorldEditorConfig,
    load_world_editor_config,
    save_world_editor_config,
)
from ui.message_hud import MessageHUD, MessageLevel


def _create_fake_png(path: Path, width: int = 16, height: int = 16) -> None:
    """Create a minimal valid PNG file at *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        img.save(str(path))
        return
    except ImportError:
        pass

    # Fallback: hand-craft a 1x1 RGBA PNG
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return (struct.pack(">I", len(data))
                + c + struct.pack(">I", crc))

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    raw_row = b"\x00\xff\xff\xff\xff"
    compressed = zlib.compress(raw_row)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    path.write_bytes(signature + ihdr + idat + iend)


# ── _validate_png_path ────────────────────────────────────────

class TestValidatePngPath:
    def test_valid_png(self, tmp_path):
        p = tmp_path / "sheet.png"
        _create_fake_png(p)
        assert _validate_png_path(p) is True

    def test_nonexistent(self):
        assert _validate_png_path(Path("/no/such/file.png")) is False

    def test_wrong_extension(self, tmp_path):
        p = tmp_path / "sheet.jpg"
        p.write_bytes(b"not a png")
        assert _validate_png_path(p) is False

    def test_directory_not_file(self, tmp_path):
        p = tmp_path / "sheet.png"
        p.mkdir()
        assert _validate_png_path(p) is False


# ── _make_project_relative ────────────────────────────────────

class TestMakeProjectRelative:
    def test_simple_relative(self):
        project = Path("/home/user/project")
        absolute = "/home/user/project/assets/world/sheet.png"
        rel = _make_project_relative(absolute, project)
        assert rel is not None
        assert Path(rel) == Path("assets/world/sheet.png")

    def test_parent_traversal(self):
        project = Path("/home/user/project")
        absolute = "/home/user/other/sheet.png"
        rel = _make_project_relative(absolute, project)
        assert rel is not None
        assert ".." in rel


# ── browse_and_set_tilesheet ──────────────────────────────────

class TestBrowseAndSetTilesheet:
    def test_user_cancels(self, tmp_path):
        hud = MessageHUD()
        with patch(
            "core.tilesheet_browser._open_png_file_dialog",
            return_value=None,
        ):
            rel, ts = browse_and_set_tilesheet(
                tmp_path, "test_world", hud)
            assert rel is None
            assert ts is None

    def test_no_world_selected(self, tmp_path):
        hud = MessageHUD()
        rel, ts = browse_and_set_tilesheet(tmp_path, "", hud)
        assert rel is None
        assert ts is None
        assert any(
            "no world selected" in m.text.lower()
            for m in hud._messages)

    def test_invalid_file_selected(self, tmp_path):
        hud = MessageHUD()
        bad_file = tmp_path / "not_a_png.txt"
        bad_file.write_text("hello")
        with patch(
            "core.tilesheet_browser._open_png_file_dialog",
            return_value=str(bad_file),
        ):
            rel, ts = browse_and_set_tilesheet(
                tmp_path, "test_world", hud)
            assert rel is None
            assert ts is None
            assert any(
                m.level == MessageLevel.ERROR
                for m in hud._messages)

    def test_valid_file_selected(self, tmp_path):
        hud = MessageHUD()
        png_path = tmp_path / "assets" / "world" / "sheet.png"
        _create_fake_png(png_path)

        with patch(
            "core.tilesheet_browser._open_png_file_dialog",
            return_value=str(png_path),
        ):
            rel, ts = browse_and_set_tilesheet(
                tmp_path, "test_world", hud)

        assert rel is not None
        assert "sheet.png" in rel

        # Verify config was saved
        cfg = load_world_editor_config(tmp_path, "test_world")
        assert cfg.tilesheet_path == rel

    def test_valid_file_saves_forward_slashes(self, tmp_path):
        """Relative path should use forward slashes."""
        hud = MessageHUD()
        png_path = tmp_path / "assets" / "deep" / "dir" / "s.png"
        _create_fake_png(png_path)

        with patch(
            "core.tilesheet_browser._open_png_file_dialog",
            return_value=str(png_path),
        ):
            rel, _ = browse_and_set_tilesheet(
                tmp_path, "test_world", hud)

        assert rel is not None
        assert "\\" not in rel


# ── clear_tilesheet ───────────────────────────────────────────

class TestClearTilesheet:
    def test_clear(self, tmp_path):
        hud = MessageHUD()
        cfg = WorldEditorConfig(tilesheet_path="assets/sheet.png")
        save_world_editor_config(tmp_path, "test_world", cfg)

        clear_tilesheet(tmp_path, "test_world", hud)

        cfg = load_world_editor_config(tmp_path, "test_world")
        assert cfg.tilesheet_path == ""

    def test_clear_no_world(self, tmp_path):
        hud = MessageHUD()
        clear_tilesheet(tmp_path, "", hud)
        assert any(
            "no world selected" in m.text.lower()
            for m in hud._messages)


# ── load_tilesheet_for_world ──────────────────────────────────

class TestLoadTilesheetForWorld:
    def test_no_tilesheet_configured(self, tmp_path):
        hud = MessageHUD()
        path, ts = load_tilesheet_for_world(
            tmp_path, "test_world", hud)
        assert path == ""
        assert ts is None

    def test_configured_but_missing_file(self, tmp_path):
        hud = MessageHUD()
        cfg = WorldEditorConfig(
            tilesheet_path="assets/missing.png")
        save_world_editor_config(tmp_path, "test_world", cfg)

        path, ts = load_tilesheet_for_world(
            tmp_path, "test_world", hud)
        assert path == "assets/missing.png"
        assert ts is None
        assert any(
            "not found" in m.text.lower()
            for m in hud._messages)

    def test_configured_and_present(self, tmp_path):
        hud = MessageHUD()
        png_path = tmp_path / "assets" / "sheet.png"
        _create_fake_png(png_path)

        cfg = WorldEditorConfig(
            tilesheet_path="assets/sheet.png")
        save_world_editor_config(tmp_path, "test_world", cfg)

        path, ts = load_tilesheet_for_world(
            tmp_path, "test_world", hud)
        assert path == "assets/sheet.png"
        # ts may be None if neither Pillow nor pypng installed,
        # but path should always be correct
