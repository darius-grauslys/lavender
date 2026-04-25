"""Tests for serialization module."""

from pathlib import Path

from core.serialization import (
    read_chunk_tiles,
    write_chunk_tiles,
    create_empty_chunk_tiles,
)
from core.engine_config import EngineConfig


def _make_config() -> EngineConfig:
    config = EngineConfig()
    config.constants['CHUNK__WIDTH'] = 8
    config.constants['CHUNK__HEIGHT'] = 8
    config.constants['CHUNK__DEPTH'] = 2
    config.constants['CHUNK__QUANTITY_OF__TILES'] = 128
    return config


class TestCreateEmptyChunkTiles:
    def test_correct_size(self):
        config = _make_config()
        data = create_empty_chunk_tiles(config, tile_size=3)
        assert len(data) == 128 * 3

    def test_all_zeros(self):
        config = _make_config()
        data = create_empty_chunk_tiles(config, tile_size=1)
        assert all(b == 0 for b in data)


class TestWriteAndReadChunkTiles:
    def test_round_trip(self, tmp_path):
        config = _make_config()
        tile_size = 3
        data = bytearray(128 * tile_size)
        data[0] = 42
        data[100] = 99

        success = write_chunk_tiles(
            tmp_path, "test_world", 0, 0, 0, bytes(data))
        assert success

        result = read_chunk_tiles(
            tmp_path, "test_world", 0, 0, 0, config, tile_size)
        assert result is not None
        assert result[0] == 42
        assert result[100] == 99

    def test_read_nonexistent_returns_none(self, tmp_path):
        config = _make_config()
        result = read_chunk_tiles(
            tmp_path, "no_world", 0, 0, 0, config, 1)
        assert result is None
