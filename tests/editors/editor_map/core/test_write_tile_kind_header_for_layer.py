"""
Tests for tile_parser.write_tile_kind_header_for_layer.

Verifies that the generated _kind.h files match the project
convention used by defines_weak.h (see core/include/defines_weak.h
and examples/template-files/).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the editor_map package is importable
_editor_map_root = (
    Path(__file__).resolve().parents[3]
    / "tools" / "editors" / "editor_map"
)
if str(_editor_map_root) not in sys.path:
    sys.path.insert(0, str(_editor_map_root))

from core.tile_parser import write_tile_kind_header_for_layer
from core.c_enum import parse_c_enum


class TestWriteTileKindHeaderForLayer:
    """Tests for write_tile_kind_header_for_layer."""

    def test_generates_file(self, tmp_path: Path) -> None:
        """Generated file should exist on disk."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        assert fp.exists()

    def test_parseable_enum(self, tmp_path: Path) -> None:
        """Generated file should be parseable by parse_c_enum."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        enums = parse_c_enum(fp.read_text())
        assert len(enums) == 1
        assert enums[0].name == "Tile_Kind"

    def test_none_is_zero(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        enum = parse_c_enum(fp.read_text())[0]
        assert enum.get_value("Tile_Kind__None") == 0

    def test_logical_aliases_none_when_empty(self, tmp_path: Path) -> None:
        """__Logical should equal __None when no logic members exist."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        enum = parse_c_enum(fp.read_text())[0]
        assert enum.get_value("Tile_Kind__Logical") == \
            enum.get_value("Tile_Kind__None")

    def test_unknown_is_last(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        enum = parse_c_enum(fp.read_text())[0]
        assert enum.members[-1].name == "Tile_Kind__Unknown"

    def test_has_exactly_three_members(self, tmp_path: Path) -> None:
        """Skeleton should have __None, __Logical, __Unknown."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        enum = parse_c_enum(fp.read_text())[0]
        names = [m.name for m in enum.members]
        assert names == [
            "Tile_Kind__None",
            "Tile_Kind__Logical",
            "Tile_Kind__Unknown",
        ]

    def test_include_guard(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        src = fp.read_text()
        assert "#ifndef IMPL_TILE_KIND_H" in src
        assert "#define IMPL_TILE_KIND_H" in src
        assert "#endif" in src

    def test_define_macro(self, tmp_path: Path) -> None:
        """DEFINE_ macro must match defines_weak.h convention."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        assert "#define DEFINE_TILE_KIND" in fp.read_text()

    def test_gen_markers(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        src = fp.read_text()
        assert "// GEN-LOGIC-BEGIN" in src
        assert "// GEN-LOGIC-END" in src
        assert "// GEN-NO-LOGIC-BEGIN" in src
        assert "// GEN-NO-LOGIC-END" in src

    def test_custom_enum_name(self, tmp_path: Path) -> None:
        fp = tmp_path / "tile_cover_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Cover_Kind")
        src = fp.read_text()
        assert "#define DEFINE_TILE_COVER_KIND" in src
        assert "#ifndef IMPL_TILE_COVER_KIND_H" in src
        enum = parse_c_enum(src)[0]
        assert enum.name == "Tile_Cover_Kind"
        names = [m.name for m in enum.members]
        assert "Tile_Cover_Kind__None" in names
        assert "Tile_Cover_Kind__Logical" in names
        assert "Tile_Cover_Kind__Unknown" in names

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        fp = tmp_path / "deep" / "nested" / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        assert fp.exists()

    def test_structural_ordering(self, tmp_path: Path) -> None:
        """Sections must appear in the correct order."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(fp, "Tile_Kind")
        src = fp.read_text()

        markers = [
            "#ifndef IMPL_TILE_KIND_H",
            "#define DEFINE_TILE_KIND",
            "typedef enum Tile_Kind",
            "Tile_Kind__None",
            "GEN-LOGIC-BEGIN",
            "GEN-LOGIC-END",
            "Tile_Kind__Logical",
            "GEN-NO-LOGIC-BEGIN",
            "GEN-NO-LOGIC-END",
            "Tile_Kind__Unknown",
            "#endif",
        ]
        positions = []
        for marker in markers:
            pos = src.find(marker)
            assert pos >= 0, f"Missing marker: {marker}"
            positions.append(pos)

        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"'{markers[i]}' should appear before "
                f"'{markers[i + 1]}'")

    def test_with_logic_bits(self, tmp_path: Path) -> None:
        """logic_bits parameter should not change the skeleton structure."""
        fp = tmp_path / "tile_kind.h"
        write_tile_kind_header_for_layer(
            fp, "Tile_Kind", logic_bits=4)
        enum = parse_c_enum(fp.read_text())[0]
        names = [m.name for m in enum.members]
        assert "Tile_Kind__None" in names
        assert "Tile_Kind__Logical" in names
        assert "Tile_Kind__Unknown" in names
