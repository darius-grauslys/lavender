"""Tests for workspace objects."""

from workspace.objects import WorkspaceObjects, ChunkData, EntityData
from core.engine_config import EngineConfig


def _make_config() -> EngineConfig:
    config = EngineConfig()
    config.constants['CHUNK__WIDTH'] = 8
    config.constants['CHUNK__HEIGHT'] = 8
    config.constants['CHUNK__DEPTH'] = 2
    config.constants['CHUNK__QUANTITY_OF__TILES'] = 128
    return config


class TestChunkAccess:
    def test_get_chunk_returns_none_when_empty(self):
        obj = WorkspaceObjects(_make_config())
        assert obj.get_chunk(0, 0, 0) is None

    def test_put_and_get_chunk(self):
        obj = WorkspaceObjects(_make_config())
        chunk = ChunkData(0, 0, 0, bytearray(128))
        obj._put_chunk(chunk)
        assert obj.get_chunk(0, 0, 0) is chunk

    def test_remove_chunk(self):
        obj = WorkspaceObjects(_make_config())
        chunk = ChunkData(1, 2, 0, bytearray(128))
        obj._put_chunk(chunk)
        removed = obj._remove_chunk(1, 2, 0)
        assert removed is chunk
        assert obj.get_chunk(1, 2, 0) is None


class TestTileAccess:
    def test_set_and_get_tile(self):
        obj = WorkspaceObjects(_make_config())
        tile_size = 3
        chunk = ChunkData(0, 0, 0, bytearray(128 * tile_size))
        obj._put_chunk(chunk)

        obj.set_tile(0, 0, 0, 0, 0, 0, bytes([1, 2, 3]))
        result = obj.get_tile_bytes(0, 0, 0, 0, 0, 0, tile_size)
        assert result == bytes([1, 2, 3])

    def test_y_inversion(self):
        """Tile at y=0 should be at the end of the row block (Y inverted)."""
        obj = WorkspaceObjects(_make_config())
        tile_size = 1
        chunk = ChunkData(0, 0, 0, bytearray(128 * tile_size))
        obj._put_chunk(chunk)

        # Set tile at (0, 0, 0) — should map to index (7 * 8) + 0 = 56
        obj.set_tile(0, 0, 0, 0, 0, 0, bytes([42]))
        assert chunk.tile_bytes[56] == 42

        # Set tile at (0, 7, 0) — should map to index (0 * 8) + 0 = 0
        obj.set_tile(0, 0, 0, 0, 7, 0, bytes([99]))
        assert chunk.tile_bytes[0] == 99


class TestEntityAccess:
    def test_add_and_get_entity(self):
        obj = WorkspaceObjects(_make_config())
        ent = EntityData(uuid=42, entity_data_bytes=bytearray(8),
                         chunk_x=0, chunk_y=0, chunk_z=0)
        obj.add_entity(ent)
        entities = obj.get_entities_in_chunk(0, 0, 0)
        assert len(entities) == 1
        assert entities[0].uuid == 42

    def test_remove_entity(self):
        obj = WorkspaceObjects(_make_config())
        ent = EntityData(uuid=42, entity_data_bytes=bytearray(8),
                         chunk_x=0, chunk_y=0, chunk_z=0)
        obj.add_entity(ent)
        obj.remove_entity(42)
        assert obj.get_entities_in_chunk(0, 0, 0) == []


class TestDirtyTracking:
    def test_dirty_after_set_tile(self):
        obj = WorkspaceObjects(_make_config())
        chunk = ChunkData(0, 0, 0, bytearray(128))
        obj._put_chunk(chunk)
        obj.set_tile(0, 0, 0, 0, 0, 0, bytes([1]))
        dirty = obj.get_dirty_chunks()
        assert len(dirty) == 1
