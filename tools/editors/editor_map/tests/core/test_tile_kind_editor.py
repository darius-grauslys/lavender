"""Tests for the Tile Kind Editor data model."""

import pytest
from pathlib import Path

from core.c_enum import CEnum, CEnumMember
from core.tile_kind_editor import (
    TileKindEditorState,
    TileKindEntry,
    LogicalTileEntry,
    AnimationTileEntry,
    create_editor_state_from_enum,
    write_tile_kind_header,
    get_tilesheet_map_from_state,
    save_tilesheet_mapping,
    load_tilesheet_mapping,
)


def _make_test_enum():
    """Create a test CEnum resembling Tile_Kind."""
    members = [
        CEnumMember(name="Tile_Kind__None", value=0),
        CEnumMember(name="Tile_Kind__Grass", value=1,
                    gen_region="GEN-LOGIC-BEGIN"),
        CEnumMember(name="Tile_Kind__Water", value=2,
                    gen_region="GEN-LOGIC-BEGIN"),
        CEnumMember(name="Tile_Kind__Stone", value=3),
        CEnumMember(name="Tile_Kind__Unknown", value=4),
    ]
    return CEnum(
        name="Tile_Kind",
        members=members,
        member_map={m.name: m.value for m in members})


class TestTileKindEditorState:
    def test_max_tile_kinds_8bit(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        assert state.max_tile_kinds == 255

    def test_max_tile_kinds_10bit(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=10, logic_bits=0, animation_bits=0)
        assert state.max_tile_kinds == 1023

    def test_max_logical_tiles_zero_bits(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        assert state.max_logical_tiles == 0
        assert not state.can_add_logical_tile

    def test_max_logical_tiles_4bits(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=10, logic_bits=4, animation_bits=0)
        assert state.max_logical_tiles == 16

    def test_max_animation_tiles_zero_bits(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        assert state.max_animation_tiles == 0
        assert not state.can_add_animation_tile

    def test_add_tile_kind(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        state.add_tile_kind("Tile_Kind__Grass")
        assert len(state.tile_kinds) == 1
        assert state.tile_kinds[0].name == "Tile_Kind__Grass"
        assert state.tile_kinds[0].value == 0
        assert state.tile_kinds[0].tilesheet_tile_index == -1

    def test_add_tile_kind_with_tilesheet_index(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        state.add_tile_kind("Tile_Kind__Grass", tilesheet_tile_index=5)
        assert state.tile_kinds[0].tilesheet_tile_index == 5

    def test_add_tile_kind_increments_value(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=0)
        state.add_tile_kind("A")
        state.add_tile_kind("B")
        assert state.tile_kinds[1].value == 1

    def test_add_tile_kind_disabled_at_max(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=2, logic_bits=0, animation_bits=0)
        for i in range(3):
            state.add_tile_kind(f"T{i}")
        assert not state.can_add_tile_kind
        state.add_tile_kind("overflow")
        assert len(state.tile_kinds) == 3

    def test_remove_tile_kind(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=4, animation_bits=0)
        state.add_tile_kind("A")
        state.add_tile_kind("B")
        state.add_logical_tile("A")
        state.remove_tile_kind(0)
        assert len(state.tile_kinds) == 1
        assert state.tile_kinds[0].name == "B"
        assert len(state.logical_tiles) == 0

    def test_add_logical_tile(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=4, animation_bits=0)
        state.add_tile_kind("A")
        state.add_logical_tile("A")
        assert len(state.logical_tiles) == 1
        assert state.logical_tiles[0].tile_kind_name == "A"

    def test_add_animation_tile(self):
        state = TileKindEditorState(
            layer_name="test", enum_type_name="Tile_Kind",
            render_bit_width=8, logic_bits=0, animation_bits=4)
        state.add_tile_kind("A")
        state.add_animation_tile("A")
        assert len(state.animation_tiles) == 1


class TestCreateEditorStateFromEnum:
    def test_creates_state_from_enum(self):
        enum = _make_test_enum()
        state = create_editor_state_from_enum(
            enum, "the_kind_of__tile", 10, 4, 4)
        assert state.layer_name == "the_kind_of__tile"
        assert state.enum_type_name == "Tile_Kind"
        assert state.render_bit_width == 10

    def test_skips_none_and_unknown(self):
        enum = _make_test_enum()
        state = create_editor_state_from_enum(
            enum, "test", 10, 0, 0)
        names = [tk.name for tk in state.tile_kinds]
        assert "Tile_Kind__None" not in names
        assert "Tile_Kind__Unknown" not in names

    def test_populates_logical_tiles(self):
        enum = _make_test_enum()
        state = create_editor_state_from_enum(
            enum, "test", 10, 4, 0)
        logical_names = [lt.tile_kind_name for lt in state.logical_tiles]
        assert "Tile_Kind__Grass" in logical_names
        assert "Tile_Kind__Water" in logical_names


class TestWriteTileKindHeader:
    def test_writes_valid_header(self, tmp_path):
        state = TileKindEditorState(
            layer_name="the_kind_of__tile",
            enum_type_name="Tile_Kind",
            render_bit_width=10,
            logic_bits=4,
            animation_bits=4,
            tile_kinds=[
                TileKindEntry(name="Tile_Kind__Grass", value=1),
                TileKindEntry(name="Tile_Kind__Water", value=2),
                TileKindEntry(name="Tile_Kind__Stone", value=3),
            ],
            logical_tiles=[
                LogicalTileEntry(tile_kind_name="Tile_Kind__Grass"),
                LogicalTileEntry(tile_kind_name="Tile_Kind__Water"),
            ],
        )
        filepath = tmp_path / "tile_kind.h"
        write_tile_kind_header(filepath, state, "DEFINE_TILE_KIND")

        content = filepath.read_text()
        assert "#ifndef TILE_KIND_H" in content
        assert "#define DEFINE_TILE_KIND" in content
        assert "Tile_Kind__None = 0," in content
        assert "// GEN-LOGIC-BEGIN" in content
        assert "Tile_Kind__Grass," in content
        assert "Tile_Kind__Water," in content
        assert "// GEN-LOGIC-END" in content
        assert "// GEN-NO-LOGIC-BEGIN" in content
        assert "Tile_Kind__Stone," in content
        assert "// GEN-NO-LOGIC-END" in content
        assert "Tile_Kind__Unknown" in content

    def test_writes_empty_logical_section(self, tmp_path):
        state = TileKindEditorState(
            layer_name="test",
            enum_type_name="Tile_Kind",
            render_bit_width=8,
            logic_bits=0,
            animation_bits=0,
            tile_kinds=[
                TileKindEntry(name="Tile_Kind__Grass", value=1),
            ],
        )
        filepath = tmp_path / "tile_kind.h"
        write_tile_kind_header(filepath, state, "DEFINE_TILE_KIND")

        content = filepath.read_text()
        assert "Tile_Kind__Logical = Tile_Kind__None," in content
        assert "Tile_Kind__Grass," in content


class TestTilesheetMapping:
    def test_get_tilesheet_map_from_state(self):
        state = TileKindEditorState(
            layer_name="test",
            enum_type_name="Tile_Kind",
            render_bit_width=8,
            logic_bits=0,
            animation_bits=0,
            tile_kinds=[
                TileKindEntry(name="Tile_Kind__Grass", value=1,
                              tilesheet_tile_index=5),
                TileKindEntry(name="Tile_Kind__Water", value=2,
                              tilesheet_tile_index=-1),
                TileKindEntry(name="Tile_Kind__Stone", value=3,
                              tilesheet_tile_index=12),
            ],
        )
        mapping = get_tilesheet_map_from_state(state)
        assert mapping == {
            "Tile_Kind__Grass": 5,
            "Tile_Kind__Stone": 12,
        }
        assert "Tile_Kind__Water" not in mapping

    def test_get_tilesheet_map_empty(self):
        state = TileKindEditorState(
            layer_name="test",
            enum_type_name="Tile_Kind",
            render_bit_width=8,
            logic_bits=0,
            animation_bits=0,
        )
        mapping = get_tilesheet_map_from_state(state)
        assert mapping == {}

    def test_save_and_load_tilesheet_mapping(self, tmp_path):
        filepath = tmp_path / "tile_kind.h"
        mapping = {"Tile_Kind__Grass": 5, "Tile_Kind__Stone": 12}
        save_tilesheet_mapping(filepath, mapping)

        loaded = load_tilesheet_mapping(filepath)
        assert loaded == mapping

    def test_load_tilesheet_mapping_missing_file(self, tmp_path):
        filepath = tmp_path / "tile_kind.h"
        loaded = load_tilesheet_mapping(filepath)
        assert loaded == {}

    def test_load_tilesheet_mapping_malformed_json(self, tmp_path):
        filepath = tmp_path / "tile_kind.h"
        map_path = tmp_path / "tile_kind_tilesheet.json"
        map_path.write_text("{bad json")
        loaded = load_tilesheet_mapping(filepath)
        assert loaded == {}

    def test_create_editor_state_with_tilesheet_map(self):
        enum = _make_test_enum()
        tilesheet_map = {
            "Tile_Kind__Grass": 3,
            "Tile_Kind__Water": 7,
        }
        state = create_editor_state_from_enum(
            enum, "test", 10, 4, 0,
            tilesheet_map=tilesheet_map)
        grass = next(
            tk for tk in state.tile_kinds
            if tk.name == "Tile_Kind__Grass")
        water = next(
            tk for tk in state.tile_kinds
            if tk.name == "Tile_Kind__Water")
        stone = next(
            tk for tk in state.tile_kinds
            if tk.name == "Tile_Kind__Stone")
        assert grass.tilesheet_tile_index == 3
        assert water.tilesheet_tile_index == 7
        assert stone.tilesheet_tile_index == -1
