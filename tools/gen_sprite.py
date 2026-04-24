#!/usr/bin/env python3
"""
gen_sprite.py – code-generator for Lavender sprite / animation / animation-group
boilerplate.

Run from the root of a Lavender *project* directory (the one that contains
./include and ./source).
"""

import argparse
import re
import sys
import os

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def validate_name(name: str) -> str:
    """Ensure *name* starts with [a-zA-Z] and the rest is [a-zA-Z0-9_]."""
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
        print(f"error: invalid --name '{name}'. "
              "Must start with a letter and contain only "
              "alphanumeric characters or underscores.",
              file=sys.stderr)
        sys.exit(1)
    return name


def read_file(path: str) -> str:
    if not os.path.isfile(path):
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r') as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)


def insert_between_markers(text: str,
                           begin_marker: str,
                           end_marker: str,
                           new_line: str,
                           *,
                           duplicate_check: str | None = None) -> str:
    """Insert *new_line* just before *end_marker* inside *text*.

    If *duplicate_check* is given and already appears between the markers the
    text is returned unchanged.
    """
    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)
    if begin_idx == -1 or end_idx == -1:
        print(f"error: could not find markers "
              f"'{begin_marker}' / '{end_marker}'",
              file=sys.stderr)
        sys.exit(1)

    region = text[begin_idx:end_idx]
    if duplicate_check and duplicate_check in region:
        return text  # already present

    # Find the position right before the end marker line
    insert_pos = end_idx
    # Walk back over any blank lines / whitespace so we insert after the last
    # real entry but keep a blank line before the end marker.
    return text[:insert_pos] + new_line + "\n" + text[insert_pos:]


# ---------------------------------------------------------------------------
# Sub-command: sprite
# ---------------------------------------------------------------------------

SPRITE_KIND_PATH = os.path.join(
    "include", "types", "implemented", "rendering", "sprite_kind.h")


def cmd_sprite(args):
    name = validate_name(args.name)
    enum_entry = f"Sprite_Kind__{name}"

    content = read_file(SPRITE_KIND_PATH)
    content = insert_between_markers(
        content,
        "// GEN-BEGIN",
        "// GEN-END",
        f"    {enum_entry},",
        duplicate_check=enum_entry,
    )
    write_file(SPRITE_KIND_PATH, content)
    print(f"sprite: ensured {enum_entry} in {SPRITE_KIND_PATH}")


# ---------------------------------------------------------------------------
# Sub-command: animation
# ---------------------------------------------------------------------------

SPRITE_ANIMATION_KIND_PATH = os.path.join(
    "include", "types", "implemented", "rendering",
    "sprite_animation_kind.h")

SPRITE_ANIMATION_REGISTRAR_PATH = os.path.join(
    "source", "rendering", "implemented",
    "sprite_animation_registrar.c")


def cmd_animation(args):
    name = validate_name(args.name)
    group = validate_name(args.group)
    init_frame = args.init_frame
    qty_frames = args.quantity_of_frames
    ticks = args.ticks_per_frame
    flags = args.flags

    enum_entry = f"Sprite_Animation_Kind__{name}"

    # --- 1. Update sprite_animation_kind.h ---
    content = read_file(SPRITE_ANIMATION_KIND_PATH)
    content = insert_between_markers(
        content,
        "// GEN-BEGIN",
        "// GEN-END",
        f"    {enum_entry},",
        duplicate_check=enum_entry,
    )
    write_file(SPRITE_ANIMATION_KIND_PATH, content)
    print(f"animation: ensured {enum_entry} in {SPRITE_ANIMATION_KIND_PATH}")

    # --- 2. Update sprite_animation_registrar.c ---
    reg_content = read_file(SPRITE_ANIMATION_REGISTRAR_PATH)

    # Variable name: lower-case group + lower-case anim portion
    var_group = group.lower()
    var_anim = name.lower()
    var_name = f"sprite_animation__{var_group}__{var_anim}"

    # 2a. Add Sprite_Animation variable in GEN-ANIMATIONS
    animation_block = (
        f"Sprite_Animation {var_name} = {{\n"
        f"    {enum_entry},\n"
        f"    (Timer__u8){{0,8}},\n"
        f"    {init_frame}, // init frame on row\n"
        f"    {qty_frames}, // quantity of frames\n"
        f"    {ticks}, // ticks per frame\n"
        f"    {flags}\n"
        f"}};\n"
    )
    reg_content = insert_between_markers(
        reg_content,
        "// GEN-ANIMATIONS-BEGIN",
        "// GEN-ANIMATIONS-END",
        "\n" + animation_block,
        duplicate_check=var_name,
    )

    # 2b. Add registration call in GEN-REGISTER-ANIMATIONS
    register_call = (
        f"    register_sprite_animation_into__sprite_context(\n"
        f"            p_sprite_context, \n"
        f"            {enum_entry}, \n"
        f"            {var_name});\n"
    )
    reg_content = insert_between_markers(
        reg_content,
        "//GEN-REGISTER-ANIMATIONS-BEGIN",
        "//GEN-REGISTER-ANIMATIONS-END",
        "\n" + register_call,
        duplicate_check=enum_entry,
    )

    write_file(SPRITE_ANIMATION_REGISTRAR_PATH, reg_content)
    print(f"animation: updated {SPRITE_ANIMATION_REGISTRAR_PATH}")


# ---------------------------------------------------------------------------
# Sub-command: animation-group
# ---------------------------------------------------------------------------

SPRITE_ANIMATION_GROUP_KIND_PATH = os.path.join(
    "include", "types", "implemented", "rendering",
    "sprite_animation_group_kind.h")


def cmd_animation_group(args):
    name = validate_name(args.name)
    cols = args.quantity_of_columns
    rows = args.quantity_of_rows
    num_anims = args.number_of_animations

    enum_entry = f"Sprite_Animation_Group_Kind__{name}"

    # --- 1. Update sprite_animation_group_kind.h ---
    content = read_file(SPRITE_ANIMATION_GROUP_KIND_PATH)
    content = insert_between_markers(
        content,
        "// GEN-BEGIN",
        "// GEN-END",
        f"    {enum_entry},",
        duplicate_check=enum_entry,
    )
    write_file(SPRITE_ANIMATION_GROUP_KIND_PATH, content)
    print(f"animation-group: ensured {enum_entry} "
          f"in {SPRITE_ANIMATION_GROUP_KIND_PATH}")

    # --- 2. Update sprite_animation_registrar.c ---
    reg_content = read_file(SPRITE_ANIMATION_REGISTRAR_PATH)

    var_name = f"sprite_animation_group__{name.lower()}"

    # 2a. Add Sprite_Animation_Group_Set variable in GEN-GROUPS
    group_block = (
        f"Sprite_Animation_Group_Set {var_name} = {{\n"
        f"    {cols}, // columns in group\n"
        f"    {rows}, // rows in group\n"
        f"    {num_anims} // number of sub groups\n"
        f"}};\n"
    )
    reg_content = insert_between_markers(
        reg_content,
        "// GEN-GROUPS-BEGIN",
        "// GEN-GROUPS-END",
        "\n" + group_block,
        duplicate_check=var_name,
    )

    # 2b. Add registration call in GEN-REGISTER-GROUPS
    register_call = (
        f"    register_sprite_animation_group_into__sprite_context(\n"
        f"            p_sprite_context, \n"
        f"            {enum_entry}, \n"
        f"            {var_name});\n"
    )
    reg_content = insert_between_markers(
        reg_content,
        "//GEN-REGISTER-GROUPS-BEGIN",
        "//GEN-REGISTER-GROUPS-END",
        "\n" + register_call,
        duplicate_check=enum_entry,
    )

    write_file(SPRITE_ANIMATION_REGISTRAR_PATH, reg_content)
    print(f"animation-group: updated {SPRITE_ANIMATION_REGISTRAR_PATH}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate sprite / animation / animation-group "
                    "boilerplate for a Lavender project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- sprite --
    sp_sprite = subparsers.add_parser(
        "sprite", help="Add a Sprite_Kind entry.")
    sp_sprite.add_argument("--name", required=True,
                           help="PascalCase name (e.g. Player)")
    sp_sprite.set_defaults(func=cmd_sprite)

    # -- animation --
    sp_anim = subparsers.add_parser(
        "animation", help="Add a Sprite_Animation_Kind entry and "
                          "registrar code.")
    sp_anim.add_argument("--name", required=True,
                         help="Animation name (e.g. Humanoid_Walk)")
    sp_anim.add_argument("--group", required=True,
                         help="Group name this animation belongs to "
                              "(e.g. Humanoid)")
    sp_anim.add_argument("--init-frame", required=True, type=int,
                         help="Initial frame on row")
    sp_anim.add_argument("--quantity-of-frames", required=True, type=int,
                         help="Number of frames in the animation")
    sp_anim.add_argument("--ticks-per-frame", required=True, type=int,
                         help="Ticks per frame")
    sp_anim.add_argument("--flags", required=True,
                         help="Sprite animation flags constant "
                              "(e.g. SPRITE_ANIMATION_FLAGS__NONE)")
    sp_anim.set_defaults(func=cmd_animation)

    # -- animation-group --
    sp_group = subparsers.add_parser(
        "animation-group",
        help="Add a Sprite_Animation_Group_Kind entry and registrar code.")
    sp_group.add_argument("--name", required=True,
                          help="Group name (e.g. Humanoid)")
    sp_group.add_argument("--quantity-of-columns", required=True, type=int,
                          help="Columns in the group")
    sp_group.add_argument("--quantity-of-rows", required=True, type=int,
                          help="Rows in the group")
    sp_group.add_argument("--number-of-animations", required=True, type=int,
                          help="Number of sub-groups / animations")
    sp_group.set_defaults(func=cmd_animation_group)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
