"""Tests for TileDrawTool click-and-drag painting."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_editor_map_dir = str(Path(__file__).resolve().parent.parent.parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from core.engine_config import EngineConfig
from workspace.objects import WorkspaceObjects
from modes.chunk_edit import TileDrawTool


@pytest.fixture
def config():
    return EngineConfig(constants={
        'CHUNK__WIDTH': 8,
        'CHUNK__HEIGHT': 8,
        'CHUNK__DEPTH': 1,
        'CHUNK__QUANTITY_OF__TILES': 64,
    })


@pytest.fixture
def objects(config):
    return WorkspaceObjects(config)


@pytest.fixture
def tool(objects):
    t = TileDrawTool(objects=objects, tile_byte_size=1)
    t._chunk_w = 8
    t._chunk_h = 8
    t._selected_tile_value = 7
    return t


class TestTileDrawDrag:
    def test_single_click_places_tile(self, tool, objects):
        tool.on_workspace_click(3.5, 4.5, 0)
        data = objects.get_tile_bytes(0, 0, 0, 3, 4, 0, 1)
        assert data is not None
        assert data[0] == 7

    def test_drag_begin_places_tile(self, tool, objects):
        tool.on_workspace_drag_begin(2.0, 2.0, 0)
        data = objects.get_tile_bytes(0, 0, 0, 2, 2, 0, 1)
        assert data is not None
        assert data[0] == 7
        assert tool._is_dragging is True

    def test_drag_update_places_tiles(self, tool, objects):
        tool.on_workspace_drag_begin(0.0, 0.0, 0)
        tool.on_workspace_drag_update(1.0, 0.0, 0)
        tool.on_workspace_drag_update(2.0, 0.0, 0)

        for tx in range(3):
            data = objects.get_tile_bytes(0, 0, 0, tx, 0, 0, 1)
            assert data[0] == 7, f"Tile ({tx},0) not painted"

    def test_drag_end_places_final_tile(self, tool, objects):
        tool.on_workspace_drag_begin(0.0, 0.0, 0)
        tool.on_workspace_drag_end(5.0, 5.0, 0)
        data = objects.get_tile_bytes(0, 0, 0, 5, 5, 0, 1)
        assert data[0] == 7
        assert tool._is_dragging is False

    def test_drag_end_without_begin_is_noop(self, tool, objects):
        """Calling drag_end without drag_begin should not crash."""
        tool.on_workspace_drag_end(3.0, 3.0, 0)
        assert tool._is_dragging is False
