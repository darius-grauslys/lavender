from __future__ import annotations

import pytest
from pathlib import Path

from lavender_tools.lav_impl import (
    PROJECT_ROOT,
    _run,
    _run_build,
    _read_lavender_config,
    _validate_platform,
    _parse_areas,
    gen_sprite_kind,
    scan_assets,
)


class TestHappyPath:
    def test_project_root_exists(self):
        assert isinstance(PROJECT_ROOT, Path)
        assert PROJECT_ROOT.exists()

    def test_run_with_valid_command(self):
        result = _run(["echo", "hello"], project_dir="/tmp")
        assert result == "hello\n"

    def test_run_build_no_guard(self):
        result = _run_build(["echo", "hello"], project_dir="/tmp")
        assert result == "hello\n"

    def test_read_lavender_config_missing(self):
        config_path = Path("/tmp/.lavender/lavender.json")
        if config_path.exists():
            pytest.skip("Unexpected lavender.json exists in /tmp")
        result = _read_lavender_config(project_dir="/tmp")
        assert result is None

    def test_validate_platform_no_config(self):
        result = _validate_platform("sdl", project_dir="/tmp")
        assert result is None

    def test_parse_areas(self):
        result = _parse_areas("x:0,y:0,width:8,height:8")
        assert result == [{"x": 0, "y": 0, "width": 8, "height": 8}]

    def test_gen_sprite_kind_signature(self):
        result = gen_sprite_kind("TestSprite", project_dir="/tmp")
        assert isinstance(result, str)

    def test_scan_assets_signature(self):
        result = scan_assets(project_dir="/tmp")
        assert isinstance(result, str)


class TestCornerCases:
    def test_run_with_failing_command(self):
        result = _run(["false"], project_dir="/tmp")
        assert isinstance(result, str)
        assert result.startswith("ERROR (exit")

    def test_run_from_engine_root(self):
        engine_root = str(PROJECT_ROOT)
        result = _run(["echo", "test"], project_dir=engine_root)
        assert isinstance(result, str)
        assert "ERROR" in result or result != "test\n"
        # The key contract: it does NOT run the command successfully
        assert "test\n" != result

    def test_run_build_from_engine_root(self):
        engine_root = str(PROJECT_ROOT)
        result = _run_build(["echo", "test"], project_dir=engine_root)
        assert result == "test\n"

    def test_parse_areas_multiple(self):
        result = _parse_areas("x:0,y:0,w:8,h:8;x:8,y:0,w:8,h:8")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"x": 0, "y": 0, "w": 8, "h": 8}
        assert result[1] == {"x": 8, "y": 0, "w": 8, "h": 8}
