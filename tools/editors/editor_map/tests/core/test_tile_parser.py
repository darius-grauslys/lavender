"""Tests for the tile header parser."""

import pytest

from core.tile_parser import (
    TileInfo, TileLayerField, parse_tile_header,
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
            Tile_Cover_Kind tike_kind_of__tile__cover : 10;
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
    def test_no_array_returns_none(self):
        info = parse_tile_header(MINIMAL_TILE_H)
        assert info is None


class TestEdgeCases:
    def test_empty_source(self):
        assert parse_tile_header('') is None

    def test_no_tile_struct(self):
        assert parse_tile_header('#define FOO 1') is None
