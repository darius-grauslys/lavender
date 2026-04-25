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
class TileLayerLayout:
    """
    Sub-bit field layout for a single tile layer from GEN-LAYER.

    When the GEN-LAYER block is empty or absent, defaults are:
      logic_bits=0, animation_bits=0, remainder_bits=8
    meaning the full byte is the raw enum value.
    """
    logic_bits: int = 0
    animation_bits: int = 0
    remainder_bits: int = 8


@dataclass
class TileInfo:
    """Parsed tile struct information."""
    size_in_bytes: int
    layer_fields: List[TileLayerField] = field(default_factory=list)
    layer_layouts: List[TileLayerLayout] = field(default_factory=list)


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

    layer_layouts = _extract_layer_layouts(source, len(layer_fields))

    return TileInfo(
        size_in_bytes=size,
        layer_fields=layer_fields,
        layer_layouts=layer_layouts)


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
    """
    Parse bitfield declarations from a code block.

    Supports both explicit bit widths (e.g. ``Tile_Kind name : 10;``)
    and plain declarations without bit widths (e.g. ``Tile_Kind name;``).
    When no bit width is specified, the field defaults to 8 bits
    (one byte per layer).
    """
    fields: List[TileLayerField] = []

    # Match: TypeName field_name : N;  (explicit bit width)
    # OR:    TypeName field_name;      (no bit width -> default 8)
    pattern = re.compile(
        r'(\w+)\s+(\w+)\s*(?::\s*(\d+)\s*)?;')
    for match in pattern.finditer(block):
        type_name = match.group(1)
        field_name = match.group(2)
        bit_width_str = match.group(3)

        # Skip primitive types that aren't enum types
        if type_name in ('u8', 'u16', 'u32', 'u64',
                         'i8', 'i16', 'i32', 'i64',
                         'bool', 'struct', 'union'):
            continue

        # Default to 8 bits when no explicit bit width is given
        bit_width = int(bit_width_str) if bit_width_str else 8

        fields.append(TileLayerField(
            enum_type_name=type_name,
            field_name=field_name,
            bit_width=bit_width))

    return fields


def _extract_layer_layouts(
        source: str,
        num_layers: int) -> List[TileLayerLayout]:
    """
    Extract sub-bit field layouts from the GEN-LAYER-BEGIN/END block.

    If the block is empty or absent, returns default layouts
    (logic=0, animation=0, remainder=8) for each layer.
    """
    layer_match = re.search(
        r'GEN-LAYER-BEGIN\s*\n(.*?)GEN-LAYER-END',
        source, re.DOTALL)

    if not layer_match:
        # No GEN-LAYER block: default all layers to 1 byte each
        return [TileLayerLayout() for _ in range(num_layers)]

    block = layer_match.group(1).strip()
    if not block:
        # Empty GEN-LAYER block: default all layers to 1 byte each
        return [TileLayerLayout() for _ in range(num_layers)]

    # Parse sub-bit fields grouped by layer index
    # Pattern: u8 tile_layer_N__field__logic : W;
    #          u8 tile_layer_N__field__animation : W;
    #          u8 tile_layer_N__remainder : W;
    logic_pattern = re.compile(
        r'u8\s+tile_layer_(\d+)__field__logic\s*:\s*(\d+)\s*;')
    anim_pattern = re.compile(
        r'u8\s+tile_layer_(\d+)__field__animation\s*:\s*(\d+)\s*;')
    remainder_pattern = re.compile(
        r'u8\s+tile_layer_(\d+)__remainder\s*:\s*(\d+)\s*;')

    logic_map = {
        int(m.group(1)): int(m.group(2))
        for m in logic_pattern.finditer(block)}
    anim_map = {
        int(m.group(1)): int(m.group(2))
        for m in anim_pattern.finditer(block)}
    remainder_map = {
        int(m.group(1)): int(m.group(2))
        for m in remainder_pattern.finditer(block)}

    layouts = []
    for i in range(num_layers):
        logic = logic_map.get(i, 0)
        anim = anim_map.get(i, 0)
        remainder = remainder_map.get(i, 8)
        layouts.append(TileLayerLayout(
            logic_bits=logic,
            animation_bits=anim,
            remainder_bits=remainder))

    return layouts


def _extract_bitfields_fallback(source: str) -> List[TileLayerField]:
    """
    Fallback: if no GEN-RENDER block, try to find Tile_Kind field
    in the struct body. Supports both explicit bit widths and plain
    declarations (defaulting to 8 bits).
    """
    # Look for Tile_Kind with or without a bit width
    match = re.search(
        r'(Tile_Kind)\s+(\w+)\s*(?::\s*(\d+)\s*)?;', source)
    if match:
        bit_width = int(match.group(3)) if match.group(3) else 8
        return [TileLayerField(
            enum_type_name=match.group(1),
            field_name=match.group(2),
            bit_width=bit_width)]
    return []
