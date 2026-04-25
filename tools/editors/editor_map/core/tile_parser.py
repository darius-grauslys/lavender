"""
Parse project-local tile.h to extract:
1. sizeof(Tile) from array_of__tile_data__u8[N]
2. Tile layer enum fields from GEN-RENDER-BEGIN/END block

See examples/template-files/include/types/implemented/world/tile.h
for the reference pattern.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class TileLayerField:
    """A tile layer bitfield from the GEN-RENDER block."""
    enum_type_name: str   # e.g. "Tile_Kind", "Tile_Cover_Kind"
    field_name: str       # e.g. "the_kind_of__tile"
    bit_width: int        # e.g. 10


@dataclass
class TileInfo:
    """Parsed tile struct information."""
    size_in_bytes: int
    layer_fields: List[TileLayerField] = field(default_factory=list)


@dataclass
class TileParseError:
    """Describes why tile header parsing failed."""
    message: str


def parse_tile_header(
        source: str,
        filepath: Optional[Path] = None,
) -> TileInfo | TileParseError:
    """
    Parse a tile.h source to extract tile size and layer fields.

    Returns a TileInfo on success, or a TileParseError describing
    the problem on failure.
    """
    location = str(filepath) if filepath else "<source>"

    size = _extract_tile_size(source)
    if size is None:
        return TileParseError(
            f"Failed to parse tile size from '{location}': "
            f"could not find 'u8 array_of__tile_data__u8[N]' pattern. "
            f"Ensure the Tile struct contains a "
            f"'u8 array_of__tile_data__u8[N]' union member that "
            f"encodes sizeof(Tile)."
        )

    layer_fields = _extract_render_fields(source)
    if not layer_fields:
        return TileParseError(
            f"Failed to parse tile layer fields from '{location}': "
            f"no bitfield declarations found in GEN-RENDER-BEGIN/END "
            f"block (or fallback Tile_Kind bitfield). "
            f"Ensure tile.h contains a GEN-RENDER-BEGIN/END block "
            f"with typed bitfield declarations (e.g. "
            f"'Tile_Kind the_kind_of__tile : 10;')."
        )

    return TileInfo(
        size_in_bytes=size,
        layer_fields=layer_fields)


def parse_tile_header_from_file(
        filepath: Path,
) -> TileInfo | TileParseError:
    """Parse tile info from a file path."""
    if not filepath.exists():
        return TileParseError(
            f"Tile header not found at '{filepath}'. "
            f"The project must provide "
            f"'include/types/implemented/world/tile.h' "
            f"defining the Tile struct."
        )
    source = filepath.read_text(encoding='utf-8', errors='replace')
    return parse_tile_header(source, filepath)


def _extract_tile_size(source: str) -> Optional[int]:
    """
    Extract sizeof(Tile) from the array_of__tile_data__u8[N] pattern.
    """
    match = re.search(
        r'u8\s+array_of__tile_data__u8\s*\[\s*(\d+)\s*\]',
        source)
    if match:
        return int(match.group(1))
    return None


def _extract_render_fields(source: str) -> List[TileLayerField]:
    """
    Extract tile layer bitfields from the GEN-RENDER-BEGIN/END block.
    """
    # Find the GEN-RENDER-BEGIN ... GEN-RENDER-END block
    render_match = re.search(
        r'GEN-RENDER-BEGIN\s*\n(.*?)GEN-RENDER-END',
        source, re.DOTALL)
    if not render_match:
        # Fallback: try to find any bitfield with a known tile kind type
        return _extract_bitfields_fallback(source)

    block = render_match.group(1)
    return _parse_bitfields(block)


def _parse_bitfields(block: str) -> List[TileLayerField]:
    """Parse bitfield declarations from a code block."""
    fields: List[TileLayerField] = []
    # Match: TypeName field_name : N;
    pattern = re.compile(
        r'(\w+)\s+(\w+)\s*:\s*(\d+)\s*;')
    for match in pattern.finditer(block):
        type_name = match.group(1)
        field_name = match.group(2)
        bit_width = int(match.group(3))

        # Skip primitive types that aren't enum types
        if type_name in ('u8', 'u16', 'u32', 'u64',
                         'i8', 'i16', 'i32', 'i64',
                         'bool'):
            continue

        fields.append(TileLayerField(
            enum_type_name=type_name,
            field_name=field_name,
            bit_width=bit_width))

    return fields


def _extract_bitfields_fallback(source: str) -> List[TileLayerField]:
    """
    Fallback: if no GEN-RENDER block, try to find Tile_Kind bitfield
    in the struct body.
    """
    # Look for Tile_Kind as a bitfield
    match = re.search(
        r'(Tile_Kind)\s+(\w+)\s*:\s*(\d+)\s*;', source)
    if match:
        return [TileLayerField(
            enum_type_name=match.group(1),
            field_name=match.group(2),
            bit_width=int(match.group(3)))]
    return []
