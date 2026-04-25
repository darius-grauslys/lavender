"""
Workspace object management (spec section 4.2).

Manages in-memory representations of world objects.
Thread safety: serialization threads use _private methods only.
Public methods are safe to call from the main thread.

.tmp file management:
- When a chunk is modified (set_tile), a .tmp file is written
  to the chunk directory alongside the real tile file.
- A list of pending .tmp chunk keys is maintained internally.
- When the pending count reaches ``max_tmp_chunks`` (configurable
  in the project-level editor.json, default 1024), an auto-save
  is triggered: each .tmp is checksummed and promoted to the
  real file if the checksum passes.

Chunk loading:
- If a chunk file does not exist on disk when requested, an
  empty chunk (all-zero tile bytes) is created in memory and
  made publicly accessible.
"""

from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from core.engine_config import EngineConfig
from core.world_directory import (
    chunk_tile_path,
    chunk_tile_tmp_path,
    ensure_chunk_dir,
)

if TYPE_CHECKING:
    from ui.message_hud import MessageHUD


def compute_checksum(data: bytes) -> str:
    """Compute a SHA-256 hex digest for *data*."""
    return hashlib.sha256(data).hexdigest()


def verify_tmp_checksum(tmp_path: Path) -> bool:
    """Read a .tmp file and its .sha256 sidecar, return True if match."""
    sha_path = tmp_path.with_suffix(tmp_path.suffix + ".sha256")
    if not tmp_path.exists() or not sha_path.exists():
        return False
    data = tmp_path.read_bytes()
    expected = sha_path.read_text(encoding='utf-8').strip()
    return compute_checksum(data) == expected


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

    def __init__(
            self,
            config: EngineConfig,
            project_dir: Optional[Path] = None,
            world_name: str = "",
            platform: str = "",
            max_tmp_chunks: int = 1024,
            message_hud: Optional[MessageHUD] = None):
        self._config = config
        self._project_dir = project_dir
        self._world_name = world_name
        self._platform = platform
        self._max_tmp_chunks = max_tmp_chunks
        self._message_hud = message_hud
        self._lock = threading.Lock()
        self._chunks: Dict[Tuple[int, int, int], ChunkData] = {}
        self._entities: Dict[int, EntityData] = {}
        self._loading_chunks: set = set()
        self._saving_chunks: set = set()
        # Ordered dict of chunk keys with pending .tmp files.
        self._pending_tmp: OrderedDict[Tuple[int, int, int], bool] = \
            OrderedDict()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_world(
            self,
            project_dir: Path,
            world_name: str,
            platform: str) -> None:
        """Set the active world for serialization paths."""
        self._project_dir = project_dir
        self._world_name = world_name
        self._platform = platform

    @property
    def max_tmp_chunks(self) -> int:
        return self._max_tmp_chunks

    @max_tmp_chunks.setter
    def max_tmp_chunks(self, value: int) -> None:
        self._max_tmp_chunks = max(1, value)

    @property
    def pending_tmp_count(self) -> int:
        """Number of chunks with pending .tmp files."""
        with self._lock:
            return len(self._pending_tmp)

    # ------------------------------------------------------------------
    # Public API (main thread)
    # ------------------------------------------------------------------

    def get_chunk(self, x: int, y: int, z: int) -> Optional[ChunkData]:
        """Get a loaded chunk, or None if not loaded."""
        with self._lock:
            return self._chunks.get((x, y, z))

    def get_or_create_chunk(
            self, x: int, y: int, z: int) -> ChunkData:
        """Get a loaded chunk, loading from disk or creating empty.

        If the chunk is not in memory:
        1. Try to load from the tile file on disk.
        2. If the file does not exist, create an empty (all-zero)
           chunk and store it in memory.

        The chunk is always publicly accessible after this call.
        """
        with self._lock:
            existing = self._chunks.get((x, y, z))
            if existing is not None:
                return existing

        # Outside lock — do disk I/O
        chunk = self._load_chunk_from_disk(x, y, z)
        with self._lock:
            # Double-check after re-acquiring lock
            existing = self._chunks.get((x, y, z))
            if existing is not None:
                return existing
            self._chunks[(x, y, z)] = chunk
            self._loading_chunks.discard((x, y, z))
        return chunk

    def get_entities_in_chunk(
            self, x: int, y: int, z: int) -> List[EntityData]:
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
        """Set a tile within a loaded chunk.

        Marks the chunk dirty and writes a .tmp file to disk.
        If the pending .tmp count reaches ``max_tmp_chunks``,
        triggers an auto-save flush.
        """
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
            key = (chunk_x, chunk_y, chunk_z)
            self._pending_tmp[key] = True
            tile_data_snapshot = bytes(chunk.tile_bytes)

        # Write .tmp outside lock
        self._write_tmp(
            chunk_x, chunk_y, chunk_z, tile_data_snapshot)

        # Check auto-save threshold
        if self.pending_tmp_count >= self._max_tmp_chunks:
            self.flush_all_tmp()

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

    @property
    def pending_operations_count(self) -> int:
        """Number of in-flight async operations (loads + saves)."""
        with self._lock:
            return len(self._loading_chunks) + len(self._saving_chunks)

    def mark_chunk_saving(self, x: int, y: int, z: int) -> None:
        with self._lock:
            self._saving_chunks.add((x, y, z))

    def unmark_chunk_saving(self, x: int, y: int, z: int) -> None:
        with self._lock:
            self._saving_chunks.discard((x, y, z))

    # ------------------------------------------------------------------
    # .tmp file management
    # ------------------------------------------------------------------

    def _write_tmp(
            self,
            chunk_x: int, chunk_y: int, chunk_z: int,
            tile_data: bytes) -> bool:
        """Write tile data to a .tmp file with a .sha256 sidecar.

        Returns True on success.
        """
        if not self._project_dir or not self._world_name:
            return False
        try:
            ensure_chunk_dir(
                self._project_dir, self._world_name,
                chunk_x, chunk_y, chunk_z,
                platform=self._platform)
            tmp_path = chunk_tile_tmp_path(
                self._project_dir, self._world_name,
                chunk_x, chunk_y, chunk_z,
                platform=self._platform)
            tmp_path.write_bytes(tile_data)
            sha_path = tmp_path.with_suffix(
                tmp_path.suffix + ".sha256")
            sha_path.write_text(
                compute_checksum(tile_data), encoding='utf-8')
            return True
        except OSError as e:
            if self._message_hud:
                self._message_hud.error(
                    f"Failed to write .tmp for chunk "
                    f"({chunk_x},{chunk_y},{chunk_z}): {e}")
            return False

    def flush_single_tmp(
            self,
            chunk_x: int,
            chunk_y: int,
            chunk_z: int) -> bool:
        """Promote a single .tmp file to the real tile file.

        Returns True if the checksum passed and the file was
        promoted, False otherwise.
        """
        if not self._project_dir or not self._world_name:
            return False
        key = (chunk_x, chunk_y, chunk_z)
        tmp_path = chunk_tile_tmp_path(
            self._project_dir, self._world_name,
            chunk_x, chunk_y, chunk_z,
            platform=self._platform)
        if not verify_tmp_checksum(tmp_path):
            if self._message_hud:
                self._message_hud.error(
                    f"Checksum failed for chunk "
                    f"({chunk_x},{chunk_y},{chunk_z}). "
                    f"Save aborted for this chunk.")
            return False

        real_path = chunk_tile_path(
            self._project_dir, self._world_name,
            chunk_x, chunk_y, chunk_z,
            platform=self._platform)
        try:
            # Atomic-ish rename
            tmp_path.replace(real_path)
            # Clean up sidecar
            sha_path = tmp_path.with_suffix(
                tmp_path.suffix + ".sha256")
            if sha_path.exists():
                sha_path.unlink()
        except OSError as e:
            if self._message_hud:
                self._message_hud.error(
                    f"Failed to promote .tmp for chunk "
                    f"({chunk_x},{chunk_y},{chunk_z}): {e}")
            return False

        with self._lock:
            self._pending_tmp.pop(key, None)
            chunk = self._chunks.get(key)
            if chunk:
                chunk.is_dirty = False
        return True

    def flush_all_tmp(self) -> int:
        """Promote all pending .tmp files to real tile files.

        Returns the number of successfully promoted chunks.
        """
        with self._lock:
            keys = list(self._pending_tmp.keys())
        count = 0
        for key in keys:
            if self.flush_single_tmp(*key):
                count += 1
        if self._message_hud:
            self._message_hud.info(
                f"Auto-save: {count}/{len(keys)} chunks saved.")
        return count

    # ------------------------------------------------------------------
    # Chunk loading from disk
    # ------------------------------------------------------------------

    def _load_chunk_from_disk(
            self, x: int, y: int, z: int) -> ChunkData:
        """Load a chunk from the tile file, or create empty.

        If the tile file does not exist, creates an empty chunk
        with all-zero tile bytes.
        """
        total_tiles = self._config.chunk_quantity_of_tiles
        tile_size = 1  # Default; caller should set properly
        if self._project_dir and self._world_name:
            tile_path = chunk_tile_path(
                self._project_dir, self._world_name,
                x, y, z, platform=self._platform)
            if tile_path.exists():
                try:
                    raw = tile_path.read_bytes()
                    return ChunkData(
                        chunk_x=x, chunk_y=y, chunk_z=z,
                        tile_bytes=bytearray(raw),
                        is_dirty=False)
                except OSError as e:
                    if self._message_hud:
                        self._message_hud.error(
                            f"Failed to read chunk "
                            f"({x},{y},{z}): {e}")

        # Create empty chunk
        empty_size = total_tiles * tile_size
        return ChunkData(
            chunk_x=x, chunk_y=y, chunk_z=z,
            tile_bytes=bytearray(empty_size),
            is_dirty=False)

    def load_chunk(self, x: int, y: int, z: int) -> ChunkData:
        """Public convenience: load or create a chunk and store it."""
        return self.get_or_create_chunk(x, y, z)

    # ------------------------------------------------------------------
    # Private API (serialization thread)
    # ------------------------------------------------------------------
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
