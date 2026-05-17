"""test_tool_invocations.py — Unit tests for lav_ai_app tool functions.

Each test patches ``subprocess.run`` and verifies that the correct command
list is built and that cwd is NOT passed (subprocesses inherit the caller's
CWD).  Return-value handling (success vs non-zero exit) is also tested.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import json

import pytest

from lavender_tools.lav_ai.lav_ai_app import (
    PROJECT_ROOT,
    build,
    build_compile_commands,
    build_spot_check,
    gen_aliased_texture,
    gen_lav_project,
    gen_scene,
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
    scan_ui,
    scan_entity,
    scan_scene,
    scan_textures,
    scan_game_actions,
    clangd_definition,
    clangd_references,
    clangd_symbols,
    clangd_workspace_symbol,
    clangd_hover,
    gen_window,
    gen_chunk_generator,
    mod_scene,
    mod_entity,
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
    run_patch = patch("lavender_tools.lav_ai.lav_ai_app.subprocess.run", return_value=return_value)
    cwd_patch = patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=_FAKE_GAME_DIR)

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
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_ui_code.py")
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
# _derive_window_name (gen_ui.py)
# ---------------------------------------------------------------------------

class TestDeriveWindowName:
    def test_single_word(self):
        from lavender_tools.gen_ui import _derive_window_name
        assert _derive_window_name("ui_window__hud") == "Hud"

    def test_multi_word_pascal_case(self):
        from lavender_tools.gen_ui import _derive_window_name
        assert _derive_window_name("ui_window__main_menu__buttons") == "Main_Menu__Buttons"

    def test_without_prefix(self):
        from lavender_tools.gen_ui import _derive_window_name
        assert _derive_window_name("pause_menu__overlay") == "Pause_Menu__Overlay"


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
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_ui.py")
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

    def test_window_name_passed_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml", window_name="World__HUD")
        cmd = mock_run.call_args[0][0]
        assert "--window-name" in cmd
        assert "World__HUD" in cmd

    def test_window_name_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_ui_create("out.xml")
        cmd = mock_run.call_args[0][0]
        assert "--window-name" not in cmd

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
        assert cmd[1] == str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_game_action.py")
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_sprite.py") in cmd
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_png.py") in cmd
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_tile.py") in cmd
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_tile_layer.py") in cmd
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

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="[gen_tile_layer] Done.\n")
        with _patch_run(proc):
            result = gen_tile_layer_name("Ground", 8, 4, 2)
        assert "Done" in result

    def test_all_args_passed_as_strings(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_name("Cover", 10, 6, 4)
        cmd = mock_run.call_args[0][0]
        assert "10" in cmd
        assert "6" in cmd
        assert "4" in cmd

    def test_two_layer_sequential_calls_independent(self):
        """Simulates the pipeline pattern: create Ground, then Cover."""
        proc1 = _make_completed_process(stdout="[gen_tile_layer] Done.\n")
        proc2 = _make_completed_process(stdout="[gen_tile_layer] Done.\n")
        with _patch_run(proc1) as mock_run:
            result1 = gen_tile_layer_name("Ground", 8, 4, 2)
        with _patch_run(proc2) as mock_run:
            result2 = gen_tile_layer_name("Cover", 8, 4, 2)
        assert "Done" in result1
        assert "Done" in result2

    def test_error_message_includes_stderr(self):
        proc = _make_completed_process(
            stdout="", stderr="logic + animation exceed total\n", returncode=1)
        with _patch_run(proc):
            result = gen_tile_layer_name("Bad", 4, 3, 3)
        assert result.startswith("ERROR (exit 1):")
        assert "logic + animation exceed total" in result


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

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(
            stdout="[gen_tile_layer] Setting Tile_Layer__Default__Is_Passable = Tile_Layer__Ground\n")
        with _patch_run(proc):
            result = gen_tile_layer_make_default("Ground", "is-passable")
        assert "Setting" in result

    def test_name_is_passed_correctly(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_make_default("Cover", "sight-blocking")
        cmd = mock_run.call_args[0][0]
        name_idx = cmd.index("--name")
        assert cmd[name_idx + 1] == "Cover"

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_tile_layer_make_default("Ground", "default")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_error_message_includes_invalid_kind(self):
        proc = _make_completed_process()
        with _patch_run(proc):
            result = gen_tile_layer_make_default("Ground", "non-existent-kind")
        assert "non-existent-kind" in result
        assert "Must be one of" in result


# ---------------------------------------------------------------------------
# gen_entity
# ---------------------------------------------------------------------------

class TestGenEntity:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_entity("Player")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_entity.py") in cmd
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_aliased_texture.py") in cmd
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
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_ui_tile_kind.py") in cmd
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

_MOD_PNG_SCRIPT = str(PROJECT_ROOT / "tools" / "lavender_tools" / "mod_png.py")


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

_QUERY_TOOLS_SCRIPT = str(PROJECT_ROOT / "tools" / "lavender_tools" / "lav_query_tools.py")
_QUERY_AGENTS_SCRIPT = str(PROJECT_ROOT / "tools" / "lavender_tools" / "lav_query_agents.py")


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
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=PROJECT_ROOT):
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
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=fake_game_dir):
            result = gen_sprite_kind("Test")
        mock_run.assert_called_once()
        assert "ok" in result

    def test_guard_error_includes_project_root_path(self):
        """The guard error message must include the PROJECT_ROOT path for debugging."""
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run, \
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=PROJECT_ROOT):
            result = gen_ui_code("test.xml")
        assert str(PROJECT_ROOT) in result


# ---------------------------------------------------------------------------
# Build tool helper — _run_build has no CWD guard, so we only patch subprocess.
# ---------------------------------------------------------------------------

def _patch_run_build(return_value):
    """Patch subprocess.run for build tools (no CWD guard to bypass)."""
    return patch("lavender_tools.lav_ai.lav_ai_app.subprocess.run", return_value=return_value)


# ===========================================================================
# Tool 22 – build
# ===========================================================================

class TestBuild:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl")
        cmd = mock_run.call_args[0][0]
        assert "tools/lavender_tools/build.py" in cmd[1]
        assert "--platform" in cmd
        assert "sdl" in cmd

    def test_flags_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl", flags="-ggdb -w")
        cmd = mock_run.call_args[0][0]
        assert any("--flags=" in arg for arg in cmd)
        assert any("-ggdb -w" in arg for arg in cmd)

    def test_clean_flag(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl", clean=True)
        cmd = mock_run.call_args[0][0]
        assert "--clean" in cmd

    def test_clean_flag_absent_by_default(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl")
        cmd = mock_run.call_args[0][0]
        assert "--clean" not in cmd

    def test_game_dir_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl", game_dir="/tmp/TestGame")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" in cmd
        assert "/tmp/TestGame" in cmd

    def test_game_dir_absent_by_default(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build("sdl")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" not in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="Build complete\n")
        with _patch_run_build(proc):
            result = build("sdl")
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 0
        assert "Build complete" in parsed["build_output"]

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(stdout="", stderr="error msg\n", returncode=2)
        with _patch_run_build(proc):
            result = build("sdl")
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 2
        assert parsed["build_output"].startswith("ERROR (exit 2):")

    def test_no_cwd_guard(self):
        """Build tools must work from the engine directory — no CWD guard."""
        proc = _make_completed_process(stdout="ok\n")
        with _patch_run_build(proc) as mock_run:
            result = build("sdl")
        mock_run.assert_called_once()
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 0
        assert "ok" in parsed["build_output"]

    def test_returns_json_dict(self):
        proc = _make_completed_process(stdout="Build complete\n")
        with _patch_run_build(proc):
            result = build("sdl")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "build_exit_code" in parsed
        assert "build_output" in parsed


# ===========================================================================
# Tool 23 – build_compile_commands
# ===========================================================================

class TestBuildCompileCommands:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_compile_commands("sdl")
        cmd = mock_run.call_args[0][0]
        assert "tools/lavender_tools/build_compile_commands.py" in cmd[1]
        assert "--platform" in cmd
        assert "sdl" in cmd

    def test_flags_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_compile_commands("sdl", flags="-ggdb -w")
        cmd = mock_run.call_args[0][0]
        assert "--flags=-ggdb -w" in cmd

    def test_game_dir_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_compile_commands("sdl", game_dir="/tmp/TestGame")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" in cmd
        assert "/tmp/TestGame" in cmd

    def test_game_dir_absent_by_default(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_compile_commands("sdl")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" not in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="compile_commands.json written\n")
        with _patch_run_build(proc):
            result = build_compile_commands("sdl")
        assert "compile_commands" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(stdout="", stderr="fail\n", returncode=1)
        with _patch_run_build(proc):
            result = build_compile_commands("sdl")
        assert result.startswith("ERROR (exit 1):")


# ===========================================================================
# Tool 24 – build_spot_check
# ===========================================================================

class TestBuildSpotCheck:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check("sdl", "core/source/input/input.c")
        cmd = mock_run.call_args[0][0]
        assert "tools/lavender_tools/build_spot_check.py" in cmd[1]
        assert "--platform" in cmd
        assert "sdl" in cmd
        assert "--file" in cmd
        assert "core/source/input/input.c" in cmd

    def test_flags_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check("sdl", "test.c", flags="-ggdb")
        cmd = mock_run.call_args[0][0]
        assert any("--flags=" in arg for arg in cmd)
        assert any("-ggdb" in arg for arg in cmd)

    def test_game_dir_passed(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check("sdl", "source/scene.c", game_dir="/tmp/TestGame")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" in cmd
        assert "/tmp/TestGame" in cmd

    def test_game_dir_absent_by_default(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check("sdl", "test.c")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" not in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="", stderr="")
        with _patch_run_build(proc):
            result = build_spot_check("sdl", "test.c")
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 0
        assert parsed["build_output"] == ""

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(
            stdout="", stderr="test.c:4:10: error: undeclared\n", returncode=1)
        with _patch_run_build(proc):
            result = build_spot_check("sdl", "test.c")
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 1
        assert "undeclared" in parsed["build_output"]

    def test_no_cwd_guard(self):
        """Build tools must work from the engine directory — no CWD guard."""
        proc = _make_completed_process(stdout="ok\n")
        with _patch_run_build(proc) as mock_run:
            result = build_spot_check("sdl", "test.c")
        mock_run.assert_called_once()
        parsed = json.loads(result)
        assert parsed["build_exit_code"] == 0
        assert "ok" in parsed["build_output"]

    def test_returns_json_dict(self):
        proc = _make_completed_process(stdout="")
        with _patch_run_build(proc):
            result = build_spot_check("sdl", "test.c")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "build_exit_code" in parsed
        assert "build_output" in parsed

    def test_absolute_path_accepted(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check("sdl", "/abs/path/to/file.c")
        cmd = mock_run.call_args[0][0]
        assert "/abs/path/to/file.c" in cmd


# ===========================================================================
# Tool 25 – gen_scene
# ===========================================================================

class TestGenScene:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_scene("Main_Menu")
        cmd = mock_run.call_args[0][0]
        assert "tools/lavender_tools/gen_scene.py" in cmd[1]
        assert "--name" in cmd
        assert "Main_Menu" in cmd

    def test_ui_xml_omitted_by_default(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_scene("World")
        cmd = mock_run.call_args[0][0]
        assert "--ui-xml" not in cmd

    def test_ui_xml_passed_when_provided(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_scene("World", ui_xml="assets/ui/xml/sdl/game/ui__world.xml")
        cmd = mock_run.call_args[0][0]
        assert "--ui-xml" in cmd
        assert "assets/ui/xml/sdl/game/ui__world.xml" in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="Scene 'World' generated successfully.\n")
        with _patch_run(proc):
            result = gen_scene("World")
        assert "generated successfully" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(stdout="", stderr="Error: bad name\n", returncode=1)
        with _patch_run(proc):
            result = gen_scene("123bad")
        assert result.startswith("ERROR (exit 1):")

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_scene("Test")
        assert mock_run.call_args[1].get("cwd") is None

    def test_main_menu_no_double_suffix(self, tmp_path, monkeypatch):
        """Integration test: gen_scene must not produce register_scene__main_menu_menu."""
        # Build minimal fake game project structure
        (tmp_path / "include" / "types" / "implemented" / "scene").mkdir(parents=True)
        (tmp_path / "source" / "scene" / "implemented").mkdir(parents=True)

        scene_kind = tmp_path / "include" / "types" / "implemented" / "scene" / "scene_kind.h"
        scene_kind.write_text(
            "#ifndef IMPL_SCENE_KIND_H\n"
            "#define IMPL_SCENE_KIND_H\n"
            "#define DEFINE_SCENE_KIND\n"
            "typedef enum Scene_Kind {\n"
            "    Scene_Kind__None = 0,\n"
            "    // GEN-BEGIN\n"
            "    // GEN-END\n"
            "    Scene_Kind__Unknown\n"
            "} Scene_Kind;\n"
            "#endif\n"
        )

        registrar = tmp_path / "source" / "scene" / "implemented" / "scene_registrar.c"
        registrar.write_text(
            '#include "scene/implemented/scene_registrar.h"\n'
            "// GEN-INCLUDE-BEGIN\n"
            '#include "scene/implemented/scene__main.h"\n'
            "// GEN-INCLUDE-END\n"
            "\n"
            "void register_scenes(Scene_Manager *p_scene_manager) {\n"
            "    // GEN-BEGIN\n"
            "    register_scene__main(p_scene_manager);\n"
            "    // GEN-END\n"
            "}\n"
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = gen_scene("Main_Menu")
        assert "generated successfully" in result

        header = (tmp_path / "include" / "scene" / "implemented" / "scene__main_menu.h").read_text()
        assert "register_scene__main_menu" in header
        assert "register_scene__main_menu_menu" not in header

        source = (tmp_path / "source" / "scene" / "implemented" / "scene__main_menu.c").read_text()
        assert "register_scene__main_menu" in source
        assert "register_scene__main_menu_menu" not in source
        # Scene_Kind must preserve multi-word PascalCase
        assert "Scene_Kind__Main_Menu" in source
        assert "Scene_Kind__Main_menu" not in source


# ===========================================================================
# Platform gate guard tests
# ===========================================================================

class TestPlatformGateGuard:
    """Test _validate_platform via the build() tool function."""

    @staticmethod
    def _mock_lavender_config(config_json: str | None):
        """Create a mock Path.cwd() that simulates .lavender/lavender.json.

        When *config_json* is a string, the config file "exists" and returns
        that content.  When None, the config file does not exist.
        """
        config_file_mock = MagicMock(
            exists=MagicMock(return_value=config_json is not None),
        )
        if config_json is not None:
            config_file_mock.read_text = MagicMock(return_value=config_json)
        # CWD / ".lavender" / "lavender.json"
        dotlavender_mock = MagicMock()
        dotlavender_mock.__truediv__ = MagicMock(return_value=config_file_mock)
        cwd_mock = MagicMock()
        cwd_mock.__truediv__ = MagicMock(return_value=dotlavender_mock)
        return cwd_mock

    def test_allowed_platform_proceeds(self):
        """When .lavender/lavender.json allows 'sdl', build('sdl') should proceed."""
        proc = _make_completed_process(stdout="ok\n")
        cwd_mock = self._mock_lavender_config('{"platforms": ["sdl"]}')
        with _patch_run_build(proc) as mock_run, \
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=cwd_mock):
            result = build("sdl")
        mock_run.assert_called_once()
        assert "ok" in result

    def test_disallowed_platform_blocked(self):
        """When .lavender/lavender.json allows only 'sdl', build('nds') should return error."""
        proc = _make_completed_process(stdout="ok\n")
        cwd_mock = self._mock_lavender_config('{"platforms": ["sdl"]}')
        with _patch_run_build(proc) as mock_run, \
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=cwd_mock):
            result = build("nds")
        mock_run.assert_not_called()
        assert "ERROR" in result
        assert "nds" in result
        assert "platforms whitelist" in result

    def test_no_config_file_allows_all(self):
        """When .lavender/lavender.json doesn't exist, all platforms are allowed."""
        proc = _make_completed_process(stdout="ok\n")
        cwd_mock = self._mock_lavender_config(None)
        with _patch_run_build(proc) as mock_run, \
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=cwd_mock):
            result = build("nds")
        mock_run.assert_called_once()

    def test_case_insensitive_matching(self):
        """Platform check should be case-insensitive (SDL vs sdl)."""
        proc = _make_completed_process(stdout="ok\n")
        cwd_mock = self._mock_lavender_config('{"platforms": ["sdl"]}')
        with _patch_run_build(proc) as mock_run, \
             patch("lavender_tools.lav_ai.lav_ai_app.Path.cwd", return_value=cwd_mock):
            result = build("SDL")
        mock_run.assert_called_once()


# ===========================================================================
# Tool 26 – gen_lav_project
# ===========================================================================

class TestGenLavProject:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_lav_project("sdl")
        cmd = mock_run.call_args[0][0]
        assert "tools/lavender_tools/gen_lav_project.py" in cmd[1]
        assert "--platforms" in cmd
        assert "sdl" in cmd

    def test_multiple_platforms(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_lav_project("sdl,nds")
        cmd = mock_run.call_args[0][0]
        assert "sdl,nds" in cmd

    def test_returns_stdout_on_success(self):
        proc = _make_completed_process(stdout="Project 'MyGame' initialized successfully.\n")
        with _patch_run(proc):
            result = gen_lav_project("sdl")
        assert "initialized successfully" in result

    def test_error_prefix_on_nonzero_exit(self):
        proc = _make_completed_process(stdout="", stderr="Error: already initialized\n", returncode=1)
        with _patch_run(proc):
            result = gen_lav_project("sdl")
        assert result.startswith("ERROR (exit 1):")

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_lav_project("sdl")
        assert mock_run.call_args[1].get("cwd") is None


# ===========================================================================
# clangd tools (Tools 27-31)
# ===========================================================================

def _mock_clangd_session():
    """Create a mock ClangdSession for testing clangd tool wrappers."""
    session = MagicMock()
    session.ensure_ready.return_value = None
    return session


def _patch_clangd_session(session):
    """Patch the module-level _clangd_session in lav_ai_app."""
    return patch("lavender_tools.lav_ai.lav_ai_app._clangd_session", session)


class TestClangdDefinition:
    def test_returns_result_from_find_definition(self):
        session = _mock_clangd_session()
        with _patch_clangd_session(session), \
             patch("lavender_tools.clang_tools.find_definition",
                   return_value="/some/file.c:10:5") as mock_fn:
            result = clangd_definition("test.c", 1, 1)
        assert result == "/some/file.c:10:5"
        mock_fn.assert_called_once_with(session, "test.c", 1, 1)

    def test_no_session_returns_error(self):
        with _patch_clangd_session(None), \
             patch("lavender_tools.lav_ai.lav_ai_app._get_clangd_session",
                   return_value=None):
            result = clangd_definition("test.c", 1, 1)
        assert "ERROR" in result
        assert "clangd not configured" in result

    def test_exception_returns_error(self):
        session = _mock_clangd_session()
        session.ensure_ready.side_effect = RuntimeError("clangd crashed")
        with _patch_clangd_session(session):
            result = clangd_definition("test.c", 1, 1)
        assert result.startswith("ERROR:")


class TestClangdReferences:
    def test_returns_result_from_find_references(self):
        session = _mock_clangd_session()
        with _patch_clangd_session(session), \
             patch("lavender_tools.clang_tools.find_references",
                   return_value="a.c:1:1\nb.c:2:1") as mock_fn:
            result = clangd_references("test.c", 5, 3)
        assert result == "a.c:1:1\nb.c:2:1"
        mock_fn.assert_called_once_with(session, "test.c", 5, 3)

    def test_no_session_returns_error(self):
        with _patch_clangd_session(None), \
             patch("lavender_tools.lav_ai.lav_ai_app._get_clangd_session",
                   return_value=None):
            result = clangd_references("test.c", 1, 1)
        assert "ERROR" in result


class TestClangdSymbols:
    def test_returns_result_from_get_symbols(self):
        session = _mock_clangd_session()
        with _patch_clangd_session(session), \
             patch("lavender_tools.clang_tools.get_symbols",
                   return_value="Function main test.c:1:1") as mock_fn:
            result = clangd_symbols("test.c")
        assert result == "Function main test.c:1:1"
        mock_fn.assert_called_once_with(session, "test.c")

    def test_no_session_returns_error(self):
        with _patch_clangd_session(None), \
             patch("lavender_tools.lav_ai.lav_ai_app._get_clangd_session",
                   return_value=None):
            result = clangd_symbols("test.c")
        assert "ERROR" in result


class TestClangdWorkspaceSymbol:
    def test_returns_result_from_search(self):
        session = _mock_clangd_session()
        with _patch_clangd_session(session), \
             patch("lavender_tools.clang_tools.search_workspace_symbols",
                   return_value="Function foo bar.c:10:1") as mock_fn:
            result = clangd_workspace_symbol("foo")
        assert result == "Function foo bar.c:10:1"
        mock_fn.assert_called_once_with(session, "foo")

    def test_no_session_returns_error(self):
        with _patch_clangd_session(None), \
             patch("lavender_tools.lav_ai.lav_ai_app._get_clangd_session",
                   return_value=None):
            result = clangd_workspace_symbol("foo")
        assert "ERROR" in result


class TestClangdHover:
    def test_returns_result_from_get_hover(self):
        session = _mock_clangd_session()
        with _patch_clangd_session(session), \
             patch("lavender_tools.clang_tools.get_hover_info",
                   return_value="void foo(int x)") as mock_fn:
            result = clangd_hover("test.c", 3, 5)
        assert result == "void foo(int x)"
        mock_fn.assert_called_once_with(session, "test.c", 3, 5)

    def test_no_session_returns_error(self):
        with _patch_clangd_session(None), \
             patch("lavender_tools.lav_ai.lav_ai_app._get_clangd_session",
                   return_value=None):
            result = clangd_hover("test.c", 1, 1)
        assert "ERROR" in result

class TestScanUiMcp:
    def test_returns_json_on_success(self):
        mock_result = {"tool": "scan_ui", "summary": {"total_checked": 1, "passed": 1, "warnings": 0, "errors": 0}, "results": []}
        with patch("lavender_tools.scan_ui.run", return_value=mock_result):
            result = scan_ui()
        parsed = json.loads(result)
        assert parsed["tool"] == "scan_ui"

    def test_default_project_root_uses_cwd(self):
        mock_result = {"tool": "scan_ui", "summary": {}, "results": [], "project_root": "/test"}
        with patch("lavender_tools.scan_ui.run", return_value=mock_result) as mock_run:
            scan_ui()
        call_args = mock_run.call_args[0]
        assert len(call_args[0]) > 0

    def test_exception_returns_error(self):
        with patch("lavender_tools.scan_ui.run", side_effect=RuntimeError("boom")):
            result = scan_ui()
        assert result.startswith("ERROR:")


class TestScanEntityMcp:
    def test_returns_json_on_success(self):
        mock_result = {"tool": "scan_entity", "summary": {"total_checked": 1, "passed": 1, "warnings": 0, "errors": 0}, "results": []}
        with patch("lavender_tools.scan_entity.run", return_value=mock_result):
            result = scan_entity()
        parsed = json.loads(result)
        assert parsed["tool"] == "scan_entity"

    def test_default_project_root_uses_cwd(self):
        mock_result = {"tool": "scan_entity", "summary": {}, "results": [], "project_root": "/test"}
        with patch("lavender_tools.scan_entity.run", return_value=mock_result) as mock_run:
            scan_entity()
        call_args = mock_run.call_args[0]
        assert len(call_args[0]) > 0

    def test_exception_returns_error(self):
        with patch("lavender_tools.scan_entity.run", side_effect=RuntimeError("boom")):
            result = scan_entity()
        assert result.startswith("ERROR:")


class TestScanSceneMcp:
    def test_returns_json_on_success(self):
        mock_result = {"tool": "scan_scene", "summary": {"total_checked": 1, "passed": 1, "warnings": 0, "errors": 0}, "results": []}
        with patch("lavender_tools.scan_scene.run", return_value=mock_result):
            result = scan_scene()
        parsed = json.loads(result)
        assert parsed["tool"] == "scan_scene"

    def test_default_project_root_uses_cwd(self):
        mock_result = {"tool": "scan_scene", "summary": {}, "results": [], "project_root": "/test"}
        with patch("lavender_tools.scan_scene.run", return_value=mock_result) as mock_run:
            scan_scene()
        call_args = mock_run.call_args[0]
        assert len(call_args[0]) > 0

    def test_exception_returns_error(self):
        with patch("lavender_tools.scan_scene.run", side_effect=RuntimeError("boom")):
            result = scan_scene()
        assert result.startswith("ERROR:")


class TestScanTexturesMcp:
    def test_returns_json_on_success(self):
        mock_result = {"tool": "scan_textures", "summary": {"total_checked": 1, "passed": 1, "warnings": 0, "errors": 0}, "results": []}
        with patch("lavender_tools.scan_textures.run", return_value=mock_result):
            result = scan_textures()
        parsed = json.loads(result)
        assert parsed["tool"] == "scan_textures"

    def test_default_project_root_uses_cwd(self):
        mock_result = {"tool": "scan_textures", "summary": {}, "results": [], "project_root": "/test"}
        with patch("lavender_tools.scan_textures.run", return_value=mock_result) as mock_run:
            scan_textures()
        call_args = mock_run.call_args[0]
        assert len(call_args[0]) > 0

    def test_exception_returns_error(self):
        with patch("lavender_tools.scan_textures.run", side_effect=RuntimeError("boom")):
            result = scan_textures()
        assert result.startswith("ERROR:")


class TestScanGameActionsMcp:
    def test_returns_json_on_success(self):
        mock_result = {"tool": "scan_game_actions", "summary": {"total_checked": 1, "passed": 1, "warnings": 0, "errors": 0}, "results": []}
        with patch("lavender_tools.scan_game_actions.run", return_value=mock_result):
            result = scan_game_actions()
        parsed = json.loads(result)
        assert parsed["tool"] == "scan_game_actions"

    def test_default_project_root_uses_cwd(self):
        mock_result = {"tool": "scan_game_actions", "summary": {}, "results": [], "project_root": "/test"}
        with patch("lavender_tools.scan_game_actions.run", return_value=mock_result) as mock_run:
            scan_game_actions()
        call_args = mock_run.call_args[0]
        assert len(call_args[0]) > 0

    def test_exception_returns_error(self):
        with patch("lavender_tools.scan_game_actions.run", side_effect=RuntimeError("boom")):
            result = scan_game_actions()
        assert result.startswith("ERROR:")


# ---------------------------------------------------------------------------
# gen_window
# ---------------------------------------------------------------------------

class TestGenWindow:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_window.py") in cmd
        assert "--name" in cmd
        assert "MyWindow" in cmd
        assert "--ui" not in cmd

    def test_ui_flag(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow", ui=True)
        cmd = mock_run.call_args[0][0]
        assert "--ui" in cmd

    def test_load_func(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow", ui=True, load_func="custom_load")
        cmd = mock_run.call_args[0][0]
        assert "--load-func" in cmd
        assert "custom_load" in cmd

    def test_close_func(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow", ui=True, close_func="custom_close")
        cmd = mock_run.call_args[0][0]
        assert "--close-func" in cmd
        assert "custom_close" in cmd

    def test_sprites(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow", sprites=8)
        cmd = mock_run.call_args[0][0]
        assert "--sprites" in cmd
        assert "8" in cmd

    def test_ui_elements(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow", ui_elements=32)
        cmd = mock_run.call_args[0][0]
        assert "--ui-elements" in cmd
        assert "32" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_window("MyWindow")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_success_returns_stdout(self):
        proc = _make_completed_process(stdout="window registered\n")
        with _patch_run(proc):
            result = gen_window("MyWindow")
        assert "window registered" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="fail\n")
        with _patch_run(proc):
            result = gen_window("MyWindow")
        assert result.startswith("ERROR (exit 1):")
        assert "fail" in result


# ---------------------------------------------------------------------------
# gen_chunk_generator
# ---------------------------------------------------------------------------

class TestGenChunkGenerator:
    def test_basic_command(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_chunk_generator("Overworld")
        cmd = mock_run.call_args[0][0]
        assert str(PROJECT_ROOT / "tools" / "lavender_tools" / "gen_chunk_generator.py") in cmd
        assert "--name" in cmd
        assert "Overworld" in cmd

    def test_no_cwd(self):
        proc = _make_completed_process()
        with _patch_run(proc) as mock_run:
            gen_chunk_generator("Overworld")
        assert "cwd" not in mock_run.call_args.kwargs

    def test_success_returns_stdout(self):
        proc = _make_completed_process(stdout="generator registered\n")
        with _patch_run(proc):
            result = gen_chunk_generator("Overworld")
        assert "generator registered" in result

    def test_error_on_nonzero(self):
        proc = _make_completed_process(returncode=1, stderr="fail\n")
        with _patch_run(proc):
            result = gen_chunk_generator("Overworld")
        assert result.startswith("ERROR (exit 1):")
        assert "fail" in result


# ---------------------------------------------------------------------------
# mod_scene
# ---------------------------------------------------------------------------

class TestModScene:
    @staticmethod
    def _make_scene_file(tmp_path: Path) -> Path:
        scene_dir = tmp_path / "source" / "scene" / "implemented"
        scene_dir.mkdir(parents=True)
        scene_file = scene_dir / "scene__test.c"
        scene_file.write_text(
            '// GEN-INCLUDE-BEGIN\n'
            '// GEN-INCLUDE-END\n'
            '\n'
            '// GEN-FORWARD-BEGIN\n'
            '// GEN-FORWARD-END\n'
            '\n'
            '// GEN-LOAD-BEGIN\n'
            '// GEN-LOAD-END\n'
            '\n'
            '// GEN-FRAME-BEGIN\n'
            '// GEN-FRAME-END\n'
            '\n'
            '// GEN-UNLOAD-BEGIN\n'
            '// GEN-UNLOAD-END\n'
        )
        return scene_file

    def test_register_chunk_generator_includes_header(self, tmp_path, monkeypatch):
        scene_file = self._make_scene_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_scene("Test", register_chunk_generator="register_chunk_generators")
        assert "updated" in result

        content = scene_file.read_text()
        assert '#include "world/implemented/chunk_generator_registrar.h"' in content

    def test_register_entity_initializer_includes_header(self, tmp_path, monkeypatch):
        scene_file = self._make_scene_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_scene("Test", register_entity_initializer="set_entity_initializer_in__entity_manager")
        assert "updated" in result

        content = scene_file.read_text()
        assert '#include "entity/entity_manager.h"' in content

    def test_register_tile_logic_includes_header(self, tmp_path, monkeypatch):
        scene_file = self._make_scene_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_scene("Test", register_tile_logic="register_tile_logic_tables")
        assert "updated" in result

        content = scene_file.read_text()
        assert '#include "world/implemented/tile_logic_table_registrar.h"' in content
        assert '#include "world/world.h"' in content

    def test_multiple_registrations_include_all_headers(self, tmp_path, monkeypatch):
        scene_file = self._make_scene_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_scene(
            "Test",
            register_chunk_generator="register_chunk_generators",
            register_entity_initializer="set_entity_initializer_in__entity_manager",
            register_tile_logic="register_tile_logic_tables",
        )
        assert "updated" in result

        content = scene_file.read_text()
        assert '#include "world/implemented/chunk_generator_registrar.h"' in content
        assert '#include "entity/entity_manager.h"' in content
        assert '#include "world/implemented/tile_logic_table_registrar.h"' in content


# ---------------------------------------------------------------------------
# mod_entity
# ---------------------------------------------------------------------------

class TestModEntity:
    @staticmethod
    def _make_entity_file(tmp_path: Path) -> Path:
        entity_dir = tmp_path / "source" / "entity" / "implemented"
        entity_dir.mkdir(parents=True)
        entity_file = entity_dir / "player.c"
        entity_file.write_text(
            '// GEN-INCLUDE-BEGIN\n'
            '// GEN-INCLUDE-END\n'
            '\n'
            '// GEN-BEGIN-BEGIN\n'
            '// GEN-BEGIN-END\n'
            '\n'
            'void m_entity_handler__update__player(\n'
            '        Entity *p_entity,\n'
            '        Game *p_game,\n'
            '        World *p_world) {\n'
            '    // player logic\n'
            '}\n'
        )
        return entity_file

    def test_sprite_wiring_includes_correct_headers(self, tmp_path, monkeypatch):
        entity_file = self._make_entity_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_entity(
            "Player",
            sprite_kind="Player_Knight",
            texture_alias="player_knight",
            animation_group="Player_Knight",
            texture_size="16x16",
        )
        assert "updated" in result

        content = entity_file.read_text()
        assert '#include "rendering/aliased_texture_manager.h"' in content
        assert '#include "rendering/sprite.h"' in content
        assert '#include "rendering/sprite_manager.h"' in content
        assert '#include "world/world.h"' in content
        assert '#include "rendering/graphics_window.h"' in content
        assert "allocate_sprite_from__sprite_manager" in content
        assert "Sprite_Kind__Player_Knight" in content
        assert "Sprite_Animation_Group_Kind__Player_Knight" in content
        assert "TEXTURE_FLAG__SIZE_16x16" in content
        assert "get_texture_by__alias" in content

    def test_hitbox_wiring_includes_correct_headers(self, tmp_path, monkeypatch):
        entity_file = self._make_entity_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_entity(
            "Player",
            hitbox_size="16x16",
        )
        assert "updated" in result

        content = entity_file.read_text()
        assert '#include "collisions/hitbox_context.h"' in content
        assert '#include "collisions/core/aabb/hitbox_aabb_manager.h"' in content
        assert '#include "collisions/core/aabb/hitbox_aabb.h"' in content
        assert '#include "world/world.h"' in content
        assert "allocate_hitbox_aabb_from__hitbox_aabb_manager" in content
        assert "set_size_of__hitbox_aabb" in content
        assert "GET_UUID_P(p_entity)" in content
        assert "GET_UUID_P(get_p_world_from__game(p_game))" in content

    def test_update_handler_replacement(self, tmp_path, monkeypatch):
        entity_file = self._make_entity_file(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("LAVENDER_DIR", str(PROJECT_ROOT))
        monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "tools"))

        result = mod_entity(
            "Player",
            update_handler="m_entity_handler__update__player",
        )
        assert "updated" in result

        content = entity_file.read_text()
        assert "m_entity_handler__update__player" in content
        assert "p_entity->entity_functions.m_entity_update_handler =" in content


# ---------------------------------------------------------------------------
# build (command construction)
# ---------------------------------------------------------------------------

class TestBuildCommandConstruction:
    def test_build_invokes_build_py_with_equals_flags(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build(platform="sdl", flags="-w")
        cmd = mock_run.call_args[0][0]
        assert f"--flags=-w" in cmd
        # Ensure it is NOT split into two tokens
        assert "--flags" not in cmd

    def test_build_passes_game_dir_when_provided(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build(platform="sdl", game_dir="/some/game")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" in cmd
        assert "/some/game" in cmd

    def test_build_omits_clean_when_false(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build(platform="sdl", clean=False)
        cmd = mock_run.call_args[0][0]
        assert "--clean" not in cmd

    def test_build_includes_clean_when_true(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build(platform="sdl", clean=True)
        cmd = mock_run.call_args[0][0]
        assert "--clean" in cmd

    def test_build_omits_game_dir_when_empty(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build(platform="sdl")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" not in cmd


# ---------------------------------------------------------------------------
# build_spot_check (command construction)
# ---------------------------------------------------------------------------

class TestBuildSpotCheckCommandConstruction:
    def test_build_spot_check_invokes_build_py_with_equals_flags(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check(platform="sdl", file="test.c", flags="-w")
        cmd = mock_run.call_args[0][0]
        assert f"--flags=-w" in cmd
        # Ensure it is NOT split into two tokens
        assert "--flags" not in cmd

    def test_build_spot_check_passes_game_dir_when_provided(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check(platform="sdl", file="test.c", game_dir="/some/game")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" in cmd
        assert "/some/game" in cmd

    def test_build_spot_check_passes_file(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check(platform="sdl", file="core/source/test.c")
        cmd = mock_run.call_args[0][0]
        assert "--file" in cmd
        assert "core/source/test.c" in cmd

    def test_build_spot_check_omits_game_dir_when_empty(self):
        proc = _make_completed_process()
        with _patch_run_build(proc) as mock_run:
            build_spot_check(platform="sdl", file="test.c")
        cmd = mock_run.call_args[0][0]
        assert "--game-dir" not in cmd
