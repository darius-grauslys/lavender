"""test_tool_invocations.py — Unit tests for lav_ai_app tool functions.

Each test patches ``subprocess.run`` and verifies that the correct command
list is built and that cwd is NOT passed (subprocesses inherit the caller's
CWD).  Return-value handling (success vs non-zero exit) is also tested.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the tools/ directory is importable so ``lav_ai`` is a top-level pkg.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lav_ai.lav_ai_app import (
    PROJECT_ROOT,
    gen_aliased_texture,
    gen_entity,
    gen_game_action,
    gen_png,
    gen_sprite_animation,
    gen_sprite_animation_group,
    gen_sprite_kind,
    gen_tile,
    gen_tile_layer_make_default,
    gen_tile_layer_name,
    gen_ui_code,
    gen_ui_create,
    gen_ui_tile_kind,
    mod_png_condense,
    mod_png_copy,
    mod_png_resize,
    mod_png_set,
    mod_png_swap,
    query_agents_list,
    query_agents_search_permissions,
    query_agents_search_prompts,
    query_agents_show,
    query_agents_verify_clean,
    query_tools_describe,
    query_tools_list,
    query_tools_search,
    read_png,
    read_png_meta,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_completed_process(stdout="ok\n", stderr="", returncode=0):
    mock = MagicMock()
    mock.stdout = stdout
    mock.stderr = stderr
    mock.returncode = returncode
    return mock


# Fake game directory used to bypass the LAVENDER_DIR guard in most tests.
_FAKE_GAME_DIR = PROJECT_ROOT / "_test_game_project"


def _patch_run(return_value):
    """Patch subprocess.run AND Path.cwd so the LAVENDER_DIR guard is bypassed.

    Most tests only care about command construction, not the guard.  Tests
    for the guard itself override the CWD mock explicitly.
    """
    run_patch = patch("lav_ai.lav_ai_app.subprocess.run", return_value=return_value)
    cwd_patch = patch("lav_ai.lav_ai_app.Path.cwd", return_value=_FAKE_GAME_DIR)

    class _CombinedContext:
        """Context manager that stacks both patches and returns the *run* mock."""
        def __enter__(self):
            self._cwd_mock = cwd_patch.__enter__()
            self._run_mock = run_patch.__enter__()
            return self._run_mock

        def __exit__(self, *exc):
            run_patch.__exit__(*exc)
            cwd_patch.__exit__(*exc)

    return _CombinedContext()


# ---------------------------------------------------------------------------
# gen_ui_code
# ---------------------------------------------------------------------------

class TestGenUiCode:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="generated\n")
        with _patch_run(proc) as mock_run:
            result = gen_ui_code("my_ui.xml")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "gen_ui_code.py")
        assert "my_ui.xml" in cmd
        assert "cwd" not in mock_run.call_args.kwargs

    def test_config_overrides(self):
        proc = _make_completed_process(stdout="ok\n")
        with _patch_run(proc) as mock_run:
            gen_ui_code("my_ui.xml", config_overrides="is_outputting true")
        cmd = mock_run.call_args[0][0]
        assert "is_outputting" in cmd
        assert "true" in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="stdout_out\n", stderr="")
        with _patch_run(proc):
            result = gen_ui_code("x.xml")
        assert "stdout_out" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(stdout="", stderr="boom\n", returncode=1)
        with _patch_run(proc):
            result = gen_ui_code("x.xml")
        assert result.startswith("ERROR (exit 1):")
        assert "boom" in result


# ---------------------------------------------------------------------------
# gen_ui_create
# ---------------------------------------------------------------------------

class TestGenUiCreate:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="Created: my_screen.xml\n")
        with _patch_run(proc) as mock_run:
            result = gen_ui_create("my_screen.xml")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "gen_ui.py")
        assert "create" in cmd
        assert "my_screen.xml" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("my_screen.xml")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="Created: out.xml\n")
        with _patch_run(proc):
            result = gen_ui_create("out.xml")
        assert "Created" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="boom\n")
        with _patch_run(proc):
            result = gen_ui_create("out.xml")
        assert result.startswith("ERROR (exit 1):")
        assert "boom" in result

    def test_defaults_omit_optional_args(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml")
        cmd = mock_run.call_args[0][0]
        assert "--sub-dir" not in cmd
        assert "--source-name" not in cmd
        assert "--platform" not in cmd
        assert "--size" not in cmd
        assert "--base-dir" not in cmd
        assert "--offset-of-ui-index" not in cmd
        assert "--include" not in cmd

    def test_sub_dir_added_when_non_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", sub_dir="ui/custom/")
        cmd = mock_run.call_args[0][0]
        assert "--sub-dir" in cmd
        assert "ui/custom/" in cmd

    def test_source_name_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", source_name="my_source")
        cmd = mock_run.call_args[0][0]
        assert "--source-name" in cmd
        assert "my_source" in cmd

    def test_platform_nds(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", platform="NDS")
        cmd = mock_run.call_args[0][0]
        assert "--platform" in cmd
        assert "NDS" in cmd

    def test_size_added_when_non_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", size="320,240")
        cmd = mock_run.call_args[0][0]
        assert "--size" in cmd
        assert "320,240" in cmd

    def test_base_dir_added_when_non_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", base_dir="../other/")
        cmd = mock_run.call_args[0][0]
        assert "--base-dir" in cmd
        assert "../other/" in cmd

    def test_offset_of_ui_index_added_when_nonzero(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", offset_of_ui_index=3)
        cmd = mock_run.call_args[0][0]
        assert "--offset-of-ui-index" in cmd
        assert "3" in cmd

    def test_offset_of_ui_index_omitted_when_zero(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", offset_of_ui_index=0)
        cmd = mock_run.call_args[0][0]
        assert "--offset-of-ui-index" not in cmd

    def test_extra_includes_single(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", extra_includes="ui/ui_ag__slider.h")
        cmd = mock_run.call_args[0][0]
        assert "--include" in cmd
        assert "ui/ui_ag__slider.h" in cmd

    def test_extra_includes_multiple(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create(
                "out.xml",
                extra_includes="ui/ui_ag__slider.h ui/ui_ag__element.h",
            )
        cmd = mock_run.call_args[0][0]
        include_indices = [i for i, x in enumerate(cmd) if x == "--include"]
        assert len(include_indices) == 2
        assert "ui/ui_ag__slider.h" in cmd
        assert "ui/ui_ag__element.h" in cmd

    def test_extra_includes_omitted_when_empty(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", extra_includes="")
        cmd = mock_run.call_args[0][0]
        assert "--include" not in cmd


# ---------------------------------------------------------------------------
# gen_game_action
# ---------------------------------------------------------------------------

class TestGenGameAction:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_game_action("collisions/aabb/update.h")
        cmd = mock_run.call_args[0][0]
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "gen_game_action.py")
        assert "collisions/aabb/update.h" in cmd
        assert "-v" not in cmd

    def test_verbose_flag(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_game_action("foo.h", verbose=True)
        cmd = mock_run.call_args[0][0]
        assert "-v" in cmd

    def test_no_verbose_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_game_action("foo.h")
        cmd = mock_run.call_args[0][0]
        assert "-v" not in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_game_action("foo.h")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_on_nonzero(self):
        proc = _make_completed_process(stderr="err\n", returncode=2)
        with _patch_run(proc):
            result = gen_game_action("bad.h")
        assert result.startswith("ERROR (exit 2):")


# ---------------------------------------------------------------------------
# gen_sprite_kind
# ---------------------------------------------------------------------------

class TestGenSpriteKind:
    def test_command_structure(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_sprite_kind("Player")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_sprite.py") in cmd
        assert "sprite" in cmd
        assert "--name" in cmd
        assert "Player" in cmd

    def test_success(self):
        proc = _make_completed_process(stdout="done\n")
        with _patch_run(proc):
            result = gen_sprite_kind("Player")
        assert "done" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="bad name\n")
        with _patch_run(proc):
            result = gen_sprite_kind("1bad")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_sprite_animation
# ---------------------------------------------------------------------------

class TestGenSpriteAnimation:
    def test_command_structure(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_sprite_animation(
                name="Walk_Right",
                group="Player",
                init_frame=0,
                quantity_of_frames=4,
                ticks_per_frame=8,
                flags="SPRITE_ANIMATION_FLAG__NONE",
            )
        cmd = mock_run.call_args[0][0]
        assert "animation" in cmd
        assert "--name" in cmd
        assert "Walk_Right" in cmd
        assert "--group" in cmd
        assert "Player" in cmd
        assert "--init-frame" in cmd
        assert "0" in cmd
        assert "--quantity-of-frames" in cmd
        assert "4" in cmd
        assert "--ticks-per-frame" in cmd
        assert "8" in cmd
        assert "--flags" in cmd
        assert "SPRITE_ANIMATION_FLAG__NONE" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_sprite_animation("A", "G", 0, 1, 1, "FLAG")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1)
        with _patch_run(proc):
            result = gen_sprite_animation("A", "G", 0, 1, 1, "F")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_sprite_animation_group
# ---------------------------------------------------------------------------

class TestGenSpriteAnimationGroup:
    def test_command_structure(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_sprite_animation_group(
                name="Player",
                quantity_of_columns=4,
                quantity_of_rows=2,
                number_of_animations=8,
            )
        cmd = mock_run.call_args[0][0]
        assert "animation-group" in cmd
        assert "--name" in cmd
        assert "Player" in cmd
        assert "--quantity-of-columns" in cmd
        assert "4" in cmd
        assert "--quantity-of-rows" in cmd
        assert "2" in cmd
        assert "--number-of-animations" in cmd
        assert "8" in cmd

    def test_success(self):
        proc = _make_completed_process(stdout="group added\n")
        with _patch_run(proc):
            result = gen_sprite_animation_group("P", 1, 1, 1)
        assert "group added" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1)
        with _patch_run(proc):
            result = gen_sprite_animation_group("P", 1, 1, 1)
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_png
# ---------------------------------------------------------------------------

class TestGenPng:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_png("sprites/player.png", 32, 4, 4)
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_png.py") in cmd
        assert "--output" in cmd
        assert "sprites/player.png" in cmd
        assert "--frame-resolution" in cmd
        assert "32" in cmd
        assert "--row-count" in cmd
        assert "4" in cmd
        assert "--column-count" in cmd

    def test_no_groups_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_png("out.png", 16, 2, 2)
        cmd = mock_run.call_args[0][0]
        assert "--groups" not in cmd

    def test_groups_path_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_png("out.png", 16, 2, 2, groups_json_path="groups.json")
        cmd = mock_run.call_args[0][0]
        assert "--groups" in cmd
        assert "groups.json" in cmd

    def test_success(self):
        proc = _make_completed_process(stdout="Wrote single file\n")
        with _patch_run(proc):
            result = gen_png("out.png", 8, 1, 1)
        assert "Wrote" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="err\n")
        with _patch_run(proc):
            result = gen_png("out.png", 3, 1, 1)
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_tile
# ---------------------------------------------------------------------------

class TestGenTile:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile("Ground", "Grass")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_tile.py") in cmd
        assert "--layer" in cmd
        assert "Ground" in cmd
        assert "--name" in cmd
        assert "Grass" in cmd
        assert "--is-logical" not in cmd

    def test_is_logical_not_added_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile("Ground", "Grass")
        cmd = mock_run.call_args[0][0]
        assert "--is-logical" not in cmd

    def test_is_logical_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile("Ground", "Lava", is_logical=True)
        cmd = mock_run.call_args[0][0]
        assert "--is-logical" in cmd

    def test_success(self):
        proc = _make_completed_process(stdout="[gen_tile] Done.\n")
        with _patch_run(proc):
            result = gen_tile("Ground", "Grass")
        assert "Done" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="no layer\n")
        with _patch_run(proc):
            result = gen_tile("BadLayer", "Tile")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_tile_layer_name
# ---------------------------------------------------------------------------

class TestGenTileLayerName:
    def test_command_structure(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_name("Ground", 10, 4, 4)
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_tile_layer.py") in cmd
        assert "name" in cmd
        assert "--name" in cmd
        assert "Ground" in cmd
        assert "--bit-field" in cmd
        assert "10" in cmd
        assert "--logic-sub-bit-field" in cmd
        assert "4" in cmd
        assert "--animation-sub-bit-field" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_name("Ground", 10, 4, 4)
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1)
        with _patch_run(proc):
            result = gen_tile_layer_name("Ground", 10, 4, 4)
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_tile_layer_make_default
# ---------------------------------------------------------------------------

class TestGenTileLayerMakeDefault:
    @pytest.mark.parametrize("kind", [
        "default",
        "sight-blocking",
        "is-passable",
        "is-with-ground",
        "height",
    ])
    def test_valid_kinds_pass_correct_flag(self, kind):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_make_default("Ground", kind)
        cmd = mock_run.call_args[0][0]
        assert f"--{kind}" in cmd
        assert "make-default" in cmd
        assert "--name" in cmd
        assert "Ground" in cmd

    def test_invalid_kind_returns_error(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            result = gen_tile_layer_make_default("Ground", "bogus-kind")
        # subprocess.run should NOT have been called
        mock_run.assert_not_called()
        assert "ERROR" in result
        assert "bogus-kind" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1)
        with _patch_run(proc):
            result = gen_tile_layer_make_default("Ground", "default")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# gen_entity
# ---------------------------------------------------------------------------

class TestGenEntity:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_entity.py") in cmd
        assert "--name" in cmd
        assert "Player" in cmd

    def test_optional_flags_absent_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player")
        cmd = mock_run.call_args[0][0]
        for flag in [
            "--gen-f-Dispose", "--gen-f-Update", "--gen-f-Enable",
            "--gen-f-Disable", "--gen-f-Serialize", "--gen-f-Deserialize",
            "--output",
        ]:
            assert flag not in cmd

    def test_gen_dispose_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_dispose=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Dispose" in cmd

    def test_gen_update_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_update=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Update" in cmd

    def test_gen_enable_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_enable=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Enable" in cmd

    def test_gen_disable_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_disable=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Disable" in cmd

    def test_gen_serialize_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_serialize=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Serialize" in cmd

    def test_gen_deserialize_added_when_true(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", gen_deserialize=True)
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Deserialize" in cmd

    def test_output_subdir(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", output="entities/player")
        cmd = mock_run.call_args[0][0]
        assert "--output" in cmd
        assert "entities/player" in cmd

    def test_f_update_method(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", f_update="m_update__player")
        cmd = mock_run.call_args[0][0]
        assert "--f-Update" in cmd
        assert "m_update__player" in cmd

    def test_f_dispose_method(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", f_dispose="m_dispose__player")
        cmd = mock_run.call_args[0][0]
        assert "--f-Dispose" in cmd
        assert "m_dispose__player" in cmd

    def test_f_update_begin_method(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player", f_update_begin="m_update_begin__player")
        cmd = mock_run.call_args[0][0]
        assert "--f-Update-Begin" in cmd
        assert "m_update_begin__player" in cmd

    def test_combined_flags(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity(
                "Enemy",
                gen_update=True,
                gen_dispose=True,
                f_enable="m_enable__enemy",
            )
        cmd = mock_run.call_args[0][0]
        assert "--gen-f-Update" in cmd
        assert "--gen-f-Dispose" in cmd
        assert "--f-Enable" in cmd
        assert "m_enable__enemy" in cmd

    def test_success_returns_stdout(self):
        proc = _make_completed_process(stdout="entity created\n")
        with _patch_run(proc):
            result = gen_entity("Player")
        assert "entity created" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="fail\n")
        with _patch_run(proc):
            result = gen_entity("Player")
        assert result.startswith("ERROR (exit 1):")

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# gen_aliased_texture
# ---------------------------------------------------------------------------

class TestGenAliasedTexture:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_aliased_texture("ground", "assets/world/ground.png")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_aliased_texture.py") in cmd
        assert "--name" in cmd
        assert "ground" in cmd
        assert "--path" in cmd
        assert "assets/world/ground.png" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_aliased_texture("ground", "assets/world/ground.png")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="aliased texture created\n")
        with _patch_run(proc):
            result = gen_aliased_texture("ground", "assets/world/ground.png")
        assert "aliased texture created" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="boom\n")
        with _patch_run(proc):
            result = gen_aliased_texture("ground", "assets/world/ground.png")
        assert result.startswith("ERROR (exit 1):")
        assert "boom" in result

    def test_name_passed_correctly(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_aliased_texture("ground", "assets/world/ground.png")
        cmd = mock_run.call_args[0][0]
        assert "ground" in cmd

    def test_path_passed_correctly(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_aliased_texture("ground", "assets/world/ground.png")
        cmd = mock_run.call_args[0][0]
        assert "assets/world/ground.png" in cmd


# ---------------------------------------------------------------------------
# gen_ui_tile_kind
# ---------------------------------------------------------------------------

class TestGenUiTileKind:
    def test_basic_command_with_integer_value(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_tile_kind("Background_Fill", "104")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "gen_ui_tile_kind.py") in cmd
        assert "--name" in cmd
        assert "Background_Fill" in cmd
        assert "--value" in cmd
        assert "104" in cmd

    def test_basic_command_with_enum_value(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_tile_kind("Button_Toggled_Fill",
                             "UI_Tile_Kind__Button_Fill")
        cmd = mock_run.call_args[0][0]
        assert "--name" in cmd
        assert "Button_Toggled_Fill" in cmd
        assert "--value" in cmd
        assert "UI_Tile_Kind__Button_Fill" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_tile_kind("Test", "42")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="[gen_ui_tile_kind] Done.\n")
        with _patch_run(proc):
            result = gen_ui_tile_kind("Test", "42")
        assert "Done" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="boom\n")
        with _patch_run(proc):
            result = gen_ui_tile_kind("Test", "42")
        assert result.startswith("ERROR (exit 1):")
        assert "boom" in result

    def test_name_and_value_both_required(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_tile_kind("Corner__Top_Left", "65")
        cmd = mock_run.call_args[0][0]
        # Both --name and --value must be present
        name_idx = cmd.index("--name")
        value_idx = cmd.index("--value")
        assert cmd[name_idx + 1] == "Corner__Top_Left"
        assert cmd[value_idx + 1] == "65"


# ---------------------------------------------------------------------------
# mod_png
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Shared helpers for mod_png / read_png test classes
# ---------------------------------------------------------------------------

_MOD_PNG_SCRIPT = str(PROJECT_ROOT / "tools" / "mod_png.py")


def _extract_op_json(cmd):
    """Extract and parse the JSON --op argument from a command list."""
    import json as _json
    op_idx = cmd.index("--op") + 1
    return _json.loads(cmd[op_idx])


# ---------------------------------------------------------------------------
# TestReadPngMeta
# ---------------------------------------------------------------------------

class TestReadPngMeta:
    def test_basic_command(self):
        proc = _make_completed_process(
            stdout="format=RGBA size=64x64\nbase64=iVBORw0KGgo=\n")
        with _patch_run(proc) as mock_run:
            result = read_png_meta(path="sprite.png")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--path" in cmd
        assert "sprite.png" in cmd
        assert "--tile-size" not in cmd
        assert "--op" not in cmd
        assert "base64=" in result

    def test_returns_format_and_base64(self):
        proc = _make_completed_process(
            stdout="format=RGBA size=32x32\nbase64=AAAA\n")
        with _patch_run(proc):
            result = read_png_meta(path="test.png")
        assert "format=RGBA" in result
        assert "size=32x32" in result
        assert "base64=AAAA" in result

    def test_no_cwd(self):
        proc = _make_completed_process(
            stdout="format=RGBA size=8x8\nbase64=X\n")
        with _patch_run(proc) as mock_run:
            read_png_meta(path="sprite.png")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="not found\n")
        with _patch_run(proc):
            result = read_png_meta(path="missing.png")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# TestReadPng
# ---------------------------------------------------------------------------

class TestReadPng:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="sprite.png", tile_size="16x16",
                     type="pixel", areas="x:0,y:0,width:32,height:32")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--path" in cmd
        assert "--tile-size" in cmd
        assert "--op" in cmd
        op = _extract_op_json(cmd)
        assert op["op"] == "read"
        assert op["type"] == "pixel"

    def test_no_value_in_json(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="sprite.png", tile_size="16x16",
                     type="pixel", areas="x:0,y:0,width:32,height:32")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert "value" not in op
        assert "value-type" not in op

    def test_output_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="sprite.png", tile_size="16x16",
                     type="pixel", areas="x:0,y:0,width:32,height:32")
        assert "--output" not in mock_run.call_args[0][0]

    def test_output_arg_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="sprite.png", tile_size="16x16",
                     type="pixel", areas="x:0,y:0,width:32,height:32",
                     output="/tmp/read_out.png")
        cmd = mock_run.call_args[0][0]
        assert "--output" in cmd
        assert "/tmp/read_out.png" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="sprite.png", tile_size="16x16",
                     type="pixel", areas="x:0,y:0")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_tile_coordinate_mode(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            read_png(path="tiles.png", tile_size="32x32",
                     type="tile", areas="x:1,y:2")
        cmd = mock_run.call_args[0][0]
        assert "32x32" in cmd
        op = _extract_op_json(cmd)
        assert op["type"] == "tile"
        assert op["areas"] == [{"x": 1, "y": 2}]


# ---------------------------------------------------------------------------
# TestModPngSet
# ---------------------------------------------------------------------------

class TestModPngSet:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_set(path="sprite.png", tile_size="16x16",
                        type="pixel", areas="x:0,y:0",
                        value="255,0,0,255", value_type="pixel")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--tile-size" in cmd
        assert "--path" in cmd
        assert "--op" in cmd

    def test_op_json_constructed(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_set(path="sprite.png", tile_size="16x16",
                        type="pixel", areas="x:0,y:0",
                        value="255,0,0,255", value_type="pixel")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert op["op"] == "set"
        assert op["type"] == "pixel"
        assert op["areas"] == [{"x": 0, "y": 0}]
        assert op["value"] == "255,0,0,255"
        assert op["value-type"] == "pixel"

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_set(path="sprite.png", tile_size="16x16",
                        type="pixel", areas="x:0,y:0",
                        value="0,0,0,255", value_type="pixel")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="Saved: sprite.png\n")
        with _patch_run(proc):
            result = mod_png_set(path="sprite.png", tile_size="16x16",
                                 type="pixel", areas="x:0,y:0",
                                 value="0,0,0,255", value_type="pixel")
        assert "Saved" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="boom\n")
        with _patch_run(proc):
            result = mod_png_set(path="sprite.png", tile_size="16x16",
                                 type="pixel", areas="x:0,y:0",
                                 value="0,0,0,255", value_type="pixel")
        assert result.startswith("ERROR (exit 1):")

    def test_output_not_in_cmd_by_default(self):
        """mod_png_set does not accept an output parameter; it modifies in place."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_set(path="sprite.png", tile_size="16x16",
                        type="pixel", areas="x:0,y:0",
                        value="0,0,0,255", value_type="pixel")
        assert "--output" not in mock_run.call_args[0][0]


# ---------------------------------------------------------------------------
# TestModPngSwap
# ---------------------------------------------------------------------------

class TestModPngSwap:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_swap(path="sprite.png", tile_size="16x16",
                         type="pixel",
                         areas="x:0,y:0,width:8,height:8;x:8,y:0,width:8,height:8")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--op" in cmd

    def test_two_areas_parsed(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_swap(path="sprite.png", tile_size="16x16",
                         type="pixel",
                         areas="x:0,y:0,width:8,height:8;x:8,y:0,width:8,height:8")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert op["op"] == "swap"
        assert len(op["areas"]) == 2
        assert op["areas"][0] == {"x": 0, "y": 0, "width": 8, "height": 8}
        assert op["areas"][1] == {"x": 8, "y": 0, "width": 8, "height": 8}

    def test_no_value_in_json(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_swap(path="sprite.png", tile_size="16x16",
                         type="pixel",
                         areas="x:0,y:0;x:1,y:0")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert "value" not in op
        assert "value-type" not in op

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_swap(path="sprite.png", tile_size="16x16",
                         type="pixel", areas="x:0,y:0;x:1,y:0")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestModPngCopy
# ---------------------------------------------------------------------------

class TestModPngCopy:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_copy(path="sprite.png", tile_size="16x16",
                         type="pixel",
                         areas="x:0,y:0,width:2,height:2;x:4,y:0,width:2,height:2")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--op" in cmd

    def test_op_is_copy(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_copy(path="sprite.png", tile_size="16x16",
                         type="tile",
                         areas="x:0,y:0;x:2,y:0;x:4,y:0")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert op["op"] == "copy"
        assert len(op["areas"]) == 3

    def test_no_value_in_json(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_copy(path="sprite.png", tile_size="16x16",
                         type="pixel", areas="x:0,y:0;x:1,y:0")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert "value" not in op
        assert "value-type" not in op

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_copy(path="sprite.png", tile_size="16x16",
                         type="pixel", areas="x:0,y:0;x:1,y:0")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestModPngResize
# ---------------------------------------------------------------------------

class TestModPngResize:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="Saved: test.png\n")
        with _patch_run(proc) as mock_run:
            result = mod_png_resize(path="test.png", tile_size="16x16",
                                    areas="x:0,y:0,width:128,height:128",
                                    value="0,0,0,0")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--op" in cmd
        op = _extract_op_json(cmd)
        assert op["op"] == "resize"
        assert op["areas"] == [{"x": 0, "y": 0, "width": 128, "height": 128}]
        assert "Saved" in result

    def test_always_pixel_type(self):
        """resize always passes type='pixel' and value-type='pixel'."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_resize(path="test.png", tile_size="16x16",
                           areas="x:0,y:0,width:64,height:64",
                           value="0,0,0,0")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert op["type"] == "pixel"
        assert op["value-type"] == "pixel"
        assert op["value"] == "0,0,0,0"

    def test_output_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_resize(path="test.png", tile_size="16x16",
                           areas="x:0,y:0,width:64,height:64",
                           value="0,0,0,0")
        assert "--output" not in mock_run.call_args[0][0]

    def test_output_arg_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_resize(path="test.png", tile_size="16x16",
                           areas="x:0,y:0,width:64,height:64",
                           value="0,0,0,0", output="/tmp/resized.png")
        cmd = mock_run.call_args[0][0]
        assert "--output" in cmd
        assert "/tmp/resized.png" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_resize(path="test.png", tile_size="16x16",
                           areas="x:0,y:0,width:64,height:64",
                           value="0,0,0,0")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestModPngCondense
# ---------------------------------------------------------------------------

class TestModPngCondense:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="64x64\n")
        with _patch_run(proc) as mock_run:
            result = mod_png_condense(path="tiles.png", tile_size="16x16",
                                      areas="x:0,y:0,width:8,height:8",
                                      value="0,0,0,0",
                                      output="tiles_condensed.png")
        cmd = mock_run.call_args[0][0]
        assert _MOD_PNG_SCRIPT in cmd
        assert "--op" in cmd
        assert "--output" in cmd
        assert "tiles_condensed.png" in cmd
        assert "64x64" in result

    def test_always_tile_type_and_pixel_value_type(self):
        """condense always passes type='tile' and value-type='pixel'."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_condense(path="tiles.png", tile_size="16x16",
                             areas="x:0,y:0,width:4,height:4",
                             value="0,0,0,0", output="out.png")
        op = _extract_op_json(mock_run.call_args[0][0])
        assert op["op"] == "condense"
        assert op["type"] == "tile"
        assert op["value-type"] == "pixel"
        assert op["value"] == "0,0,0,0"

    def test_output_is_required(self):
        """condense requires an output path — verify it always appears in cmd."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_condense(path="tiles.png", tile_size="16x16",
                             areas="x:0,y:0,width:4,height:4",
                             value="0,0,0,0", output="condensed.png")
        assert "--output" in mock_run.call_args[0][0]

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            mod_png_condense(path="tiles.png", tile_size="16x16",
                             areas="x:0,y:0,width:4,height:4",
                             value="0,0,0,0", output="out.png")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# Query tools helpers
# ---------------------------------------------------------------------------

_QUERY_TOOLS_SCRIPT = str(PROJECT_ROOT / "tools" / "lav_query_tools.py")
_QUERY_AGENTS_SCRIPT = str(PROJECT_ROOT / "tools" / "lav_query_agents.py")


# ---------------------------------------------------------------------------
# TestQueryToolsList
# ---------------------------------------------------------------------------

class TestQueryToolsList:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="gen_entity\ngen_png\n")
        with _patch_run(proc) as mock_run:
            result = query_tools_list()
        cmd = mock_run.call_args[0][0]
        assert _QUERY_TOOLS_SCRIPT in cmd
        assert "list" in cmd
        assert "gen_entity" in result

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_tools_list()
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(returncode=1, stderr="fail\n")
        with _patch_run(proc):
            result = query_tools_list()
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# TestQueryToolsSearch
# ---------------------------------------------------------------------------

class TestQueryToolsSearch:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="mod_png_set\nmod_png_swap\n")
        with _patch_run(proc) as mock_run:
            result = query_tools_search(pattern="mod_png")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_TOOLS_SCRIPT in cmd
        assert "search" in cmd
        assert "--pattern" in cmd
        assert "mod_png" in cmd
        assert "mod_png_set" in result

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_tools_search(pattern="test")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryToolsDescribe
# ---------------------------------------------------------------------------

class TestQueryToolsDescribe:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="name: gen_entity\n")
        with _patch_run(proc) as mock_run:
            result = query_tools_describe(name="gen_entity")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_TOOLS_SCRIPT in cmd
        assert "describe" in cmd
        assert "--name" in cmd
        assert "gen_entity" in cmd
        assert "gen_entity" in result

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_tools_describe(name="gen_entity")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryAgentsList
# ---------------------------------------------------------------------------

class TestQueryAgentsList:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="planner\ncoder\n")
        with _patch_run(proc) as mock_run:
            result = query_agents_list()
        cmd = mock_run.call_args[0][0]
        assert _QUERY_AGENTS_SCRIPT in cmd
        assert "list" in cmd
        assert "planner" in result

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_list()
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryAgentsShow
# ---------------------------------------------------------------------------

class TestQueryAgentsShow:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="name: planner\n")
        with _patch_run(proc) as mock_run:
            result = query_agents_show(agent="planner")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_AGENTS_SCRIPT in cmd
        assert "show" in cmd
        assert "--agent" in cmd
        assert "planner" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_show(agent="planner")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryAgentsSearchPrompts
# ---------------------------------------------------------------------------

class TestQueryAgentsSearchPrompts:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="planner: 2 match(es)\n")
        with _patch_run(proc) as mock_run:
            result = query_agents_search_prompts(pattern="gen_entity")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_AGENTS_SCRIPT in cmd
        assert "search-prompts" in cmd
        assert "--pattern" in cmd
        assert "gen_entity" in cmd

    def test_agent_filter_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_prompts(pattern="test")
        assert "--agent" not in mock_run.call_args[0][0]

    def test_agent_filter_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_prompts(pattern="test", agent="planner")
        cmd = mock_run.call_args[0][0]
        assert "--agent" in cmd
        assert "planner" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_prompts(pattern="test")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryAgentsSearchPermissions
# ---------------------------------------------------------------------------

class TestQueryAgentsSearchPermissions:
    def test_basic_command(self):
        proc = _make_completed_process(
            stdout="  spritesheet-animator: lavender-tools_gen_png = allow\n")
        with _patch_run(proc) as mock_run:
            result = query_agents_search_permissions(pattern="gen_png")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_AGENTS_SCRIPT in cmd
        assert "search-permissions" in cmd
        assert "--pattern" in cmd

    def test_agent_filter_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_permissions(pattern="allow")
        assert "--agent" not in mock_run.call_args[0][0]

    def test_agent_filter_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_permissions(pattern="allow", agent="coder")
        cmd = mock_run.call_args[0][0]
        assert "--agent" in cmd
        assert "coder" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_search_permissions(pattern="test")
        assert "cwd" not in mock_run.call_args.kwargs


# ---------------------------------------------------------------------------
# TestQueryAgentsVerifyClean
# ---------------------------------------------------------------------------

class TestQueryAgentsVerifyClean:
    def test_basic_command(self):
        proc = _make_completed_process(stdout="planner: clean\ncoder: clean\n")
        with _patch_run(proc) as mock_run:
            result = query_agents_verify_clean(pattern="old_tool")
        cmd = mock_run.call_args[0][0]
        assert _QUERY_AGENTS_SCRIPT in cmd
        assert "verify-clean" in cmd
        assert "--pattern" in cmd
        assert "old_tool" in cmd
        assert "clean" in result

    def test_agent_filter_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_verify_clean(pattern="test")
        assert "--agent" not in mock_run.call_args[0][0]

    def test_agent_filter_added_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_verify_clean(pattern="test", agent="planner")
        cmd = mock_run.call_args[0][0]
        assert "--agent" in cmd
        assert "planner" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            query_agents_verify_clean(pattern="test")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_on_stale_refs(self):
        proc = _make_completed_process(returncode=1,
                                        stderr="WARNING: planner has 1 stale\n")
        with _patch_run(proc):
            result = query_agents_verify_clean(pattern="old_name")
        assert result.startswith("ERROR (exit 1):")


# ---------------------------------------------------------------------------
# TestLavenderDirGuard
# ---------------------------------------------------------------------------

class TestLavenderDirGuard:
    """Tests that _run() refuses to execute when CWD == PROJECT_ROOT."""

    def test_guard_blocks_execution_in_lavender_dir(self):
        """When CWD == PROJECT_ROOT, _run() must return an error without calling subprocess."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run, \
             patch("lav_ai.lav_ai_app.Path.cwd", return_value=PROJECT_ROOT):
            result = gen_sprite_kind("Test")
        mock_run.assert_not_called()
        assert "ERROR" in result
        assert "Refusing to run" in result
        assert "Lavender engine directory" in result

    def test_guard_allows_execution_in_game_dir(self):
        """When CWD != PROJECT_ROOT, _run() should proceed normally."""
        proc = _make_completed_process(stdout="ok\n")
        fake_game_dir = PROJECT_ROOT / "nonexistent_game_project"
        with _patch_run(proc) as mock_run, \
             patch("lav_ai.lav_ai_app.Path.cwd", return_value=fake_game_dir):
            result = gen_sprite_kind("Test")
        mock_run.assert_called_once()
        assert "ok" in result

    def test_guard_error_includes_project_root_path(self):
        """The guard error message must include the PROJECT_ROOT path for debugging."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run, \
             patch("lav_ai.lav_ai_app.Path.cwd", return_value=PROJECT_ROOT):
            result = gen_ui_code("test.xml")
        assert str(PROJECT_ROOT) in result
