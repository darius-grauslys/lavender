"""Tests for the world directory port."""

from pathlib import Path

from core.world_directory import (
    world_root,
    world_header_path,
    chunk_dir,
    chunk_tile_path,
    chunk_entity_path,
    chunk_inventory_path,
    list_worlds,
    ensure_world_dir,
    ensure_chunk_dir,
)


class TestWorldRoot:
    def test_basic_path(self):
        p = world_root(Path("/game"), "test_world")
        assert p == Path("/game/save/test_world")


class TestWorldHeaderPath:
    def test_header_file(self):
        p = world_header_path(Path("/game"), "w")
        assert p == Path("/game/save/w/h")


class TestChunkDir:
    def test_returns_path_with_quad_tree(self):
        p = chunk_dir(Path("/g"), "w", 0, 0, 0)
        # Should have region dir + 6 quad levels + leaf
        parts = p.parts
        # Find the region dir
        region_parts = [x for x in parts if x.startswith("r_")]
        assert len(region_parts) == 1
        # Find chunk dirs
        chunk_parts = [x for x in parts if x.startswith("c_")]
        assert len(chunk_parts) == 7  # 6 quad + 1 leaf

    def test_different_coords_give_different_paths(self):
        p1 = chunk_dir(Path("/g"), "w", 0, 0, 0)
        p2 = chunk_dir(Path("/g"), "w", 1, 0, 0)
        assert p1 != p2


class TestChunkFilePaths:
    def test_tile_path_ends_with_t(self):
        p = chunk_tile_path(Path("/g"), "w", 0, 0, 0)
        assert p.name == "t"

    def test_entity_path_ends_with_e(self):
        p = chunk_entity_path(Path("/g"), "w", 0, 0, 0)
        assert p.name == "e"

    def test_inventory_path_ends_with_i(self):
        p = chunk_inventory_path(Path("/g"), "w", 0, 0, 0)
        assert p.name == "i"


class TestListWorlds:
    def test_empty_when_no_save_dir(self, tmp_path):
        assert list_worlds(tmp_path) == []

    def test_lists_world_dirs(self, tmp_path):
        save = tmp_path / "save"
        save.mkdir()
        (save / "alpha").mkdir()
        (save / "beta").mkdir()
        # Files should be ignored
        (save / "not_a_world.txt").write_text("x")
        result = list_worlds(tmp_path)
        assert result == ["alpha", "beta"]


class TestEnsureDirs:
    def test_ensure_world_dir(self, tmp_path):
        p = ensure_world_dir(tmp_path, "test")
        assert p.is_dir()
        assert p == tmp_path / "save" / "test"

    def test_ensure_chunk_dir(self, tmp_path):
        p = ensure_chunk_dir(tmp_path, "test", 5, 5, 0)
        assert p.is_dir()
