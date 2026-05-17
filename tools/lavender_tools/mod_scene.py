#!/usr/bin/env python3
"""mod_scene.py — Wire resource lifecycle boilerplate into scene GEN markers.

Usage:
    python tools/lavender_tools/mod_scene.py --scene <Name> [options...]

Injects deterministic boilerplate (UI window open/close, texture registration,
world setup, etc.) into existing scene ``GEN-*-BEGIN/END`` marker regions.
All injections are idempotent — running the same command twice produces the
same result.

**Prerequisite**: The scene must already exist (created by ``gen_scene.py``).
UI windows must be registered (via ``gen_window.py --ui``).

**Out of scope**: World serialization/deserialization (load_world, load_client,
save_client).  That is handled by separate future tooling.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Optional, Set

from lavender_tools import tool_history


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

_SCENE_SOURCE_REL = "source/scene/implemented/scene__{name_lower}.c"

# GEN marker names used in scene source files
_GEN_INCLUDE = "GEN-INCLUDE"
_GEN_FORWARD = "GEN-FORWARD"
_GEN_LOAD = "GEN-LOAD"
_GEN_FRAME = "GEN-FRAME"
_GEN_UNLOAD = "GEN-UNLOAD"


# ---------------------------------------------------------------------------
# GEN marker manipulation (append with dedup)
# ---------------------------------------------------------------------------

def _find_gen_block(content: str, marker_name: str) -> tuple[int, int] | None:
    """Return (begin_end_of_line, end_start_of_line) for a GEN block.

    Returns None if markers are not found.
    """
    begin_tag = f"// {marker_name}-BEGIN"
    end_tag = f"// {marker_name}-END"

    begin_idx = content.find(begin_tag)
    if begin_idx == -1:
        return None
    # Move past the newline after BEGIN
    after_begin = content.find("\n", begin_idx)
    if after_begin == -1:
        return None
    after_begin += 1

    end_idx = content.find(end_tag, after_begin)
    if end_idx == -1:
        return None

    return (after_begin, end_idx)


def _get_gen_block_content(content: str, marker_name: str) -> str:
    """Return the text between GEN-X-BEGIN and GEN-X-END."""
    bounds = _find_gen_block(content, marker_name)
    if bounds is None:
        return ""
    return content[bounds[0]:bounds[1]]


def _append_to_gen_marker(
    content: str,
    marker_name: str,
    new_lines: str,
    *,
    dedup_key: str = "",
) -> str:
    """Append *new_lines* to a GEN marker block, with duplicate checking.

    If *dedup_key* is non-empty, the insertion is skipped when *dedup_key*
    already appears in the block.  Otherwise *new_lines* itself is used as
    the dedup key.

    Returns the (possibly modified) content.
    """
    bounds = _find_gen_block(content, marker_name)
    if bounds is None:
        print(f"  [skip] {marker_name}-BEGIN/END markers not found.")
        return content

    existing = content[bounds[0]:bounds[1]]
    key = dedup_key or new_lines.strip()
    if key in existing:
        print(f"  [skip] already present in {marker_name}: {key[:60]}...")
        return content

    # Ensure new_lines ends with newline
    insert = new_lines if new_lines.endswith("\n") else new_lines + "\n"

    # Insert just before the END marker
    content = content[:bounds[1]] + insert + content[bounds[1]:]
    return content


# ---------------------------------------------------------------------------
# Include injection
# ---------------------------------------------------------------------------

_INCLUDE_MAP: dict[str, list[str]] = {
    "open_ui_window": [
        "ui/ui_context.h",
    ],
    "register_ui_windows": [
        "ui/implemented/ui_window_registrar.h",
    ],
    "register_aliased_textures": [
        "rendering/implemented/aliased_texture_registrar.h",
    ],
    "register_chunk_generator": [
        "world/implemented/chunk_generator_registrar.h",
    ],
    "register_entity_initializer": [
        "entity/entity_manager.h",
    ],
    "register_tile_logic": [
        "world/implemented/tile_logic_table_registrar.h",
        "world/world.h",
    ],
    "world": [
        "world/world.h",
    ],
}


def _inject_include(content: str, header: str) -> str:
    """Add a #include to the GEN-INCLUDE block if not already present."""
    include_line = f'#include "{header}"'
    if include_line in content:
        return content
    return _append_to_gen_marker(
        content, _GEN_INCLUDE, include_line,
        dedup_key=include_line,
    )


def _inject_includes_for(content: str, category: str) -> str:
    """Inject all includes for a given category."""
    headers = _INCLUDE_MAP.get(category, [])
    for h in headers:
        content = _inject_include(content, h)
    return content


# ---------------------------------------------------------------------------
# Variable name derivation
# ---------------------------------------------------------------------------

def _window_var_name(kind: str) -> str:
    """Derive a static variable name from a window kind.

    E.g. 'Game__Hud' -> '_p_gfx_window__ui__game__hud'
    """
    return f"_p_gfx_window__ui__{kind.lower()}"


# ---------------------------------------------------------------------------
# Code generation: UI window open/close
# ---------------------------------------------------------------------------

def _gen_open_ui_window(
    content: str,
    kind: str,
    persist_set: Set[str],
) -> str:
    """Generate open_ui_window in GEN-LOAD, static var in GEN-FORWARD,
    and conditional close in GEN-UNLOAD (unless persisted).
    """
    entry = f"Graphics_Window_Kind__UI__{kind}"
    var = _window_var_name(kind)

    # --- GEN-FORWARD: static variable declaration ---
    forward_line = f"static Graphics_Window *{var} = 0;"
    content = _append_to_gen_marker(
        content, _GEN_FORWARD, forward_line,
        dedup_key=var,
    )

    # --- GEN-LOAD: open_ui_window call ---
    load_line = (
        f"    {var} =\n"
        f"        open_ui_window(p_game, {entry});"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, load_line,
        dedup_key=f"open_ui_window(p_game, {entry})",
    )

    # --- GEN-UNLOAD: close (unless persisted) ---
    if kind not in persist_set:
        unload_line = (
            f"    if ({var}) {{\n"
            f"        close_ui_window(p_game, GET_UUID_P({var}));\n"
            f"        {var} = 0;\n"
            f"    }}"
        )
        content = _append_to_gen_marker(
            content, _GEN_UNLOAD, unload_line,
            dedup_key=f"close_ui_window(p_game, GET_UUID_P({var}))",
        )

    # --- Includes ---
    content = _inject_includes_for(content, "open_ui_window")

    return content


# ---------------------------------------------------------------------------
# Code generation: registration calls
# ---------------------------------------------------------------------------

def _gen_register_ui_windows(content: str) -> str:
    """Generate register_ui_windows() call in GEN-LOAD."""
    call = "    register_ui_windows(\n            get_p_gfx_context_from__game(p_game));"
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key="register_ui_windows(",
    )
    content = _inject_includes_for(content, "register_ui_windows")
    return content


def _gen_register_aliased_textures(content: str, func: str) -> str:
    """Generate a texture registration call in GEN-LOAD."""
    call = (
        f"    {func}(\n"
        f"            get_p_aliased_texture_manager_from__game(p_game),\n"
        f"            p_game);"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key=f"{func}(",
    )
    content = _inject_includes_for(content, "register_aliased_textures")
    return content


# ---------------------------------------------------------------------------
# Code generation: world setup
# ---------------------------------------------------------------------------

def _gen_register_tile_logic(content: str, func: str) -> str:
    call = (
        f"    {func}(p_game,\n"
        f"            get_p_tile_logic_context_from__world(\n"
        f"                get_p_world_from__game(p_game)));"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key=f"{func}(",
    )
    content = _inject_includes_for(content, "register_tile_logic")
    return content


def _gen_register_chunk_generator(content: str, func: str) -> str:
    call = (
        f"    {func}(\n"
        f"            get_p_chunk_generation_table_from__world(\n"
        f"                get_p_world_from__game(p_game)));"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key=f"{func}(",
    )
    content = _inject_includes_for(content, "register_chunk_generator")
    return content


def _gen_register_entity_initializer(content: str, func: str) -> str:
    call = (
        f"    set_entity_initializer_in__entity_manager(\n"
        f"            get_p_entity_manager_from__game(p_game),\n"
        f"            {func});"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key=f"set_entity_initializer_in__entity_manager(",
    )
    content = _inject_includes_for(content, "register_entity_initializer")
    return content


def _gen_allocate_world(content: str) -> str:
    call = (
        "    allocate_world_for__game(p_game);\n"
        "    initialize_world(p_game, get_p_world_from__game(p_game));"
    )
    content = _append_to_gen_marker(
        content, _GEN_LOAD, call,
        dedup_key="allocate_world_for__game(p_game)",
    )
    content = _inject_includes_for(content, "world")
    return content


def _gen_manage_world(content: str) -> str:
    call = "        manage_world(p_game);"
    content = _append_to_gen_marker(
        content, _GEN_FRAME, call,
        dedup_key="manage_world(p_game)",
    )
    content = _inject_includes_for(content, "world")
    return content


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _verify_scene_exists(name_lower: str) -> str | None:
    """Return the scene source path if it exists, else None with error."""
    path = _SCENE_SOURCE_REL.format(name_lower=name_lower)
    if not os.path.isfile(path):
        print(f"ERROR: {path} not found. Run gen_scene.py --name {name_lower.capitalize()} first.")
        return None
    return path


def _verify_ui_windows(kinds: list[str], base_dir: str = "./") -> bool:
    """Verify all UI window kinds exist in the enum."""
    from lavender_tools import gen_window

    ok = True
    for kind in kinds:
        if not gen_window.verify_window_exists(kind, ui=True, base_dir=base_dir):
            ok = False
    return ok


def _validate_name(name: str) -> bool:
    for segment in name.split("__"):
        if not _NAME_RE.match(segment):
            return False
    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mod_scene.py",
        description=(
            "Wire resource lifecycle boilerplate into scene GEN markers."
        ),
    )
    parser.add_argument(
        "--scene", required=True,
        help="Scene name (e.g., 'Main_Menu', 'World').",
    )

    # --- UI wiring ---
    parser.add_argument(
        "--open-ui-window", action="append", default=[], dest="open_ui_windows",
        metavar="KIND",
        help=(
            "Open a UI window in GEN-LOAD and auto-close in GEN-UNLOAD. "
            "Repeatable. E.g., --open-ui-window Game__Hud"
        ),
    )
    parser.add_argument(
        "--persist-ui-window", action="append", default=[], dest="persist_ui_windows",
        metavar="KIND",
        help=(
            "Exempt a window from auto-close in GEN-UNLOAD. "
            "Must also appear in --open-ui-window. Repeatable."
        ),
    )
    parser.add_argument(
        "--call-register-ui-windows", action="store_true", default=False,
        dest="register_ui_windows",
        help="Call register_ui_windows() in GEN-LOAD.",
    )
    parser.add_argument(
        "--call-register-aliased-textures", action="append", default=[],
        dest="register_textures", metavar="FUNC",
        help=(
            "Call a texture registration function in GEN-LOAD. Repeatable. "
            "E.g., --call-register-aliased-textures register_aliased_textures"
        ),
    )

    # --- World wiring ---
    parser.add_argument(
        "--register-tile-logic", default="", metavar="FUNC",
        help="Wire tile logic table registration in GEN-LOAD.",
    )
    parser.add_argument(
        "--register-chunk-generator", default="", metavar="FUNC",
        help="Wire chunk generator registration in GEN-LOAD.",
    )
    parser.add_argument(
        "--register-entity-initializer", default="", metavar="FUNC",
        help="Wire entity initializer in GEN-LOAD.",
    )
    parser.add_argument(
        "--allocate-world", action="store_true", default=False,
        help="Emit allocate_world_for__game + initialize_world in GEN-LOAD.",
    )
    parser.add_argument(
        "--manage-world", action="store_true", default=False,
        help="Emit manage_world(p_game) in GEN-FRAME.",
    )

    args = parser.parse_args()

    # --- Validate scene name ---
    name_lower = args.scene.lower()
    if not _validate_name(args.scene):
        print(f"ERROR: Invalid scene name '{args.scene}'.")
        sys.exit(1)

    # --- Verify scene file exists ---
    scene_path = _verify_scene_exists(name_lower)
    if scene_path is None:
        sys.exit(1)

    # --- Verify persist windows are subset of open windows ---
    persist_set = set(args.persist_ui_windows)
    open_set = set(args.open_ui_windows)
    invalid_persist = persist_set - open_set
    if invalid_persist:
        print(
            f"ERROR: --persist-ui-window {invalid_persist} "
            f"not in --open-ui-window. A window must be opened to be persisted."
        )
        sys.exit(1)

    # --- Verify UI windows exist in enum ---
    if args.open_ui_windows:
        if not _verify_ui_windows(args.open_ui_windows):
            sys.exit(1)

    # --- Read scene file ---
    with open(scene_path, "r") as fh:
        content = fh.read()

    original = content

    # --- Apply modifications ---

    # Registration calls (order matters: textures before windows before UI opens)
    for func in args.register_textures:
        content = _gen_register_aliased_textures(content, func)

    if args.register_ui_windows:
        content = _gen_register_ui_windows(content)

    # World setup
    if args.allocate_world:
        content = _gen_allocate_world(content)

    if args.register_tile_logic:
        content = _gen_register_tile_logic(content, args.register_tile_logic)

    if args.register_chunk_generator:
        content = _gen_register_chunk_generator(content, args.register_chunk_generator)

    if args.register_entity_initializer:
        content = _gen_register_entity_initializer(content, args.register_entity_initializer)

    # UI window open/close
    for kind in args.open_ui_windows:
        content = _gen_open_ui_window(content, kind, persist_set)

    # World frame management
    if args.manage_world:
        content = _gen_manage_world(content)

    # --- Write if changed ---
    if content != original:
        with open(scene_path, "w") as fh:
            fh.write(content)
        tool_history.record_modify(scene_path)
        print(f"  [mod_scene] updated {scene_path}")
    else:
        print(f"  [mod_scene] no changes needed for {scene_path}")

    print("Done.")


if __name__ == "__main__":
    main()
