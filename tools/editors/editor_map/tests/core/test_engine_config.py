"""Tests for the engine config parser."""

import pytest
from pathlib import Path

from tools.editors.editor_map.core.engine_config import (
    EngineConfig, load_engine_config, _evaluate_expr, _parse_defines,
)


class TestEvaluateExpr:
    def test_integer(self):
        assert _evaluate_expr('42', {}) == 42

    def test_negative(self):
        assert _evaluate_expr('-1', {}) == -1

    def test_hex(self):
        assert _evaluate_expr('0xFF', {}) == 255

    def test_bit(self):
        assert _evaluate_expr('BIT(3)', {}) == 8

    def test_mask(self):
        assert _evaluate_expr('MASK(4)', {}) == 15

    def test_reference(self):
        assert _evaluate_expr('FOO', {'FOO': 10}) == 10

    def test_bit_with_reference(self):
        assert _evaluate_expr(
            'BIT(CHUNK__DEPTH__BIT_SHIFT)',
            {'CHUNK__DEPTH__BIT_SHIFT': 1}) == 2

    def test_multiplication(self):
        known = {'A': 8, 'B': 8, 'C': 2}
        assert _evaluate_expr('A * B * C', known) == 128

    def test_parenthesized(self):
        known = {'A': 8, 'B': 8}
        assert _evaluate_expr('(A * B)', known) == 64

    def test_unknown_returns_none(self):
        assert _evaluate_expr('UNKNOWN_SYMBOL', {}) is None


class TestParseDefines:
    def test_simple_define(self):
        source = '#define FOO 42\n'
        result = _parse_defines(source, {})
        assert result['FOO'] == 42

    def test_commented_out_skipped(self):
        source = '//#define FOO 42\n'
        result = _parse_defines(source, {})
        assert 'FOO' not in result

    def test_bit_expression(self):
        source = '#define CHUNK__WIDTH BIT(3)\n'
        result = _parse_defines(source, {})
        assert result['CHUNK__WIDTH'] == 8

    def test_with_known_constants(self):
        source = '#define DERIVED BIT(BASE)\n'
        result = _parse_defines(source, {'BASE': 4})
        assert result['DERIVED'] == 16


class TestLoadEngineConfig:
    def test_loads_from_engine_dir(self, tmp_path):
        # Create a minimal platform_defaults.h
        defaults_dir = tmp_path / 'core' / 'include'
        defaults_dir.mkdir(parents=True)
        (defaults_dir / 'platform_defaults.h').write_text(
            '#define CHUNK__WIDTH 8\n'
            '#define CHUNK__HEIGHT 8\n'
            '#define CHUNK__DEPTH 2\n'
            '#define LOCAL_SPACE_MANAGER__WIDTH 8\n'
        )

        config = load_engine_config(tmp_path)
        assert config.chunk_width == 8
        assert config.chunk_height == 8
        assert config.chunk_depth == 2

    def test_project_overrides(self, tmp_path):
        # Engine defaults
        defaults_dir = tmp_path / 'engine' / 'core' / 'include'
        defaults_dir.mkdir(parents=True)
        (defaults_dir / 'platform_defaults.h').write_text(
            '#define CHUNK__WIDTH 8\n'
            '#define CHUNK__DEPTH 2\n'
        )

        # Project override
        project_dir = tmp_path / 'project'
        config_dir = project_dir / 'include' / 'config' / 'implemented'
        config_dir.mkdir(parents=True)
        (config_dir / 'engine_config.h').write_text(
            '#define CHUNK__DEPTH 4\n'
        )

        config = load_engine_config(
            tmp_path / 'engine', project_dir)
        assert config.chunk_width == 8
        assert config.chunk_depth == 4

    def test_derived_constants(self, tmp_path):
        defaults_dir = tmp_path / 'core' / 'include'
        defaults_dir.mkdir(parents=True)
        (defaults_dir / 'platform_defaults.h').write_text(
            '#define CHUNK__WIDTH 8\n'
            '#define CHUNK__HEIGHT 8\n'
            '#define CHUNK__DEPTH 2\n'
        )

        config = load_engine_config(tmp_path)
        assert config.chunk_quantity_of_tiles == 128


class TestEngineConfigProperties:
    def test_defaults_without_files(self, tmp_path):
        config = load_engine_config(tmp_path)
        assert config.chunk_width == 8
        assert config.chunk_height == 8
        assert config.chunk_depth == 2
        assert config.chunk_quantity_of_tiles == 128
        assert config.local_space_manager_width == 8
        assert config.local_space_manager_depth == 1
        assert config.max_quantity_of_entities == 128
        assert config.tile_pixel_size == 8
