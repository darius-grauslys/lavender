"""Tests for TilesheetManager."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_editor_map_dir = str(Path(__file__).resolve().parent.parent.parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from core.tilesheet import Tilesheet
from core.tilesheet_manager import TilesheetManager, TilesheetEntry


def _make_tilesheet(w=16, h=16):
    """Create a minimal tilesheet for testing."""
    pixels = bytes(w * h * 4)
    return Tilesheet(width=w, height=h, pixels=pixels)


class TestTilesheetManagerBasic:
    def test_empty_manager(self):
        mgr = TilesheetManager()
        assert mgr.count == 0
        assert mgr.active_entry is None
        assert mgr.entries == []

    def test_add_single(self):
        mgr = TilesheetManager()
        ts = _make_tilesheet()
        entry = mgr.add("foo.png", ts, gl_texture_id=42)
        assert mgr.count == 1
        assert mgr.has("foo.png")
        assert entry.gl_texture_id == 42
        assert mgr.active_path == "foo.png"

    def test_add_auto_selects_first(self):
        mgr = TilesheetManager()
        mgr.add("a.png", _make_tilesheet())
        mgr.add("b.png", _make_tilesheet())
        assert mgr.active_path == "a.png"

    def test_remove(self):
        mgr = TilesheetManager()
        mgr.add("a.png", _make_tilesheet())
        mgr.add("b.png", _make_tilesheet())
        removed = mgr.remove("a.png")
        assert removed is not None
        assert mgr.count == 1
        assert not mgr.has("a.png")
        assert mgr.active_path == "b.png"

    def test_remove_last(self):
        mgr = TilesheetManager()
        mgr.add("a.png", _make_tilesheet())
        mgr.remove("a.png")
        assert mgr.count == 0
        assert mgr.active_path == ""

    def test_get(self):
        mgr = TilesheetManager()
        mgr.add("x.png", _make_tilesheet(), gl_texture_id=99)
        entry = mgr.get("x.png")
        assert entry is not None
        assert entry.gl_texture_id == 99

    def test_get_nonexistent(self):
        mgr = TilesheetManager()
        assert mgr.get("nope.png") is None

    def test_set_gl_texture(self):
        mgr = TilesheetManager()
        mgr.add("t.png", _make_tilesheet())
        mgr.set_gl_texture("t.png", 123)
        assert mgr.get("t.png").gl_texture_id == 123

    def test_clear(self):
        mgr = TilesheetManager()
        mgr.add("a.png", _make_tilesheet())
        mgr.add("b.png", _make_tilesheet())
        mgr.clear()
        assert mgr.count == 0
        assert mgr.active_path == ""

    def test_entries_order(self):
        mgr = TilesheetManager()
        mgr.add("c.png", _make_tilesheet())
        mgr.add("a.png", _make_tilesheet())
        mgr.add("b.png", _make_tilesheet())
        paths = [e.relative_path for e in mgr.entries]
        assert paths == ["c.png", "a.png", "b.png"]

    def test_add_duplicate_updates(self):
        mgr = TilesheetManager()
        ts1 = _make_tilesheet(8, 8)
        ts2 = _make_tilesheet(32, 32)
        mgr.add("x.png", ts1, gl_texture_id=1)
        mgr.add("x.png", ts2, gl_texture_id=2)
        assert mgr.count == 1
        entry = mgr.get("x.png")
        assert entry.tilesheet.width == 32
        assert entry.gl_texture_id == 2
