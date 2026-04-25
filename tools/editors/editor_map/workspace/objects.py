"""
Workspace object management (spec section 4.2).

Manages in-memory representations of world objects.
Thread safety: serialization threads use _private methods only.
Public methods are safe to call from the main thread.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.engine_config import EngineConfig


@dataclass
class ChunkData:
    """In-memory representation of a chunk's tile data."""
    chunk_x: int
    chunk_y: int
    chunk_z: int
    tile_bytes: bytearray  # Raw tile data
    is_dirty: bool = False


@dataclass
class EntityData:
    """In-memory representation of a serialized entity."""
    uuid: int
    entity_data_bytes: bytearray
    chunk_x: int
    chunk_y: int
    chunk_z: int
    has_hitbox: bool = False
    has_inventory: bool = False


class WorkspaceObjects:
    """
    Manages loaded world objects with thread-safe access.

    Public methods: main thread only.
    _private methods: serialization thread access (documented).
    """

    def __init__(self, config: EngineConfig):
        self._config = config
        self._lock = threading.Lock()
        self._chunks: Dict[Tuple[int, int, int], ChunkData] = {}
        self._entities: Dict[int, EntityData] = {}
        self._loading_chunks: set = set()

    # -- Public API (main thread) --

    def get_chunk(self, x: int, y: int, z: int) -> Optional[ChunkData]:
        """Get a loaded chunk, or None if not loaded."""
        with self._lock:
            return self._chunks.get((x, y, z))

    def get_entities_in_chunk(self, x: int, y: int, z: int) -> List[EntityData]:
        """Get all entities in a given chunk."""
        with self._lock:
            return [
                e for e in self._entities.values()
                if e.chunk_x == x and e.chunk_y == y and e.chunk_z == z
            ]

    def is_chunk_loading(self, x: int, y: int, z: int) -> bool:
        with self._lock:
            return (x, y, z) in self._loading_chunks

    def mark_chunk_loading(self, x: int, y: int, z: int) -> None:
        with self._lock:
            self._loading_chunks.add((x, y, z))

    def set_tile(
            self, chunk_x: int, chunk_y: int, chunk_z: int,
            local_x: int, local_y: int, local_z: int,
            tile_bytes: bytes) -> None:
        """Set a tile within a loaded chunk."""
        with self._lock:
            chunk = self._chunks.get((chunk_x, chunk_y, chunk_z))
            if chunk is None:
                return
            tile_size = len(tile_bytes)
            cw = self._config.chunk_width
            ch = self._config.chunk_height
            # Y-inverted indexing per chunk.h get_p_tile_from__chunk
            index = (
                local_x
                + ((ch - 1 - local_y) * cw)
                + (cw * ch * local_z)
            )
            offset = index * tile_size
            chunk.tile_bytes[offset:offset + tile_size] = tile_bytes
            chunk.is_dirty = True

    def get_tile_bytes(
            self, chunk_x: int, chunk_y: int, chunk_z: int,
            local_x: int, local_y: int, local_z: int,
            tile_size: int) -> Optional[bytes]:
        """Get raw tile bytes from a loaded chunk."""
        with self._lock:
            chunk = self._chunks.get((chunk_x, chunk_y, chunk_z))
            if chunk is None:
                return None
            cw = self._config.chunk_width
            ch = self._config.chunk_height
            index = (
                local_x
                + ((ch - 1 - local_y) * cw)
                + (cw * ch * local_z)
            )
            offset = index * tile_size
            return bytes(chunk.tile_bytes[offset:offset + tile_size])

    def add_entity(self, entity: EntityData) -> None:
        with self._lock:
            self._entities[entity.uuid] = entity

    def remove_entity(self, uuid: int) -> None:
        with self._lock:
            self._entities.pop(uuid, None)

    def get_dirty_chunks(self) -> List[ChunkData]:
        """Return all chunks that have been modified."""
        with self._lock:
            return [c for c in self._chunks.values() if c.is_dirty]

    # -- Private API (serialization thread) --
    # These methods are ONLY to be called by serialization
    # processes spawned by workspace.movement.

    def _put_chunk(self, chunk: ChunkData) -> None:
        """Store a deserialized chunk. Called by serialization thread."""
        with self._lock:
            self._chunks[(chunk.chunk_x, chunk.chunk_y, chunk.chunk_z)] = chunk
            self._loading_chunks.discard(
                (chunk.chunk_x, chunk.chunk_y, chunk.chunk_z))

    def _remove_chunk(self, x: int, y: int, z: int) -> Optional[ChunkData]:
        """Remove and return a chunk. Called by serialization thread."""
        with self._lock:
            return self._chunks.pop((x, y, z), None)

    def _put_entity(self, entity: EntityData) -> None:
        """Store a deserialized entity. Called by serialization thread."""
        with self._lock:
            self._entities[entity.uuid] = entity
