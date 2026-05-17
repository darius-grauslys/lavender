#!/usr/bin/env python3
"""mod_entity.py — Wire __begin first-frame handler boilerplate into entity files.

Usage:
    python tools/lavender_tools/mod_entity.py --entity <Name> [options]

Injects sprite allocation, texture lookup, hitbox allocation, animation
group binding, and handler replacement code into an existing entity's
``__begin`` update handler.  Not all entities need this — use only for
entities that require first-frame initialization.

The generated code follows the Lavender ``__begin`` pattern: the initial
``m_entity_update_handler`` performs one-time setup, then replaces itself
with the real update handler.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from lavender_tools import tool_history

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

_ENTITY_SOURCE_REL = "source/entity/implemented/{entity_lower}.c"

_GEN_BEGIN_BEGIN = "// GEN-BEGIN-BEGIN"
_GEN_BEGIN_END = "// GEN-BEGIN-END"
_GEN_INCLUDE = "GEN-INCLUDE"


def _find_gen_block(content, begin_tag, end_tag):
    b = content.find(begin_tag)
    if b == -1:
        return None
    after_b = content.find("\n", b)
    if after_b == -1:
        return None
    after_b += 1
    e = content.find(end_tag, after_b)
    if e == -1:
        return None
    return (after_b, e)


def _append_to_block(content, begin_tag, end_tag, new_text, dedup_key):
    bounds = _find_gen_block(content, begin_tag, end_tag)
    if bounds is None:
        print(f"  [skip] {begin_tag}/{end_tag} markers not found.")
        return content
    existing = content[bounds[0]:bounds[1]]
    if dedup_key in existing:
        print(f"  [skip] already present: {dedup_key}")
        return content
    insert = new_text if new_text.endswith("\n") else new_text + "\n"
    return content[:bounds[1]] + insert + content[bounds[1]:]


def _inject_include(content, header):
    include_line = f'#include "{header}"'
    if include_line in content:
        return content
    begin = "// GEN-INCLUDE-BEGIN"
    end = "// GEN-INCLUDE-END"
    bounds = _find_gen_block(content, begin, end)
    if bounds is not None:
        return _append_to_block(content, begin, end, include_line, include_line)
    # Fallback: insert after last #include
    lines = content.split("\n")
    last_inc = -1
    for i, line in enumerate(lines):
        if line.startswith("#include"):
            last_inc = i
    if last_inc >= 0:
        lines.insert(last_inc + 1, include_line)
        return "\n".join(lines)
    return content


def _gen_sprite_wiring(entity_lower, sprite_kind, texture_alias, animation_group, texture_size):
    size_flag = f"TEXTURE_FLAG__SIZE_{texture_size}"
    lines = []
    lines.append(f"    // Sprite allocation for {entity_lower}")
    if texture_alias:
        lines.append(f"    Texture texture_of__{entity_lower};")
        lines.append(f"    get_texture_by__alias(")
        lines.append(f"            get_p_aliased_texture_manager_from__game(p_game),")
        lines.append(f"            \"{texture_alias}\",")
        lines.append(f"            &texture_of__{entity_lower});")
        lines.append(f"")
    lines.append(f"    Sprite *p_sprite =")
    lines.append(f"            allocate_sprite_from__sprite_manager(")
    lines.append(f"                    get_p_gfx_context_from__game(p_game),")
    lines.append(f"                    get_p_sprite_manager_from__graphics_window(")
    lines.append(f"                            p_game,")
    lines.append(f"                            get_p_graphics_window_from__world(")
    lines.append(f"                                    get_p_world_from__game(p_game))),")
    lines.append(f"                    get_p_graphics_window_from__world(")
    lines.append(f"                            get_p_world_from__game(p_game)),")
    lines.append(f"                    GET_UUID_P(p_entity),")
    if texture_alias:
        lines.append(f"                    texture_of__{entity_lower},")
    else:
        lines.append(f"                    (Texture){{0}},")
    lines.append(f"                    {size_flag});")
    lines.append(f"    if (p_sprite) {{")
    if sprite_kind:
        lines.append(f"        p_sprite->the_kind_of__sprite = Sprite_Kind__{sprite_kind};")
    if animation_group:
        lines.append(f"        p_sprite->the_kind_of__sprite__animation_group =")
        lines.append(f"                Sprite_Animation_Group_Kind__{animation_group};")
    lines.append(f"    }}")
    return "\n".join(lines)


def _gen_hitbox_wiring(hitbox_width, hitbox_height):
    return (
        f"    // Hitbox allocation\n"
        f"    Hitbox_AABB_Manager *p_hitbox_aabb_manager =\n"
        f"            (Hitbox_AABB_Manager*)get_pV_hitbox_manager_from__hitbox_context(\n"
        f"                    get_p_hitbox_context_from__game(p_game),\n"
        f"                    GET_UUID_P(get_p_world_from__game(p_game)));\n"
        f"    Hitbox_AABB *p_hitbox_aabb =\n"
        f"            allocate_hitbox_aabb_from__hitbox_aabb_manager(\n"
        f"                    p_hitbox_aabb_manager,\n"
        f"                    GET_UUID_P(p_entity));\n"
        f"    if (p_hitbox_aabb) {{\n"
        f"        set_size_of__hitbox_aabb(p_hitbox_aabb, {hitbox_width}, {hitbox_height});\n"
        f"    }}"
    )


def _gen_handler_replacement(entity_lower, update_handler):
    return (
        f"    // Replace __begin with real update handler\n"
        f"    p_entity->entity_functions.m_entity_update_handler =\n"
        f"            {update_handler};"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mod_entity.py",
        description="Wire __begin first-frame handler boilerplate into entity files.",
    )
    parser.add_argument("--entity", required=True, help="Entity name (e.g., Player, Skeleton).")
    parser.add_argument("--sprite-kind", default="", dest="sprite_kind",
                        help="Sprite_Kind name to attach (e.g., Player_Knight).")
    parser.add_argument("--texture-alias", default="", dest="texture_alias",
                        help="Aliased texture name for the sprite (e.g., player_knight).")
    parser.add_argument("--animation-group", default="", dest="animation_group",
                        help="Sprite_Animation_Group_Kind name (e.g., Player_Knight).")
    parser.add_argument("--texture-size", default="16x16", dest="texture_size",
                        help="Texture size flag for the sprite (e.g., 16x16, 8x8, 32x32).")
    parser.add_argument("--hitbox-size", default="", dest="hitbox_size",
                        help="Hitbox dimensions as WxH (e.g., 16x16).")
    parser.add_argument("--update-handler", default="", dest="update_handler",
                        help="Real update handler function name to replace __begin with.")

    args = parser.parse_args()

    entity_lower = args.entity.lower()
    if not _NAME_RE.match(args.entity):
        print(f"ERROR: Invalid entity name '{args.entity}'.")
        sys.exit(1)

    # Find the entity source file
    path = _ENTITY_SOURCE_REL.format(entity_lower=entity_lower)
    if not os.path.isfile(path):
        # Try with subdirectory patterns
        alt = f"source/entity/implemented/entity__{entity_lower}.c"
        if os.path.isfile(alt):
            path = alt
        else:
            print(f"ERROR: Entity source file not found at {path} or {alt}.")
            sys.exit(1)

    with open(path, "r") as fh:
        content = fh.read()

    original = content

    # Inject includes as needed
    if args.sprite_kind or args.texture_alias or args.animation_group:
        content = _inject_include(content, "rendering/aliased_texture_manager.h")
        content = _inject_include(content, "rendering/sprite.h")
        content = _inject_include(content, "rendering/sprite_manager.h")
        content = _inject_include(content, "world/world.h")
        content = _inject_include(content, "rendering/graphics_window.h")
    if args.hitbox_size:
        content = _inject_include(content, "collisions/hitbox_context.h")
        content = _inject_include(content, "collisions/core/aabb/hitbox_aabb_manager.h")
        content = _inject_include(content, "collisions/core/aabb/hitbox_aabb.h")
        content = _inject_include(content, "world/world.h")

    # Inject __begin handler body
    begin_marker_begin = "// GEN-BEGIN-BEGIN"
    begin_marker_end = "// GEN-BEGIN-END"

    if args.sprite_kind or args.texture_alias or args.animation_group:
        sprite_code = _gen_sprite_wiring(
            entity_lower, args.sprite_kind, args.texture_alias, args.animation_group, args.texture_size)
        content = _append_to_block(content, begin_marker_begin, begin_marker_end,
                                   sprite_code, "allocate_sprite_from__sprite_manager")

    if args.hitbox_size:
        parts = args.hitbox_size.lower().split("x")
        if len(parts) == 2:
            hitbox_code = _gen_hitbox_wiring(parts[0], parts[1])
            content = _append_to_block(content, begin_marker_begin, begin_marker_end,
                                       hitbox_code, "allocate_hitbox_aabb_from__hitbox_aabb_manager")

    if args.update_handler:
        handler_code = _gen_handler_replacement(entity_lower, args.update_handler)
        content = _append_to_block(content, begin_marker_begin, begin_marker_end,
                                   handler_code, "m_entity_update_handler =")

    if content != original:
        with open(path, "w") as fh:
            fh.write(content)
        tool_history.record_modify(path)
        print(f"  [mod_entity] updated {path}")
    else:
        print(f"  [mod_entity] no changes needed for {path}")

    print("Done.")


if __name__ == "__main__":
    main()
