"""Tests for the C enum parser."""

import pytest
from pathlib import Path

from core.c_enum import (
    CEnum, CEnumMember, parse_c_enum, find_enum_by_name,
    parse_c_enum_from_file,
)

import sys
from pathlib import Path

# Allow running tests from the editor_map directory or the repo root
_editor_map_dir = Path(__file__).resolve().parents[2]
_repo_root = _editor_map_dir.parents[2]
for _p in (_repo_root, _editor_map_dir):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from core.c_enum import (  # noqa: E402
    CEnum, CEnumMember, parse_c_enum, find_enum_by_name,
    parse_c_enum_from_file,
)

# ---- Fixtures: real engine headers ----

ENGINE_TILE_KIND = """\
#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Kind__None,

    // GEN-NO-LOGIC-BEGIN
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
"""

TEMPLATE_TILE_KIND = """\
#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    Tile_Kind__Teleport_Tile,
    Tile_Kind__Heal_Tile,
    Tile_Kind__Power_Up_Tile,
    Tile_Kind__Lava,
    Tile_Kind__Water,
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Kind__Water,

    // GEN-NO-LOGIC-BEGIN
    Tile_Kind__Grass,
    Tile_Kind__Stone,
    Tile_Kind__Wood,
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
"""

TEMPLATE_TILE_COVER_KIND = """\
#ifndef IMPL_TILE_COVER_KIND_H
#define IMPL_TILE_COVER_KIND_H

#define DEFINE_TILE_COVER_KIND

typedef enum Tile_Cover_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    Tile_Cover_Kind__Door__Horizontal,
    Tile_Cover_Kind__Door__Vertical,
    Tile_Cover_Kind__Door__Horizontal__Open,
    Tile_Cover_Kind__Door__Vertical__Open,
    Tile_Cover_Kind__Wall__Corner__North_West,
    Tile_Cover_Kind__Wall__Corner__North,
    Tile_Cover_Kind__Wall__Corner__North_East,
    Tile_Cover_Kind__Wall__Corner__East,
    Tile_Cover_Kind__Wall__Corner__South_East,
    Tile_Cover_Kind__Wall__Corner__South,
    Tile_Cover_Kind__Wall__Corner__South_West,
    Tile_Cover_Kind__Wall__Corner__West,
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Cover_Kind__Wall__Corner__West,

    // GEN-NO-LOGIC-BEGIN
    Tile_Cover_Kind__Plant__Grass,
    Tile_Cover_Kind__Flower__Red,
    Tile_Cover_Kind__Flower__Blue,
    Tile_Cover_Kind__Flower__Yellow,
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Cover_Kind;

#endif
"""

TEMPLATE_TILE_LAYER = """\
#ifndef IMPL_TILE_LAYER_H
#define IMPL_TILE_LAYER_H

#define DEFINE_TILE_LAYER

typedef enum Tile_Layer {
    // GEN-BEGIN
    Tile_Layer__Ground,
    Tile_Layer__Cover,
    // GEN-END
    Tile_Layer__Default = Tile_Layer__Ground,
    Tile_Layer__Unknown
} Tile_Layer;

#endif
"""


class TestParseEngineDefaultTileKind:
    def test_parses_enum_name(self):
        enums = parse_c_enum(ENGINE_TILE_KIND)
        assert len(enums) == 1
        assert enums[0].name == 'Tile_Kind'

    def test_has_none_and_unknown(self):
        enums = parse_c_enum(ENGINE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__None') == 0
        assert 'Tile_Kind__Unknown' in e.member_map

    def test_alias_logical_equals_none(self):
        enums = parse_c_enum(ENGINE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__Logical') == 0


class TestParseTemplateTileKind:
    def test_sequential_values(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__None') == 0
        assert e.get_value('Tile_Kind__Teleport_Tile') == 1
        assert e.get_value('Tile_Kind__Heal_Tile') == 2
        assert e.get_value('Tile_Kind__Power_Up_Tile') == 3
        assert e.get_value('Tile_Kind__Lava') == 4
        assert e.get_value('Tile_Kind__Water') == 5

    def test_alias_logical(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__Logical') == \
            e.get_value('Tile_Kind__Water')

    def test_no_logic_members(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__Grass') == 6
        assert e.get_value('Tile_Kind__Stone') == 7
        assert e.get_value('Tile_Kind__Wood') == 8

    def test_unknown_is_last(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        e = enums[0]
        assert e.get_value('Tile_Kind__Unknown') == 9

    def test_gen_regions(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        e = enums[0]
        logic_members = e.get_members_in_region('GEN-LOGIC-BEGIN')
        names = [m.name for m in logic_members]
        assert 'Tile_Kind__Teleport_Tile' in names
        assert 'Tile_Kind__Water' in names


class TestParseTileCoverKind:
    """Test that enum member names don't need to match typedef name."""

    def test_enum_name_is_tile_cover_kind(self):
        enums = parse_c_enum(TEMPLATE_TILE_COVER_KIND)
        e = find_enum_by_name(enums, 'Tile_Cover_Kind')
        assert e is not None

    def test_mixed_prefixes(self):
        enums = parse_c_enum(TEMPLATE_TILE_COVER_KIND)
        e = find_enum_by_name(enums, 'Tile_Cover_Kind')
        # Members with Tile_Kind__ prefix
        assert e.get_value('Tile_Kind__None') == 0
        # Members with Tile_Cover_Kind__ prefix
        assert e.get_value('Tile_Cover_Kind__Door__Horizontal') == 1

    def test_alias_across_prefixes(self):
        enums = parse_c_enum(TEMPLATE_TILE_COVER_KIND)
        e = find_enum_by_name(enums, 'Tile_Cover_Kind')
        assert e.get_value('Tile_Kind__Logical') == \
            e.get_value('Tile_Cover_Kind__Wall__Corner__West')


class TestParseTileLayer:
    def test_gen_begin_members(self):
        enums = parse_c_enum(TEMPLATE_TILE_LAYER)
        e = find_enum_by_name(enums, 'Tile_Layer')
        assert e is not None
        assert e.get_value('Tile_Layer__Ground') == 0
        assert e.get_value('Tile_Layer__Cover') == 1

    def test_alias_default(self):
        enums = parse_c_enum(TEMPLATE_TILE_LAYER)
        e = find_enum_by_name(enums, 'Tile_Layer')
        assert e.get_value('Tile_Layer__Default') == \
            e.get_value('Tile_Layer__Ground')


class TestFindEnumByName:
    def test_found(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        assert find_enum_by_name(enums, 'Tile_Kind') is not None

    def test_not_found(self):
        enums = parse_c_enum(TEMPLATE_TILE_KIND)
        assert find_enum_by_name(enums, 'Nonexistent') is None


class TestEdgeCases:
    def test_empty_source(self):
        assert parse_c_enum('') == []

    def test_no_enums(self):
        assert parse_c_enum('#define FOO 42\nint x;') == []

    def test_multiline_comments_stripped(self):
        source = """\
typedef enum Foo {
    /* this is a
       multi-line comment */
    A,
    B
} Foo;
"""
        enums = parse_c_enum(source)
        e = enums[0]
        assert e.get_value('A') == 0
        assert e.get_value('B') == 1
