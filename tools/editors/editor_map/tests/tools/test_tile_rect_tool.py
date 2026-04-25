"""Tests for TileRectTool."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_editor_map_dir = str(Path(__file__).resolve().parent.parent.parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from core.engine_config import EngineConfig
from workspace.objects import WorkspaceObjects
from modes.chunk_edit import TileRectTool


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
    t = TileRectTool(objects=objects, tile_byte_size=1)
    t._chunk_w = 8
    t._chunk_h = 8
    t._selected_tile_values[0] = 5
    return t


class TestTileRectToolConstruction:
    def test_default_state(self):
        t = TileRectTool()
        assert t.fill is True
        assert t.edge_thickness == 1
        assert t.selected_tile_value == 0
        assert t.selected_layer == 0
        assert t.is_dragging is False
        assert t.drag_rect is None

    def test_with_objects(self, objects):
        t = TileRectTool(objects=objects, tile_byte_size=2)
        assert t._tile_byte_size == 2


class TestTileRectToolFill:
    def test_single_click_fills_one_tile(self, tool, objects):
        tool.on_workspace_click(2.5, 3.5, 0)
        data = objects.get_tile_bytes(0, 0, 0, 2, 3, 0, 1)
        assert data is not None
        assert data[0] == 5

    def test_drag_fills_rectangle(self, tool, objects):
        tool.on_workspace_drag_begin(1.0, 1.0, 0)
        tool.on_workspace_drag_update(3.0, 3.0, 0)
        tool.on_workspace_drag_end(3.0, 3.0, 0)

        # All tiles in 1,1 to 3,3 should be filled
        for tx in range(1, 4):
            for ty in range(1, 4):
                data = objects.get_tile_bytes(0, 0, 0, tx, ty, 0, 1)
                assert data is not None
                assert data[0] == 5, f"Tile ({tx},{ty}) not filled"

    def test_drag_rect_property_during_drag(self, tool):
        tool.on_workspace_drag_begin(5.0, 2.0, 0)
        tool.on_workspace_drag_update(1.0, 4.0, 0)
        assert tool.is_dragging is True
        rect = tool.drag_rect
        assert rect == (1, 2, 5, 4)

    def test_drag_rect_none_after_end(self, tool):
        tool.on_workspace_drag_begin(0.0, 0.0, 0)
        tool.on_workspace_drag_end(2.0, 2.0, 0)
        assert tool.is_dragging is False
        assert tool.drag_rect is None


class TestTileRectToolHollow:
    def test_hollow_rect_edge_1(self, tool, objects):
        tool._fill = False
        tool._edge_thickness = 1
        tool.on_workspace_drag_begin(0.0, 0.0, 0)
        tool.on_workspace_drag_end(4.0, 4.0, 0)

        # Edges should be filled
        for tx in range(5):
            data = objects.get_tile_bytes(0, 0, 0, tx, 0, 0, 1)
            assert data[0] == 5, f"Top edge ({tx},0) not filled"
            data = objects.get_tile_bytes(0, 0, 0, tx, 4, 0, 1)
            assert data[0] == 5, f"Bottom edge ({tx},4) not filled"
        for ty in range(5):
            data = objects.get_tile_bytes(0, 0, 0, 0, ty, 0, 1)
            assert data[0] == 5, f"Left edge (0,{ty}) not filled"
            data = objects.get_tile_bytes(0, 0, 0, 4, ty, 0, 1)
            assert data[0] == 5, f"Right edge (4,{ty}) not filled"

        # Interior should NOT be filled
        for tx in range(1, 4):
            for ty in range(1, 4):
                data = objects.get_tile_bytes(0, 0, 0, tx, ty, 0, 1)
                assert data[0] == 0, \
                    f"Interior ({tx},{ty}) should be empty"

    def test_hollow_rect_edge_2(self, tool, objects):
        tool._fill = False
        tool._edge_thickness = 2
        tool._selected_tile_values[0] = 3
        tool.on_workspace_drag_begin(0.0, 0.0, 0)
        tool.on_workspace_drag_end(5.0, 5.0, 0)

        # Interior (2,2)-(3,3) should be empty
        for tx in range(2, 4):
            for ty in range(2, 4):
                data = objects.get_tile_bytes(0, 0, 0, tx, ty, 0, 1)
                assert data[0] == 0, \
                    f"Interior ({tx},{ty}) should be empty"

        # Edge tiles should be filled
        data = objects.get_tile_bytes(0, 0, 0, 0, 0, 0, 1)
        assert data[0] == 3
        data = objects.get_tile_bytes(0, 0, 0, 1, 1, 0, 1)
        assert data[0] == 3


class TestTileRectToolProperties:
    def test_fill_default_true(self):
        t = TileRectTool()
        assert t.fill is True

    def test_edge_thickness_default_1(self):
        t = TileRectTool()
        assert t.edge_thickness == 1

    def test_set_tile_byte_size(self):
        t = TileRectTool()
        t.set_tile_byte_size(4)
        assert t._tile_byte_size == 4
