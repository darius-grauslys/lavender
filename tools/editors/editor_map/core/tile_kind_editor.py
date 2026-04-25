"""
Data model and file writer for the Tile Kind Editor sub-window.

Manages editing of tile enum members, logical tile assignments,
and animation tile assignments for a single tile layer.
Writes changes back to the project's _kind.h file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.c_enum import CEnum, CEnumMember


@dataclass
class TileKindEntry:
    """An editable tile kind enum entry."""
    name: str
    value: int
    # Index into the tilesheet image for visual representation.
    # -1 means no tilesheet tile assigned.
    tilesheet_tile_index: int = -1


@dataclass
class LogicalTileEntry:
    """A logical tile referencing a tile kind by name."""
    tile_kind_name: str


@dataclass
class AnimationTileEntry:
    """An animation tile referencing a tile kind by name."""
    tile_kind_name: str


@dataclass
class TileKindEditorState:
    """
    Mutable editing state for one tile layer's enum.

    Created from a CEnum, edited in the sub-window,
    and written back to the _kind.h file on OK.
    """
    layer_name: str
    enum_type_name: str
    render_bit_width: int
    logic_bits: int
    animation_bits: int

    tile_kinds: List[TileKindEntry] = field(default_factory=list)
    logical_tiles: List[LogicalTileEntry] = field(default_factory=list)
    animation_tiles: List[AnimationTileEntry] = field(default_factory=list)

    # Search filters
    kind_filter: str = ""
    logic_filter: str = ""
    animation_filter: str = ""

    @property
    def max_tile_kinds(self) -> int:
        """Max expressible value minus 1 (reserve Unknown)."""
        return (1 << self.render_bit_width) - 1

    @property
    def max_logical_tiles(self) -> int:
        if self.logic_bits == 0:
            return 0
        return 1 << self.logic_bits

    @property
    def max_animation_tiles(self) -> int:
        if self.animation_bits == 0:
            return 0
        return 1 << self.animation_bits

    @property
    def can_add_tile_kind(self) -> bool:
        return len(self.tile_kinds) < self.max_tile_kinds

    @property
    def can_add_logical_tile(self) -> bool:
        return (self.logic_bits > 0
                and len(self.logical_tiles) < self.max_logical_tiles)

    @property
    def can_add_animation_tile(self) -> bool:
        return (self.animation_bits > 0
                and len(self.animation_tiles) < self.max_animation_tiles)

    def add_tile_kind(
            self, name: str = "",
            tilesheet_tile_index: int = -1) -> None:
        """Add a new tile kind with the next available value."""
        if not self.can_add_tile_kind:
            return
        next_val = 0
        if self.tile_kinds:
            next_val = max(e.value for e in self.tile_kinds) + 1
        if not name:
            name = f"{self.enum_type_name}__New_{next_val}"
        self.tile_kinds.append(TileKindEntry(
            name=name, value=next_val,
            tilesheet_tile_index=tilesheet_tile_index))

    def remove_tile_kind(self, index: int) -> None:
        """Remove a tile kind by index."""
        if 0 <= index < len(self.tile_kinds):
            removed = self.tile_kinds.pop(index)
            # Also remove references in logical/animation
            self.logical_tiles = [
                lt for lt in self.logical_tiles
                if lt.tile_kind_name != removed.name]
            self.animation_tiles = [
                at for at in self.animation_tiles
                if at.tile_kind_name != removed.name]

    def add_logical_tile(self, tile_kind_name: str = "") -> None:
        if not self.can_add_logical_tile:
            return
        if not tile_kind_name and self.tile_kinds:
            tile_kind_name = self.tile_kinds[0].name
        self.logical_tiles.append(
            LogicalTileEntry(tile_kind_name=tile_kind_name))

    def remove_logical_tile(self, index: int) -> None:
        if 0 <= index < len(self.logical_tiles):
            self.logical_tiles.pop(index)

    def add_animation_tile(self, tile_kind_name: str = "") -> None:
        if not self.can_add_animation_tile:
            return
        if not tile_kind_name and self.tile_kinds:
            tile_kind_name = self.tile_kinds[0].name
        self.animation_tiles.append(
            AnimationTileEntry(tile_kind_name=tile_kind_name))

    def remove_animation_tile(self, index: int) -> None:
        if 0 <= index < len(self.animation_tiles):
            self.animation_tiles.pop(index)


def create_editor_state_from_enum(
        enum: CEnum,
        layer_name: str,
        render_bit_width: int,
        logic_bits: int = 0,
        animation_bits: int = 0,
        tilesheet_map: Optional[Dict[str, int]] = None,
) -> TileKindEditorState:
    """
    Create an editable state from a parsed CEnum.

    Populates tile_kinds from enum members, and separates
    logical/non-logical members using GEN region markers.

    Args:
        tilesheet_map: Optional mapping of enum member name to
            tilesheet tile index. If None, all entries default to -1.
    """
    if tilesheet_map is None:
        tilesheet_map = {}

    state = TileKindEditorState(
        layer_name=layer_name,
        enum_type_name=enum.name,
        render_bit_width=render_bit_width,
        logic_bits=logic_bits,
        animation_bits=animation_bits,
    )

    for member in enum.members:
        # Skip None and Unknown sentinel values
        if member.name.endswith('__None') or member.name.endswith('__Unknown'):
            continue
        # Skip alias members (e.g. Tile_Kind__Logical = Tile_Kind__Water)
        if member.gen_region is None and member.value > 0:
            same_val = [
                m for m in enum.members
                if m.value == member.value and m.name != member.name]
            if same_val:
                continue

        tile_idx = tilesheet_map.get(member.name, -1)
        state.tile_kinds.append(
            TileKindEntry(
                name=member.name, value=member.value,
                tilesheet_tile_index=tile_idx))

        # Populate logical tiles from GEN-LOGIC-BEGIN region
        if member.gen_region and 'LOGIC-BEGIN' in member.gen_region:
            state.logical_tiles.append(
                LogicalTileEntry(tile_kind_name=member.name))

    return state


def write_tile_kind_header(
        filepath: Path,
        state: TileKindEditorState,
        guard_macro: str,
) -> None:
    """
    Write the tile kind enum header file, preserving GEN markers.

    Args:
        filepath: Path to the _kind.h file
        state: The edited state to write
        guard_macro: e.g. "DEFINE_TILE_KIND"
    """
    logical_names = {lt.tile_kind_name for lt in state.logical_tiles}

    logical_kinds = [
        tk for tk in state.tile_kinds if tk.name in logical_names]
    non_logical_kinds = [
        tk for tk in state.tile_kinds if tk.name not in logical_names]

    logical_kinds.sort(key=lambda e: e.value)
    non_logical_kinds.sort(key=lambda e: e.value)

    lines = []
    header_guard = filepath.stem.upper() + "_H"
    lines.append(f"#ifndef {header_guard}")
    lines.append(f"#define {header_guard}")
    lines.append("")
    lines.append('#include "defines_weak.h"')
    lines.append("")
    lines.append(f"#define {guard_macro}")
    lines.append("")
    lines.append(f"typedef enum {state.enum_type_name} {{")
    lines.append(f"    {state.enum_type_name}__None = 0,")

    lines.append("    // GEN-LOGIC-BEGIN")
    for tk in logical_kinds:
        lines.append(f"    {tk.name},")
    lines.append("    // GEN-LOGIC-END")

    if logical_kinds:
        lines.append(
            f"    {state.enum_type_name}__Logical = "
            f"{logical_kinds[-1].name},")
    else:
        lines.append(
            f"    {state.enum_type_name}__Logical = "
            f"{state.enum_type_name}__None,")

    lines.append("")

    lines.append("    // GEN-NO-LOGIC-BEGIN")
    for tk in non_logical_kinds:
        lines.append(f"    {tk.name},")
    lines.append("    // GEN-NO-LOGIC-END")

    lines.append(f"    {state.enum_type_name}__Unknown")
    lines.append(f"}} {state.enum_type_name};")
    lines.append("")
    lines.append("#endif")
    lines.append("")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(lines), encoding='utf-8')


def get_tilesheet_map_from_state(
        state: TileKindEditorState,
) -> Dict[str, int]:
    """
    Extract the tilesheet tile index mapping from editor state.
    Returns a dict of {enum_member_name: tilesheet_tile_index}
    for entries that have a valid (>= 0) tilesheet index.
    """
    return {
        tk.name: tk.tilesheet_tile_index
        for tk in state.tile_kinds
        if tk.tilesheet_tile_index >= 0
    }


def save_tilesheet_mapping(
        filepath: Path,
        mapping: Dict[str, int]) -> None:
    """
    Save tilesheet tile index mapping to a JSON file alongside
    the _kind.h header. The file is named <stem>_tilesheet.json.
    """
    import json
    map_path = filepath.parent / (filepath.stem + "_tilesheet.json")
    map_path.write_text(
        json.dumps(mapping, indent=2) + "\n",
        encoding='utf-8')


def load_tilesheet_mapping(filepath: Path) -> Dict[str, int]:
    """
    Load tilesheet tile index mapping from the JSON file
    alongside the _kind.h header.
    Returns empty dict if file doesn't exist or is invalid.
    """
    import json
    map_path = filepath.parent / (filepath.stem + "_tilesheet.json")
    if not map_path.exists():
        return {}
    try:
        data = json.loads(
            map_path.read_text(encoding='utf-8', errors='replace'))
        if isinstance(data, dict):
            return {k: int(v) for k, v in data.items() if isinstance(v, int)}
    except (json.JSONDecodeError, OSError, ValueError):
        pass
    return {}
