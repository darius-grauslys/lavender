"""
Parse engine_config.h and platform_defaults.h to resolve
engine constants.

The project's engine_config.h contains commented-out #define
directives. Projects uncomment lines to override defaults from
platform_defaults.h.

This parser:
1. Reads the project-local engine_config.h
2. Reads the engine's platform_defaults.h
3. Resolves all constants, with project overrides taking precedence
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class EngineConfig:
    """Resolved engine constants."""
    constants: Dict[str, int] = field(default_factory=dict)

    def get(self, name: str, default: Optional[int] = None) -> Optional[int]:
        return self.constants.get(name, default)

    @property
    def chunk_width(self) -> int:
        return self.constants.get('CHUNK__WIDTH', 8)

    @property
    def chunk_height(self) -> int:
        # Engine has a typo: CHUNK_HEIGHT vs CHUNK__HEIGHT
        return self.constants.get(
            'CHUNK__HEIGHT',
            self.constants.get('CHUNK_HEIGHT', 8))

    @property
    def chunk_depth(self) -> int:
        return self.constants.get('CHUNK__DEPTH', 2)

    @property
    def chunk_quantity_of_tiles(self) -> int:
        return self.constants.get(
            'CHUNK__QUANTITY_OF__TILES',
            self.chunk_width * self.chunk_height * self.chunk_depth)

    @property
    def local_space_manager_width(self) -> int:
        return self.constants.get('LOCAL_SPACE_MANAGER__WIDTH', 8)

    @property
    def local_space_manager_height(self) -> int:
        return self.constants.get('LOCAL_SPACE_MANAGER__HEIGHT', 8)

    @property
    def local_space_manager_depth(self) -> int:
        return self.constants.get('LOCAL_SPACE_MANAGER__DEPTH', 1)

    @property
    def max_quantity_of_entities(self) -> int:
        return self.constants.get('MAX_QUANTITY_OF__ENTITIES', 128)

    @property
    def tile_width_and_height_bit_shift(self) -> int:
        return self.constants.get('TILE__WIDTH_AND__HEIGHT__BIT_SHIFT', 3)

    @property
    def tile_pixel_size(self) -> int:
        return 1 << self.tile_width_and_height_bit_shift


def _evaluate_expr(
        expr: str,
        known: Dict[str, int]) -> Optional[int]:
    """Evaluate a simple C #define value expression."""
    expr = expr.strip()

    # Integer literal
    if re.match(r'^-?\d+$', expr):
        return int(expr)

    # Hex literal
    if re.match(r'^0[xX][0-9a-fA-F]+$', expr):
        return int(expr, 16)

    # BIT(n)
    bit_match = re.match(r'^BIT\((\w+)\)$', expr)
    if bit_match:
        inner = bit_match.group(1)
        inner_val = _evaluate_expr(inner, known)
        if inner_val is not None:
            return 1 << inner_val
        return None

    # MASK(n)
    mask_match = re.match(r'^MASK\((\w+)\)$', expr)
    if mask_match:
        inner = mask_match.group(1)
        inner_val = _evaluate_expr(inner, known)
        if inner_val is not None:
            return (1 << inner_val) - 1
        return None

    # Reference to another constant
    if expr in known:
        return known[expr]

    # Parenthesized expression with simple arithmetic
    # Handle (A * B * C), (A + B), (A >> B), (A << B)
    # Strip outer parens
    if expr.startswith('(') and expr.endswith(')'):
        return _evaluate_expr(expr[1:-1], known)

    # Multiplication chain: A * B * C
    if '*' in expr and '>>' not in expr and '<<' not in expr:
        parts = expr.split('*')
        result = 1
        for part in parts:
            val = _evaluate_expr(part.strip(), known)
            if val is None:
                return None
            result *= val
        return result

    # Addition
    if '+' in expr and '>>' not in expr and '<<' not in expr:
        parts = expr.split('+')
        result = 0
        for part in parts:
            val = _evaluate_expr(part.strip(), known)
            if val is None:
                return None
            result += val
        return result

    # Shift right
    sr_match = re.match(r'^(\w+)\s*>>\s*(\w+)$', expr)
    if sr_match:
        lhs = _evaluate_expr(sr_match.group(1), known)
        rhs = _evaluate_expr(sr_match.group(2), known)
        if lhs is not None and rhs is not None:
            return lhs >> rhs
        return None

    # Shift left
    sl_match = re.match(r'^(\w+)\s*<<\s*(\w+)$', expr)
    if sl_match:
        lhs = _evaluate_expr(sl_match.group(1), known)
        rhs = _evaluate_expr(sl_match.group(2), known)
        if lhs is not None and rhs is not None:
            return lhs << rhs
        return None

    return None


def _parse_defines(source: str, known: Dict[str, int]) -> Dict[str, int]:
    """
    Parse uncommented #define lines from C source.
    Only parses simple value definitions, not function-like macros.
    """
    results: Dict[str, int] = {}
    # Match: #define NAME value
    # Skip lines that are commented out (start with //)
    for line in source.split('\n'):
        stripped = line.strip()
        # Skip commented-out defines
        if stripped.startswith('//') or stripped.startswith('/*'):
            continue
        define_match = re.match(
            r'#\s*define\s+(\w+)\s+(.+?)(?:\s*(?://|/\*).*)?$',
            stripped)
        if not define_match:
            continue
        name = define_match.group(1)
        value_expr = define_match.group(2).strip()

        # Skip function-like macros and string macros
        if '(' in name or value_expr.startswith('"'):
            continue
        # Skip multi-line macros (ending with \)
        if value_expr.endswith('\\'):
            continue

        # Merge known + results for resolution
        merged = {**known, **results}
        val = _evaluate_expr(value_expr, merged)
        if val is not None:
            results[name] = val

    return results


def _parse_defines_multiline(
        source: str, known: Dict[str, int]) -> Dict[str, int]:
    """
    Parse #define directives including multi-line ones (with backslash
    continuation). Only resolves to integer values.
    """
    results: Dict[str, int] = {}
    lines = source.split('\n')
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        # Skip commented-out defines
        if stripped.startswith('//') or stripped.startswith('/*'):
            i += 1
            continue

        define_match = re.match(
            r'#\s*define\s+(\w+)\s+(.*)', stripped)
        if not define_match:
            i += 1
            continue

        name = define_match.group(1)
        value_expr = define_match.group(2).strip()

        # Skip function-like macros
        if '(' in name:
            i += 1
            continue

        # Collect continuation lines
        while value_expr.endswith('\\'):
            value_expr = value_expr[:-1].strip()
            i += 1
            if i < len(lines):
                value_expr += ' ' + lines[i].strip()

        # Strip trailing comments
        value_expr = re.sub(r'//.*$', '', value_expr).strip()
        value_expr = re.sub(r'/\*.*?\*/', '', value_expr).strip()

        # Skip string macros
        if value_expr.startswith('"') or value_expr.startswith("'"):
            i += 1
            continue

        merged = {**known, **results}
        val = _evaluate_expr(value_expr, merged)
        if val is not None:
            results[name] = val

        i += 1

    return results


def load_engine_config(
        engine_dir: Path,
        project_dir: Optional[Path] = None) -> EngineConfig:
    """
    Load engine configuration by parsing platform_defaults.h
    and optionally the project's engine_config.h override.

    Args:
        engine_dir: Path to the engine root (contains core/)
        project_dir: Path to the project root (contains include/).
                     If None, only engine defaults are loaded.
    """
    config = EngineConfig()

    # 1. Parse engine platform_defaults.h for defaults
    defaults_path = engine_dir / 'core' / 'include' / 'platform_defaults.h'
    if defaults_path.exists():
        source = defaults_path.read_text(encoding='utf-8', errors='replace')
        config.constants.update(
            _parse_defines_multiline(source, config.constants))

    # Handle the CHUNK_HEIGHT typo: if CHUNK_HEIGHT is defined but
    # CHUNK__HEIGHT is not, alias it
    if 'CHUNK_HEIGHT' in config.constants \
            and 'CHUNK__HEIGHT' not in config.constants:
        config.constants['CHUNK__HEIGHT'] = config.constants['CHUNK_HEIGHT']

    # 2. Parse project engine_config.h overrides
    if project_dir:
        project_config_path = (
            project_dir / 'include' / 'config' / 'implemented'
            / 'engine_config.h')
        if project_config_path.exists():
            source = project_config_path.read_text(
                encoding='utf-8', errors='replace')
            overrides = _parse_defines_multiline(
                source, config.constants)
            config.constants.update(overrides)

            # Re-check the typo alias after overrides
            if 'CHUNK_HEIGHT' in config.constants \
                    and 'CHUNK__HEIGHT' not in config.constants:
                config.constants['CHUNK__HEIGHT'] = \
                    config.constants['CHUNK_HEIGHT']

    # 3. Compute derived constants if not already present
    _ensure_derived(config)

    return config


def _ensure_derived(config: EngineConfig) -> None:
    """Compute derived constants from base constants."""
    c = config.constants

    if 'CHUNK__WIDTH' not in c:
        bit_shift = c.get('CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT', 3)
        c['CHUNK__WIDTH'] = 1 << bit_shift

    if 'CHUNK__HEIGHT' not in c:
        bit_shift = c.get('CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT', 3)
        c['CHUNK__HEIGHT'] = 1 << bit_shift

    if 'CHUNK__DEPTH' not in c:
        bit_shift = c.get('CHUNK__DEPTH__BIT_SHIFT', 1)
        c['CHUNK__DEPTH'] = 1 << bit_shift

    if 'CHUNK__QUANTITY_OF__TILES' not in c:
        c['CHUNK__QUANTITY_OF__TILES'] = (
            c['CHUNK__WIDTH'] * c['CHUNK__HEIGHT'] * c['CHUNK__DEPTH'])

    if 'VOLUME_OF__LOCAL_SPACE_MANAGER' not in c:
        c['VOLUME_OF__LOCAL_SPACE_MANAGER'] = (
            c.get('LOCAL_SPACE_MANAGER__WIDTH', 8)
            * c.get('LOCAL_SPACE_MANAGER__HEIGHT', 8)
            * c.get('LOCAL_SPACE_MANAGER__DEPTH', 1))

    if 'QUANTITY_OF__GLOBAL_SPACE' not in c:
        c['QUANTITY_OF__GLOBAL_SPACE'] = (
            c.get('VOLUME_OF__LOCAL_SPACE_MANAGER', 64)
            * c.get('MAX_QUANTITY_OF__CLIENTS', 4))
