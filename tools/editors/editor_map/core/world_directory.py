"""
Python port of core/source/world/serialization/world_directory.c

Replicates the engine's world filesystem layout exactly,
including the quad-tree chunk directory descent and hex encoding.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple


def _hex2(value: int) -> str:
    """Format lower 8 bits as 2-char hex, matching engine's append_u32_as__hex_to__path with beginning_index=2."""
    # Engine extracts top nibbles first after shifting.
    # With beginning_index=2, it shifts value left by (8-2)*4=24 bits,
    # then extracts top nibble twice.
    # For small values this means: high nibble, low nibble of the byte.
    value &= 0xFF
    return f"{value:02x}"


def _hex8(value: int) -> str:
    """Format as 8-char hex, matching engine's append_u32_as__hex_to__path with beginning_index=8."""
    value &= 0xFFFFFFFF
    return f"{value:08x}"


def saves_root(base_dir: Path, platform: str) -> Path:
    """Get the saves root directory: <base>/build/<platform>/saves/"""
    return base_dir / "build" / platform / "saves"


def world_root(
        base_dir: Path,
        world_name: str,
        platform: str) -> Path:
    """Get the world root directory.

    If *platform* is provided:
        <base>/build/<platform>/saves/<world_name>/
    Otherwise falls back to legacy path:
        <base>/save/<world_name>/
    """
    return saves_root(base_dir, platform) / world_name


def world_header_path(
        base_dir: Path,
        world_name: str,
        platform: str) -> Path:
    """Get the world header file path."""
    return world_root(base_dir, world_name, platform) / "h"


def region_dir(
        base_dir: Path,
        world_name: str,
        region_x: int,
        region_y: int,
        region_z: int,
        platform: str) -> Path:
    """Get the region directory path."""
    root = world_root(base_dir, world_name, platform)
    region_name = f"r_{_hex8(region_x)}_{_hex8(region_y)}_{_hex8(region_z)}"
    return root / region_name


def chunk_dir(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        region_width_bit_shift: int = 11) -> Path:
    """
    Get the full chunk directory path, replicating the engine's
    quad-tree descent from world_directory.c::stat_chunk_directory.

    Args:
        base_dir: Project base directory
        world_name: Name of the world
        chunk_x, chunk_y, chunk_z: Chunk coordinates
        region_width_bit_shift: Bit shift for region width (default 11)
        platform: Target platform name for save directory
    """
    # Compute region vector (same as engine's get_region_that__this_global_space_is_in)
    region_x = chunk_x >> region_width_bit_shift
    region_y = chunk_y >> region_width_bit_shift
    region_z = chunk_z  # z is passed through

    path = region_dir(
        base_dir, world_name, region_x, region_y, region_z,
        platform=platform)

    # Mask chunk coords to 8 bits for quad-tree descent
    cx = chunk_x & 0xFF
    cy = chunk_y & 0xFF

    # Quad-tree descent: 6 levels
    descend_x = 127
    descend_y = 127
    descend_z = 127
    quad_x = 128
    quad_y = 128

    for _level in range(6):
        if cx > descend_x:
            descend_x += quad_x
        else:
            descend_x -= quad_x

        if cy > descend_y:
            descend_y += quad_y
        else:
            descend_y -= quad_y

        dir_name = f"c_{_hex2(descend_x)}_{_hex2(descend_y)}_{_hex2(descend_z)}"
        path = path / dir_name

        quad_x >>= 1
        quad_y >>= 1

    # Final leaf directory with actual chunk coords
    leaf_name = f"c_{_hex2(cx)}_{_hex2(cy)}_{_hex2(chunk_z & 0xFF)}"
    path = path / leaf_name

    return path


def chunk_tile_path(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        **kwargs) -> Path:
    """Path to the tile file for a chunk."""
    return chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z,
        platform=platform, **kwargs) / "t"


def chunk_tile_tmp_path(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        **kwargs) -> Path:
    """Path to the .tmp tile file for a chunk."""
    return chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z,
        platform=platform, **kwargs) / "t.tmp"


def chunk_entity_path(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        **kwargs) -> Path:
    """Path to the entity file for a chunk."""
    return chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z,
        platform=platform, **kwargs) / "e"


def chunk_inventory_path(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        **kwargs) -> Path:
    """Path to the inventory file for a chunk."""
    return chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z,
        platform=platform, **kwargs) / "i"


def list_worlds(base_dir: Path, platform: str = "") -> list[str]:
    """List all world names in the save directory."""
    if platform:
        save_dir = saves_root(base_dir, platform)
    else:
        save_dir = base_dir / "save"
    if not save_dir.is_dir():
        return []
    return sorted([
        d.name for d in save_dir.iterdir()
        if d.is_dir()
    ])


def ensure_chunk_dir(
        base_dir: Path,
        world_name: str,
        chunk_x: int,
        chunk_y: int,
        chunk_z: int,
        platform: str,
        **kwargs) -> Path:
    """Create the chunk directory tree if it doesn't exist, return the path."""
    path = chunk_dir(
        base_dir, world_name, chunk_x, chunk_y, chunk_z,
        platform=platform, **kwargs)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_world_dir(
        base_dir: Path,
        world_name: str,
        platform: str) -> Path:
    """Create the world root directory if it doesn't exist."""
    path = world_root(base_dir, world_name, platform)
    path.mkdir(parents=True, exist_ok=True)
    return path


def world_editor_config_path(
        base_dir: Path,
        world_name: str,
        platform: str) -> Path:
    """Get the per-world editor.json path."""
    return world_root(base_dir, world_name, platform) / "editor.json"
