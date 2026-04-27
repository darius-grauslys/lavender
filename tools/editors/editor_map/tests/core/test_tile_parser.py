"""Tests for the tile header parser."""

import pytest

from core.tile_parser import (
    TileInfo, TileLayerField, TileLayerLayout, TileParseError,
    parse_tile_header,
)

TEMPLATE_TILE_H = """\
#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"

// GEN-INCLUDE-BEGIN
#include "types/implemented/world/tile_cover_kind.h"
// GEN-INCLUDE-END

#define DEFINE_TILE

typedef struct Tile_t {
    union {
        struct {
            // GEN-RENDER-BEGIN
            Tile_Kind the_kind_of__tile : 10;
            Tile_Cover_Kind tile_kind_of__tile__cover : 10;
            // GEN-RENDER-END
        };
        struct {
            // GEN-LAYER-BEGIN
            u8 tile_layer_0__field__logic : 4;
            u8 tile_layer_0__field__animation : 4;

            u8 tile_layer_0__remainder : 2;
            u8 tile_layer_1__field__animation : 4;
            u8 tile_layer_1__remainder : 2;

            u8 tile_layer_1__field__logic : 6;
            u8 : 2;
            // GEN-LAYER-END
        };
        // NOTE: 3 is determinstically automatically generated via scripting.
        u8 array_of__tile_data__u8[3];
    };
    // GEN-END
} Tile;

#endif
"""

MINIMAL_TILE_H = """\
#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#define DEFINE_TILE

typedef struct Tile_t {
    Tile_Kind the_kind_of__tile;
} Tile;

#endif
"""

SINGLE_LAYER_TILE_H = """\
#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#define DEFINE_TILE

typedef struct Tile_t {
    union {
        struct {
            // GEN-RENDER-BEGIN
            Tile_Kind the_kind_of__tile : 8;
            // GEN-RENDER-END
        };
        u8 array_of__tile_data__u8[1];
    };
} Tile;

#endif
"""


class TestParseTemplateTile:
    def test_size_is_3(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert info is not None
        assert info.size_in_bytes == 3

    def test_two_layer_fields(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert len(info.layer_fields) == 2

    def test_first_layer_is_tile_kind(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        f = info.layer_fields[0]
        assert f.enum_type_name == 'Tile_Kind'
        assert f.bit_width == 10

    def test_second_layer_is_project_defined(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        f = info.layer_fields[1]
        assert f.enum_type_name == 'Tile_Cover_Kind'
        assert f.bit_width == 10


class TestParseSingleLayerTile:
    def test_size_is_1(self):
        info = parse_tile_header(SINGLE_LAYER_TILE_H)
        assert info is not None
        assert info.size_in_bytes == 1

    def test_one_layer_field(self):
        info = parse_tile_header(SINGLE_LAYER_TILE_H)
        assert len(info.layer_fields) == 1
        assert info.layer_fields[0].enum_type_name == 'Tile_Kind'


class TestParseMinimalTile:
    def test_no_array_returns_error(self):
        result = parse_tile_header(MINIMAL_TILE_H)
        assert isinstance(result, TileParseError)
        assert "array_of__tile_data__u8" in result.message


class TestEdgeCases:
    def test_empty_source(self):
        result = parse_tile_header('')
        assert isinstance(result, TileParseError)

    def test_no_tile_struct(self):
        result = parse_tile_header('#define FOO 1')
        assert isinstance(result, TileParseError)


class TestParseLayerLayouts:
    """Verify _extract_layer_layouts correctly parses GEN-LAYER sub-fields.

    The TEMPLATE_TILE_H fixture encodes:
      layer 0: logic=4, animation=4, remainder=2
      layer 1: logic=6, animation=4, remainder=2
    """

    def test_layout_count_matches_layer_field_count(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert len(info.layer_layouts) == len(info.layer_fields)

    def test_layer_0_logic_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[0].logic_bits == 4

    def test_layer_0_animation_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[0].animation_bits == 4

    def test_layer_0_remainder_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[0].remainder_bits == 2

    def test_layer_1_logic_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[1].logic_bits == 6

    def test_layer_1_animation_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[1].animation_bits == 4

    def test_layer_1_remainder_bits(self):
        info = parse_tile_header(TEMPLATE_TILE_H)
        assert not isinstance(info, TileParseError)
        assert info.layer_layouts[1].remainder_bits == 2

    def test_layout_returns_defaults_when_gen_layer_absent(self):
        """Without a GEN-LAYER block, layouts default to remainder=8."""
        result = parse_tile_header(SINGLE_LAYER_TILE_H)
        assert not isinstance(result, TileParseError)
        assert len(result.layer_layouts) == 1
        layout = result.layer_layouts[0]
        assert layout.logic_bits == 0
        assert layout.animation_bits == 0
        assert layout.remainder_bits == 8
