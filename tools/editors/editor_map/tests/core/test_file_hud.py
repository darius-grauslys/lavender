"""Tests for FileHUD."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_editor_map_dir = str(Path(__file__).resolve().parent.parent.parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from core.file_hud import FileHUD, LayerEditorWindow


class TestFileHUD:
    def test_construction(self):
        hud = FileHUD()
        assert hud.on_save is None
        assert hud.on_exit is None
        assert hud.show_exit_prompt is False

    def test_callbacks_wired(self):
        hud = FileHUD()
        save_called = []
        hud.on_save = lambda: save_called.append(True)
        hud.on_save()
        assert save_called == [True]

    def test_try_exit_no_pending(self):
        """Exit without pending .tmp should call on_exit directly."""
        hud = FileHUD()
        exit_called = []
        hud.on_exit = lambda: exit_called.append(True)

        objects = MagicMock()
        objects.pending_tmp_count = 0
        hud._try_exit(objects)
        assert exit_called == [True]
        assert hud.show_exit_prompt is False

    def test_try_exit_with_pending(self):
        """Exit with pending .tmp should show prompt."""
        hud = FileHUD()
        exit_called = []
        hud.on_exit = lambda: exit_called.append(True)

        objects = MagicMock()
        objects.pending_tmp_count = 5
        hud._try_exit(objects)
        assert exit_called == []
        assert hud.show_exit_prompt is True

    def test_try_exit_no_objects(self):
        """Exit with no objects should call on_exit directly."""
        hud = FileHUD()
        exit_called = []
        hud.on_exit = lambda: exit_called.append(True)
        hud._try_exit(None)
        assert exit_called == [True]


class TestLayerEditorWindow:
    def test_construction(self):
        w = LayerEditorWindow()
        assert w.is_open is False

    def test_open_close(self):
        w = LayerEditorWindow()
        w.open()
        assert w.is_open is True
        w.close()
        assert w.is_open is False
