"""
Layer Manager — maps each Tile_Layer to a tilesheet and bitfield config.

Each layer entry stores:
- layer_name: The enum member name (e.g. "Tile_Layer__Ground")
- enum_type_name: The tile kind enum for this layer (e.g. "Tile_Kind")
- tilesheet_path: Project-relative path to the tilesheet PNG
- bit_width: Total bits for this layer's render field (max 32)
- logic_bits: Bits for logic sub-field (max 8, logic+anim <= bit_width)
- animation_bits: Bits for animation sub-field (max 8)

The remainder bits are: bit_width - logic_bits - animation_bits
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LayerEntry:
    """Configuration for a single tile layer."""
    layer_name: str = ""
    enum_type_name: str = "Tile_Kind"
    tilesheet_path: str = ""
    bit_width: int = 8
    logic_bits: int = 0
    animation_bits: int = 0

    @property
    def remainder_bits(self) -> int:
        return max(0, self.bit_width - self.logic_bits - self.animation_bits)

    def validate(self) -> Optional[str]:
        """Return an error message if invalid, else None."""
        if self.bit_width < 1 or self.bit_width > 32:
            return f"bit_width must be 1..32, got {self.bit_width}"
        if self.logic_bits < 0 or self.logic_bits > 8:
            return f"logic_bits must be 0..8, got {self.logic_bits}"
        if self.animation_bits < 0 or self.animation_bits > 8:
            return f"animation_bits must be 0..8, got {self.animation_bits}"
        if self.logic_bits + self.animation_bits > self.bit_width:
            return (
                f"logic_bits({self.logic_bits}) + "
                f"animation_bits({self.animation_bits}) = "
                f"{self.logic_bits + self.animation_bits} exceeds "
                f"bit_width({self.bit_width})")
        return None

    def to_dict(self) -> dict:
        return {
            "layer_name": self.layer_name,
            "enum_type_name": self.enum_type_name,
            "tilesheet_path": self.tilesheet_path,
            "bit_width": self.bit_width,
            "logic_bits": self.logic_bits,
            "animation_bits": self.animation_bits,
        }

    @staticmethod
    def from_dict(d: dict) -> LayerEntry:
        return LayerEntry(
            layer_name=d.get("layer_name", ""),
            enum_type_name=d.get("enum_type_name", "Tile_Kind"),
            tilesheet_path=d.get("tilesheet_path", ""),
            bit_width=d.get("bit_width", 8),
            logic_bits=d.get("logic_bits", 0),
            animation_bits=d.get("animation_bits", 0),
        )


class LayerManager:
    """Manages the mapping from tile layers to tilesheets and bitfields."""

    def __init__(self) -> None:
        self._layers: List[LayerEntry] = []

    @property
    def layers(self) -> List[LayerEntry]:
        return list(self._layers)

    @property
    def count(self) -> int:
        return len(self._layers)

    def get(self, index: int) -> Optional[LayerEntry]:
        if 0 <= index < len(self._layers):
            return self._layers[index]
        return None

    def get_by_name(self, layer_name: str) -> Optional[LayerEntry]:
        for entry in self._layers:
            if entry.layer_name == layer_name:
                return entry
        return None

    def add(self, entry: LayerEntry) -> int:
        """Add a layer entry. Returns its index."""
        self._layers.append(entry)
        return len(self._layers) - 1

    def remove(self, index: int) -> Optional[LayerEntry]:
        """Remove a layer by index. Returns the removed entry."""
        if 0 <= index < len(self._layers):
            return self._layers.pop(index)
        return None

    def update(self, index: int, entry: LayerEntry) -> bool:
        """Update a layer at the given index."""
        if 0 <= index < len(self._layers):
            self._layers[index] = entry
            return True
        return False

    def clear(self) -> None:
        self._layers.clear()

    def set_layers(self, layers: List[LayerEntry]) -> None:
        self._layers = list(layers)

    def to_list(self) -> List[dict]:
        return [e.to_dict() for e in self._layers]

    def from_list(self, data: List[dict]) -> None:
        self._layers = [LayerEntry.from_dict(d) for d in data]

    def get_tilesheet_path_for_layer(self, index: int) -> str:
        """Get the tilesheet path for a layer index."""
        entry = self.get(index)
        if entry:
            return entry.tilesheet_path
        return ""

    def get_unique_tilesheet_paths(self) -> List[str]:
        """Return deduplicated list of tilesheet paths in use."""
        seen = set()
        result = []
        for entry in self._layers:
            if entry.tilesheet_path and entry.tilesheet_path not in seen:
                seen.add(entry.tilesheet_path)
                result.append(entry.tilesheet_path)
        return result


def load_layer_manager_from_config(config_data: dict) -> LayerManager:
    """Load a LayerManager from a world config dict."""
    mgr = LayerManager()
    layers_data = config_data.get("layers", [])
    if isinstance(layers_data, list):
        mgr.from_list(layers_data)
    return mgr


def layer_manager_to_config(mgr: LayerManager) -> List[dict]:
    """Serialize a LayerManager to a config-compatible list."""
    return mgr.to_list()
