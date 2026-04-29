"""
Tests for tile_parser.write_tile_header and _layer_enum_to_include_path.

Verifies that write_tile_header generates output consistent with the
canonical template (examples/template-files/.../tile.h) and that the
output is round-trip parseable by parse_tile_header.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the editor_map package is importable from this test location.
_editor_map_root = (
    Path(__file__).resolve().parents[3]
    / "tools" / "editors" / "editor_map"
)
if str(_editor_map_root) not in sys.path:
    sys.path.insert(0, str(_editor_map_root))

from core.tile_parser import (
    TileLayerField,
    TileLayerLayout,
    TileParseError,
    _layer_enum_to_include_path,
    parse_tile_header,
    write_tile_header,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _two_layer_fields() -> list[TileLayerField]:
    """2-layer setup matching the canonical template (Ground + Cover)."""
    return [
        TileLayerField("Tile_Kind", "the_kind_of__tile", 10),
        TileLayerField("Tile_Cover_Kind", "tile_kind_of__tile__cover", 10),
    ]


def _two_layer_layouts() -> list[TileLayerLayout]:
    """Sub-bit field layouts matching the canonical template."""
    return [
        TileLayerLayout(logic_bits=4, animation_bits=4, remainder_bits=2),
        TileLayerLayout(logic_bits=6, animation_bits=4, remainder_bits=2),
    ]


# ---------------------------------------------------------------------------
# _layer_enum_to_include_path
# ---------------------------------------------------------------------------

class TestLayerEnumToIncludePath:
    """Unit tests for the include-path derivation helper."""

    def test_index_0_always_returns_tile_kind(self):
        result = _layer_enum_to_include_path("Tile_Kind", 0)
        assert result == "types/implemented/world/tile_kind.h"

    def test_index_0_ignores_enum_name(self):
        """First layer always maps to tile_kind.h regardless of enum name."""
        result = _layer_enum_to_include_path("Tile_Cover_Kind", 0)
        assert result == "types/implemented/world/tile_kind.h"

    def test_second_layer_lowercases_enum_name(self):
        result = _layer_enum_to_include_path("Tile_Cover_Kind", 1)
        assert result == "types/implemented/world/tile_cover_kind.h"

    def test_arbitrary_layer_index(self):
        result = _layer_enum_to_include_path("Tile_Foo_Bar_Kind", 2)
        assert result == "types/implemented/world/tile_foo_bar_kind.h"

    def test_result_ends_with_dot_h(self):
        assert _layer_enum_to_include_path("Tile_Cover_Kind", 1).endswith(".h")

    def test_result_starts_with_types_path(self):
        result = _layer_enum_to_include_path("Tile_Cover_Kind", 1)
        assert result.startswith("types/implemented/world/")


# ---------------------------------------------------------------------------
# write_tile_header — file structure
# ---------------------------------------------------------------------------

class TestWriteTileHeaderStructure:
    """Verify that write_tile_header produces the correct structural layout."""

    def test_generates_file(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert fp.exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        fp = tmp_path / "world" / "implemented" / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert fp.exists()

    def test_include_guard_is_impl_tile_h(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "#ifndef IMPL_TILE_H" in src
        assert "#define IMPL_TILE_H" in src

    def test_define_tile_is_present_and_separate_from_guard(
            self, tmp_path: Path) -> None:
        """#define DEFINE_TILE must appear after the include block."""
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        guard_pos = src.find("#define IMPL_TILE_H")
        define_pos = src.find("#define DEFINE_TILE")
        assert define_pos > guard_pos, (
            "#define DEFINE_TILE must come after #define IMPL_TILE_H")

    def test_includes_defines_weak(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert '#include "defines_weak.h"' in fp.read_text()

    def test_gen_include_markers_present(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "// GEN-INCLUDE-BEGIN" in src
        assert "// GEN-INCLUDE-END" in src

    def test_first_layer_include_is_tile_kind(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert '#include "types/implemented/world/tile_kind.h"' in fp.read_text()

    def test_second_layer_include_is_cover_kind(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert '#include "types/implemented/world/tile_cover_kind.h"' in fp.read_text()

    def test_gen_render_markers_present(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "// GEN-RENDER-BEGIN" in src
        assert "// GEN-RENDER-END" in src

    def test_gen_layer_markers_present(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "// GEN-LAYER-BEGIN" in src
        assert "// GEN-LAYER-END" in src

    def test_gen_end_marker_present(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert "// GEN-END" in fp.read_text()

    def test_array_size_two_layers_is_3_bytes(self, tmp_path: Path) -> None:
        """10 + 10 = 20 bits → requires 3 bytes."""
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        assert "u8 array_of__tile_data__u8[3]" in fp.read_text()

    def test_array_size_single_8bit_layer_is_1_byte(self, tmp_path: Path) -> None:
        fields = [TileLayerField("Tile_Kind", "the_kind_of__tile", 8)]
        layouts = [TileLayerLayout(logic_bits=4, animation_bits=4, remainder_bits=0)]
        fp = tmp_path / "tile.h"
        write_tile_header(fp, fields, layouts)
        assert "u8 array_of__tile_data__u8[1]" in fp.read_text()

    def test_structural_ordering(self, tmp_path: Path) -> None:
        """Key sections must appear in the same order as the canonical template."""
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        markers = [
            "#ifndef IMPL_TILE_H",
            '#include "defines_weak.h"',
            "// GEN-INCLUDE-BEGIN",
            "// GEN-INCLUDE-END",
            "#define DEFINE_TILE",
            "// GEN-RENDER-BEGIN",
            "// GEN-RENDER-END",
            "// GEN-LAYER-BEGIN",
            "// GEN-LAYER-END",
            "// GEN-END",
            "#endif",
        ]
        positions = [src.find(m) for m in markers]
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"'{markers[i]}' must appear before '{markers[i + 1]}'")


# ---------------------------------------------------------------------------
# write_tile_header — GEN-LAYER field naming
# ---------------------------------------------------------------------------

class TestWriteTileHeaderLayerFieldNaming:
    """Verify the logic/animation/remainder naming convention in GEN-LAYER."""

    def test_logic_fields_use_field_prefix(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "tile_layer_0__field__logic" in src
        assert "tile_layer_1__field__logic" in src

    def test_animation_fields_use_field_prefix(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "tile_layer_0__field__animation" in src
        assert "tile_layer_1__field__animation" in src

    def test_remainder_fields_omit_field_prefix(self, tmp_path: Path) -> None:
        """Remainder fields must use tile_layer_N__remainder, not __field__remainder."""
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "tile_layer_0__remainder" in src
        assert "tile_layer_1__remainder" in src
        assert "tile_layer_0__field__remainder" not in src
        assert "tile_layer_1__field__remainder" not in src

    def test_correct_bit_widths_for_all_sub_fields(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "tile_layer_0__field__logic : 4" in src
        assert "tile_layer_0__field__animation : 4" in src
        assert "tile_layer_0__remainder : 2" in src
        assert "tile_layer_1__field__logic : 6" in src
        assert "tile_layer_1__field__animation : 4" in src
        assert "tile_layer_1__remainder : 2" in src

    def test_render_field_names_preserved(self, tmp_path: Path) -> None:
        """GEN-RENDER bitfield declarations must use the field names from input."""
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        assert "the_kind_of__tile" in src
        assert "tile_kind_of__tile__cover" in src


# ---------------------------------------------------------------------------
# write_tile_header — anonymous padding
# ---------------------------------------------------------------------------

class TestWriteTileHeaderPadding:
    """Verify that anonymous u8 : N; bits are emitted when needed."""

    def test_two_layer_template_has_trailing_padding(
            self, tmp_path: Path) -> None:
        """Canonical 2-layer layout: 20 bits → 24 bits in 3 bytes → 4 pad bits total.

        Layout trace:
          byte 0: layer0 logic(4) + layer0 anim(4) = 8 bits (full)
          byte 1: layer0 remainder(2) + layer1 anim(4) + layer1 remainder(2) = 8 bits (full)
          byte 2: layer1 logic(6) + anonymous padding(2) = 8 bits (full)
        """
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        src = fp.read_text()
        start = src.find("// GEN-LAYER-BEGIN")
        end = src.find("// GEN-LAYER-END")
        layer_block = src[start:end]
        assert "u8 : 2;" in layer_block

    def test_mid_stream_padding_emitted_when_field_straddles_byte(
            self, tmp_path: Path) -> None:
        """A 5-bit logic + 5-bit anim layout straddles a byte boundary.

        Layout trace:
          byte 0: logic(5) used → anim(5) won't fit in remaining 3 bits
                  → u8 : 3; padding emitted, byte 0 complete
          byte 1: anim(5) written → 5 bits used
                  → trailing u8 : 3; padding emitted
        """
        fields = [TileLayerField("Tile_Kind", "the_kind_of__tile", 10)]
        layouts = [TileLayerLayout(logic_bits=5, animation_bits=5, remainder_bits=0)]
        fp = tmp_path / "tile.h"
        write_tile_header(fp, fields, layouts)
        src = fp.read_text()
        start = src.find("// GEN-LAYER-BEGIN")
        end = src.find("// GEN-LAYER-END")
        layer_block = src[start:end]
        assert "u8 : 3;" in layer_block

    def test_no_padding_when_bytes_exactly_filled(self, tmp_path: Path) -> None:
        """An 8-bit layer with logic=4 + anim=4 fills exactly one byte."""
        fields = [TileLayerField("Tile_Kind", "the_kind_of__tile", 8)]
        layouts = [TileLayerLayout(logic_bits=4, animation_bits=4, remainder_bits=0)]
        fp = tmp_path / "tile.h"
        write_tile_header(fp, fields, layouts)
        src = fp.read_text()
        start = src.find("// GEN-LAYER-BEGIN")
        end = src.find("// GEN-LAYER-END")
        layer_block = src[start:end]
        assert "u8 : " not in layer_block


# ---------------------------------------------------------------------------
# write_tile_header — round-trip with parse_tile_header
# ---------------------------------------------------------------------------

class TestWriteTileHeaderRoundTrip:
    """Write a tile.h then parse it back and verify the data is lossless."""

    def test_round_trip_size(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError), result.message
        assert result.size_in_bytes == 3

    def test_round_trip_layer_field_count(self, tmp_path: Path) -> None:
        fields = _two_layer_fields()
        fp = tmp_path / "tile.h"
        write_tile_header(fp, fields, _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert len(result.layer_fields) == len(fields)

    def test_round_trip_first_layer_enum_type(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_fields[0].enum_type_name == "Tile_Kind"

    def test_round_trip_first_layer_bit_width(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_fields[0].bit_width == 10

    def test_round_trip_second_layer_enum_type(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_fields[1].enum_type_name == "Tile_Cover_Kind"

    def test_round_trip_second_layer_bit_width(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_fields[1].bit_width == 10

    def test_round_trip_layer_0_logic_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[0].logic_bits == 4

    def test_round_trip_layer_0_animation_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[0].animation_bits == 4

    def test_round_trip_layer_0_remainder_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[0].remainder_bits == 2

    def test_round_trip_layer_1_logic_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[1].logic_bits == 6

    def test_round_trip_layer_1_animation_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[1].animation_bits == 4

    def test_round_trip_layer_1_remainder_bits(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile.h"
        write_tile_header(fp, _two_layer_fields(), _two_layer_layouts())
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.layer_layouts[1].remainder_bits == 2

    def test_round_trip_single_layer(self, tmp_path: Path) -> None:
        fields = [TileLayerField("Tile_Kind", "the_kind_of__tile", 8)]
        layouts = [TileLayerLayout(logic_bits=4, animation_bits=4, remainder_bits=0)]
        fp = tmp_path / "tile.h"
        write_tile_header(fp, fields, layouts)
        result = parse_tile_header(fp.read_text(), fp)
        assert not isinstance(result, TileParseError)
        assert result.size_in_bytes == 1
        assert len(result.layer_fields) == 1
        assert result.layer_fields[0].enum_type_name == "Tile_Kind"
        assert result.layer_fields[0].bit_width == 8
