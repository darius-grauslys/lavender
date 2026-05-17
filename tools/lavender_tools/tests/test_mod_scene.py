"""test_mod_scene.py — Unit tests for scene GEN-marker boilerplate injection.

Tests verify that _gen_register_aliased_textures, _gen_register_ui_windows,
and _gen_allocate_world produce correct C code inside GEN-* marker regions.
"""

from unittest.mock import patch

import pytest

from lavender_tools.mod_scene import (
    _gen_allocate_world,
    _gen_register_aliased_textures,
    _gen_register_tile_logic,
    _gen_register_ui_windows,
)

# Minimal scene .c template with empty GEN regions.
SCENE_TEMPLATE = """\
#include "scene.h"
// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

void m_load_scene_as__test(Scene *p_this_scene, Game *p_game) {
    // GEN-LOAD-BEGIN
    // GEN-LOAD-END
}
"""

# Template with custom code already inside GEN-LOAD.
SCENE_TEMPLATE_WITH_CUSTOM_CODE = """\
#include "scene.h"
// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

void m_load_scene_as__test(Scene *p_this_scene, Game *p_game) {
    // GEN-LOAD-BEGIN
    custom_code_here();
    // GEN-LOAD-END
}
"""


@pytest.fixture
def scene_content(tmp_path):
    """Provide base scene content by reading from a temp file."""
    scene_file = tmp_path / "scene__test.c"
    scene_file.write_text(SCENE_TEMPLATE)
    return scene_file.read_text()


# ---------------------------------------------------------------------------
# _gen_register_aliased_textures
# ---------------------------------------------------------------------------

def test_gen_register_aliased_textures_emits_two_args(scene_content):
    """_gen_register_aliased_textures injects the correct 2-argument call."""
    result = _gen_register_aliased_textures(
        scene_content, "register_aliased_textures"
    )

    assert "get_p_aliased_texture_manager_from__game(p_game)" in result
    assert "p_game);" in result
    assert "register_aliased_textures(p_game);" not in result


def test_gen_register_aliased_textures_is_idempotent(scene_content):
    """Calling _gen_register_aliased_textures twice only inserts once."""
    first = _gen_register_aliased_textures(
        scene_content, "register_aliased_textures"
    )
    second = _gen_register_aliased_textures(
        first, "register_aliased_textures"
    )

    assert second.count("register_aliased_textures") == 1


def test_gen_register_aliased_textures_adds_include(scene_content):
    """The include for aliased_texture_registrar.h is injected into GEN-INCLUDE."""
    result = _gen_register_aliased_textures(
        scene_content, "register_aliased_textures"
    )

    assert '#include "rendering/implemented/aliased_texture_registrar.h"' in result


def test_gen_register_aliased_textures_preserves_other_content(tmp_path):
    """Unrelated content between GEN markers is preserved."""
    scene_file = tmp_path / "scene__test.c"
    scene_file.write_text(SCENE_TEMPLATE_WITH_CUSTOM_CODE)
    content = scene_file.read_text()

    result = _gen_register_aliased_textures(
        content, "register_aliased_textures"
    )

    assert "custom_code_here();" in result


# ---------------------------------------------------------------------------
# _gen_register_ui_windows
# ---------------------------------------------------------------------------

def test_gen_register_ui_windows_emits_correct_call(scene_content):
    """_gen_register_ui_windows injects register_ui_windows into GEN-LOAD."""
    result = _gen_register_ui_windows(scene_content)

    assert "register_ui_windows(" in result


# ---------------------------------------------------------------------------
# _gen_allocate_world
# ---------------------------------------------------------------------------

def test_gen_allocate_world_emits_correct_calls(scene_content):
    """_gen_allocate_world injects allocate and initialize calls."""
    result = _gen_allocate_world(scene_content)

    assert "allocate_world_for__game" in result
    assert "initialize_world" in result


# ---------------------------------------------------------------------------
# _gen_register_tile_logic
# ---------------------------------------------------------------------------

def test_gen_register_tile_logic_emits_correct_call(scene_content):
    """_gen_register_tile_logic injects the correct tile logic registration call."""
    result = _gen_register_tile_logic(
        scene_content, "register_tile_logic_tables"
    )

    assert "get_p_tile_logic_context_from__world" in result
    assert "get_p_world_from__game(p_game)" in result
    assert "register_tile_logic_tables(p_game," in result
    assert "get_p_tile_logic_table_from__world" not in result


def test_gen_register_tile_logic_is_idempotent(scene_content):
    """Calling _gen_register_tile_logic twice only inserts once."""
    first = _gen_register_tile_logic(
        scene_content, "register_tile_logic_tables"
    )
    second = _gen_register_tile_logic(
        first, "register_tile_logic_tables"
    )

    assert second.count("register_tile_logic_tables") == 1


def test_gen_register_tile_logic_adds_include(scene_content):
    """The include for tile_logic_table_registrar.h is injected into GEN-INCLUDE."""
    result = _gen_register_tile_logic(
        scene_content, "register_tile_logic_tables"
    )

    assert '#include "world/implemented/tile_logic_table_registrar.h"' in result


def test_gen_register_tile_logic_preserves_other_content(tmp_path):
    """Unrelated content between GEN markers is preserved."""
    scene_file = tmp_path / "scene__test.c"
    scene_file.write_text(SCENE_TEMPLATE_WITH_CUSTOM_CODE)
    content = scene_file.read_text()

    result = _gen_register_tile_logic(
        content, "register_tile_logic_tables"
    )

    assert "custom_code_here();" in result
