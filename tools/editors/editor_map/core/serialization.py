"""
Serialization/deserialization for world data (spec section 4.3).

Handles reading/writing chunk tile files, entity files, etc.
Uses the world_directory module for path generation.
Designed to be called from serialization threads.
"""

from __future__ import annotations

import hashlib
import struct
import tempfile
from pathlib import Path
from typing import Optional

from core.engine_config import EngineConfig
from core.world_directory import (
    chunk_tile_path,
    chunk_entity_path,
    chunk_inventory_path,
    ensure_chunk_dir,
)


def read_chunk_tiles(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        config: EngineConfig,
        tile_size: int) -> Optional[bytearray]:
    """
    Read raw tile data from a chunk's 't' file.
    Returns None if the file doesn't exist.
    """
    path = chunk_tile_path(base_dir, world_name, chunk_x, chunk_y, chunk_z)
    if not path.exists():
        return None
    data = path.read_bytes()
    expected = config.chunk_quantity_of_tiles * tile_size
    if len(data) != expected:
        return None
    return bytearray(data)


def write_chunk_tiles(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        tile_data: bytes) -> bool:
    """
    Write raw tile data to a chunk's 't' file.
    Uses .tmp + checksum + rename pattern per spec section 4.2.
    Returns True on success.
    """
    chunk_path = ensure_chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z)
    target = chunk_path / "t"
    tmp_path = chunk_path / "t.tmp"

    try:
        tmp_path.write_bytes(tile_data)

        # Verify checksum
        checksum = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        expected = hashlib.sha256(tile_data).hexdigest()
        if checksum != expected:
            tmp_path.unlink(missing_ok=True)
            return False

        tmp_path.rename(target)
        return True
    except OSError:
        tmp_path.unlink(missing_ok=True)
        return False


def read_chunk_entities(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int) -> Optional[bytes]:
    """Read raw entity data from a chunk's 'e' file."""
    path = chunk_entity_path(base_dir, world_name, chunk_x, chunk_y, chunk_z)
    if not path.exists():
        return None
    return path.read_bytes()


def write_chunk_entities(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        entity_data: bytes) -> bool:
    """Write raw entity data to a chunk's 'e' file."""
    chunk_path = ensure_chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z)
    target = chunk_path / "e"
    tmp_path = chunk_path / "e.tmp"

    try:
        tmp_path.write_bytes(entity_data)
        checksum = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        expected = hashlib.sha256(entity_data).hexdigest()
        if checksum != expected:
            tmp_path.unlink(missing_ok=True)
            return False
        tmp_path.rename(target)
        return True
    except OSError:
        tmp_path.unlink(missing_ok=True)
        return False


def create_empty_chunk_tiles(config: EngineConfig, tile_size: int) -> bytearray:
    """Create a zeroed tile array for a new chunk."""
    return bytearray(config.chunk_quantity_of_tiles * tile_size)
