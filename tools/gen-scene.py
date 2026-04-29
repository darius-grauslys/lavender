#!/usr/bin/env python3

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET


def validate_name(name):
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
        print(f"Error: Invalid --name '{name}'. "
              "First character must be [a-zA-Z], "
              "remaining characters must be alphanumeric or underscores.",
              file=sys.stderr)
        sys.exit(1)


def update_scene_kind(name):
    path = os.path.join("include", "types", "implemented", "scene", "scene_kind.h")
    if not os.path.isfile(path):
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(path, "r") as f:
        content = f.read()

    entry = f"    Scene_Kind__{name},"
    gen_begin = "// GEN-BEGIN"
    gen_end = "// GEN-END"

    begin_idx = content.find(gen_begin)
    end_idx = content.find(gen_end)
    if begin_idx == -1 or end_idx == -1:
        print(f"Error: GEN-BEGIN/GEN-END markers not found in {path}.",
              file=sys.stderr)
        sys.exit(1)

    # Check if already present
    between = content[begin_idx:end_idx]
    if f"Scene_Kind__{name}" in between:
        print(f"Warning: Scene_Kind__{name} already exists in {path}. Skipping kind update.")
        return

    insert_pos = end_idx
    # Walk back to find the right insertion point (just before GEN-END line)
    line_start = content.rfind("\n", 0, end_idx)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    new_content = content[:line_start] + entry + "\n" + content[line_start:]

    with open(path, "w") as f:
        f.write(new_content)

    print(f"Updated {path} with Scene_Kind__{name}.")


def copy_and_rename_header(name_lower, lavender_dir):
    src = os.path.join(lavender_dir, "core", "include", "scene", "implemented", "scene__main.h")
    dst_dir = os.path.join("include", "scene", "implemented")
    dst = os.path.join(dst_dir, f"scene__{name_lower}.h")

    if not os.path.isfile(src):
        print(f"Error: Source header {src} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(dst_dir, exist_ok=True)

    with open(src, "r") as f:
        content = f.read()

    # Replace references to main with the new name
    content = content.replace("scene__main", f"scene__{name_lower}")
    content = content.replace("SCENE__MAIN", f"SCENE__{name_lower.upper()}")
    content = content.replace("scene_main", f"scene_{name_lower}")
    content = content.replace("register_scene__main", f"register_scene__{name_lower}")

    with open(dst, "w") as f:
        f.write(content)

    print(f"Created {dst}.")


def parse_ui_xml(xml_path):
    """Parse a UI XML file and extract tilesheet configuration from the <ui> element.

    Returns a dict:
        {
            "aliased_texture": str or None,
            "tile_map_size":   str,
        }
    """
    if not os.path.isfile(xml_path):
        print(f"Error: UI XML file '{xml_path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"Error: Failed to parse UI XML file '{xml_path}': {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()
    ui_elem = root.find("ui")
    if ui_elem is None:
        print(f"Error: No <ui> element found in '{xml_path}'.", file=sys.stderr)
        sys.exit(1)

    aliased_texture = ui_elem.get("ui_tile_map__aliased_texture", None)
    tile_map_size = ui_elem.get("ui_tile_map__size", "UI_Tile_Map_Size__Large")

    return {
        "aliased_texture": aliased_texture,
        "tile_map_size": tile_map_size,
    }


def populate_gen_marker(content, marker_name, lines):
    """Insert *lines* (a single string, may contain newlines) between the
    // <marker_name>-BEGIN and // <marker_name>-END markers.

    The text is inserted after the BEGIN line and before the END line.
    Returns the modified content string.
    """
    begin_marker = f"// {marker_name}-BEGIN"
    end_marker = f"// {marker_name}-END"

    begin_idx = content.find(begin_marker)
    end_idx = content.find(end_marker)

    if begin_idx == -1 or end_idx == -1:
        print(f"Warning: markers '{begin_marker}'/'{end_marker}' not found in content. "
              "Skipping population.", file=sys.stderr)
        return content

    # Find the position just after the newline that follows BEGIN
    after_begin = content.find("\n", begin_idx)
    if after_begin == -1:
        # No newline after BEGIN — insert right after the marker text
        after_begin = begin_idx + len(begin_marker)
    else:
        after_begin += 1  # move past the '\n'

    # Ensure lines ends with a newline so the END marker stays on its own line
    insert_text = lines
    if insert_text and not insert_text.endswith("\n"):
        insert_text += "\n"

    new_content = content[:after_begin] + insert_text + content[after_begin:]
    return new_content


def generate_ui_code(content, name_lower, ui_config):
    """Populate all GEN marker regions in *content* with UI boilerplate.

    Parameters
    ----------
    content    : str   — the source file content (after name replacements)
    name_lower : str   — lower-case scene name, e.g. "my_scene"
    ui_config  : dict  — {"aliased_texture": str|None, "tile_map_size": str}
    """
    aliased_texture = ui_config["aliased_texture"]
    tile_map_size = ui_config["tile_map_size"]

    # ------------------------------------------------------------------ #
    # GEN-INCLUDE-BEGIN/END
    # ------------------------------------------------------------------ #
    include_lines = (
        '#include "rendering/graphics_window.h"\n'
        '#include "rendering/graphics_window_manager.h"\n'
        '#include "rendering/aliased_texture_manager.h"\n'
        '#include "rendering/implemented/aliased_texture_registrar.h"\n'
        '#include "rendering/gfx_context.h"\n'
        '#include "ui/ui_tile_map_manager.h"\n'
        '#include "ui/ui_manager.h"'
    )
    content = populate_gen_marker(content, "GEN-INCLUDE", include_lines)

    # ------------------------------------------------------------------ #
    # GEN-FORWARD-BEGIN/END
    # ------------------------------------------------------------------ #
    forward_lines = (
        f"static Graphics_Window *_p_graphics_window__{name_lower} = 0;\n"
        f"static void load_ui_for__scene_{name_lower}(Game *p_game);\n"
        f"static void poll_ui_for__scene_{name_lower}(Game *p_game);\n"
        f"static void unload_ui_for__scene_{name_lower}(Game *p_game);"
    )
    content = populate_gen_marker(content, "GEN-FORWARD", forward_lines)

    # ------------------------------------------------------------------ #
    # GEN-LOAD-BEGIN/END  (4-space indent — inside m_load_scene handler)
    # ------------------------------------------------------------------ #
    load_lines = f"    load_ui_for__scene_{name_lower}(p_game);"
    content = populate_gen_marker(content, "GEN-LOAD", load_lines)

    # ------------------------------------------------------------------ #
    # GEN-FRAME-BEGIN/END  (8-space indent — inside while loop)
    # ------------------------------------------------------------------ #
    frame_lines = f"        poll_ui_for__scene_{name_lower}(p_game);"
    content = populate_gen_marker(content, "GEN-FRAME", frame_lines)

    # ------------------------------------------------------------------ #
    # GEN-PRE-RENDER-BEGIN/END  (8-space indent)
    # ------------------------------------------------------------------ #
    pre_render_lines = (
        "        compose_graphic_windows_in__graphics_window_manager(p_game);\n"
        "        render_graphic_windows_in__graphics_window_manager(p_game);"
    )
    content = populate_gen_marker(content, "GEN-PRE-RENDER", pre_render_lines)

    # ------------------------------------------------------------------ #
    # GEN-UNLOAD-BEGIN/END  (4-space indent — inside m_unload_scene handler)
    # ------------------------------------------------------------------ #
    unload_lines = f"    unload_ui_for__scene_{name_lower}(p_game);"
    content = populate_gen_marker(content, "GEN-UNLOAD", unload_lines)

    # ------------------------------------------------------------------ #
    # GEN-UI-MANAGEMENT-BEGIN/END  — wrapper function implementations
    # ------------------------------------------------------------------ #

    # Build the load_ui body — tile-map wiring is conditional on aliased_texture
    if aliased_texture is not None:
        tilemap_wiring = (
            f"    set_graphics_window__ui_tile_map(\n"
            f"            _p_graphics_window__{name_lower},\n"
            f"            allocate_ui_tile_map_with__ui_tile_map_manager(\n"
            f"                get_p_ui_tile_map_manager_from__gfx_context(\n"
            f"                    get_p_gfx_context_from__game(p_game)),\n"
            f"                {tile_map_size}));\n"
            f"    set_graphics_window__ui_tile_map__texture(\n"
            f"            _p_graphics_window__{name_lower},\n"
            f"            get_uuid_of__aliased_texture(\n"
            f"                get_p_aliased_texture_manager_from__game(p_game),\n"
            f"                name_of__texture__{aliased_texture}));\n"
        )
    else:
        tilemap_wiring = ""

    ui_management_lines = (
        f"static void load_ui_for__scene_{name_lower}(Game *p_game) {{\n"
        f"#ifdef PLATFORM__SDL\n"
        f"    _p_graphics_window__{name_lower} =\n"
        f"        allocate_graphics_window_from__graphics_window_manager(\n"
        f"                get_p_gfx_context_from__game(p_game),\n"
        f"                get_p_graphics_window_manager_from__gfx_context(\n"
        f"                    get_p_gfx_context_from__game(p_game)),\n"
        f"                TEXTURE_FLAG__SIZE_256x256);\n"
        f"    if (!_p_graphics_window__{name_lower}) {{\n"
        f'        debug_error("load_ui_for__scene_{name_lower}, failed to allocate.");\n'
        f"        return;\n"
        f"    }}\n"
        f"{tilemap_wiring}"
        f"    allocate_ui_manager_for__graphics_window(\n"
        f"            get_p_gfx_context_from__game(p_game),\n"
        f"            _p_graphics_window__{name_lower},\n"
        f"            128);\n"
        f"#endif\n"
        f"}}\n"
        f"\n"
        f"static void poll_ui_for__scene_{name_lower}(Game *p_game) {{\n"
        f"#ifdef PLATFORM__SDL\n"
        f"    poll_ui_manager__update(\n"
        f"            get_p_ui_manager_from__graphics_window(\n"
        f"                p_game,\n"
        f"                _p_graphics_window__{name_lower}),\n"
        f"            p_game,\n"
        f"            _p_graphics_window__{name_lower});\n"
        f"#endif\n"
        f"}}\n"
        f"\n"
        f"static void unload_ui_for__scene_{name_lower}(Game *p_game) {{\n"
        f"#ifdef PLATFORM__SDL\n"
        f"    release_graphics_window_from__graphics_window_manager(\n"
        f"            p_game,\n"
        f"            _p_graphics_window__{name_lower});\n"
        f"#endif\n"
        f"}}"
    )
    content = populate_gen_marker(content, "GEN-UI-MANAGEMENT", ui_management_lines)

    return content


def copy_and_rename_source(name_lower, lavender_dir, ui_config=None):
    src = os.path.join(lavender_dir, "core", "source", "scene", "implemented", "scene__main.c")
    dst_dir = os.path.join("source", "scene", "implemented")
    dst = os.path.join(dst_dir, f"scene__{name_lower}.c")

    if not os.path.isfile(src):
        print(f"Error: Source file {src} not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(dst_dir, exist_ok=True)

    with open(src, "r") as f:
        content = f.read()

    # Replace all mentions of "main" contextually
    content = content.replace("scene__main", f"scene__{name_lower}")
    content = content.replace("SCENE__MAIN", f"SCENE__{name_lower.upper()}")
    content = content.replace("scene_main", f"scene_{name_lower}")
    content = content.replace("register_scene__main", f"register_scene__{name_lower}")
    content = content.replace("Scene_Kind__Main", f"Scene_Kind__{name_lower.capitalize()}")

    # Populate GEN marker regions when --ui-xml was supplied
    if ui_config is not None:
        content = generate_ui_code(content, name_lower, ui_config)

    with open(dst, "w") as f:
        f.write(content)

    print(f"Created {dst}.")


def update_scene_registrar(name, name_lower):
    path = os.path.join("source", "scene", "implemented", "scene_registrar.c")
    if not os.path.isfile(path):
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(path, "r") as f:
        content = f.read()

    include_line = f'#include "scene/implemented/scene__{name_lower}.h"'
    register_line = f"    register_scene__{name_lower}(p_scene_manager);"

    # Update GEN-INCLUDE-BEGIN / GEN-INCLUDE-END
    inc_begin = "// GEN-INCLUDE-BEGIN"
    inc_end = "// GEN-INCLUDE-END"

    inc_begin_idx = content.find(inc_begin)
    inc_end_idx = content.find(inc_end)
    if inc_begin_idx == -1 or inc_end_idx == -1:
        print(f"Error: GEN-INCLUDE-BEGIN/END markers not found in {path}.",
              file=sys.stderr)
        sys.exit(1)

    between_inc = content[inc_begin_idx:inc_end_idx]
    if include_line not in between_inc:
        line_start = content.rfind("\n", 0, inc_end_idx)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1
        content = content[:line_start] + include_line + "\n" + content[line_start:]
        print(f"Added include for scene__{name_lower}.h in {path}.")
    else:
        print(f"Warning: Include for scene__{name_lower}.h already exists in {path}.")

    # Re-find indices after possible modification
    gen_begin = "// GEN-BEGIN"
    gen_end = "// GEN-END"

    # Find the GEN-BEGIN/END that is NOT the INCLUDE one
    # The registrar has GEN-INCLUDE-BEGIN/END and GEN-BEGIN/END
    begin_idx = content.find(gen_begin, content.find(inc_end))
    end_idx = content.find(gen_end, begin_idx) if begin_idx != -1 else -1

    if begin_idx == -1 or end_idx == -1:
        print(f"Error: GEN-BEGIN/GEN-END markers not found in {path}.",
              file=sys.stderr)
        sys.exit(1)

    between_reg = content[begin_idx:end_idx]
    if register_line not in between_reg:
        line_start = content.rfind("\n", 0, end_idx)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1
        content = content[:line_start] + register_line + "\n" + content[line_start:]
        print(f"Added register_scene__{name_lower} call in {path}.")
    else:
        print(f"Warning: register_scene__{name_lower} already exists in {path}.")

    with open(path, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Generate a new scene.")
    parser.add_argument("--name", required=True, help="Name of the scene to generate.")
    parser.add_argument("--ui-xml", default=None, metavar="PATH",
                        help="Optional path to a UI XML file. When provided, "
                             "UI wrapper functions are generated and wired into "
                             "the scene source file.")
    args = parser.parse_args()

    name = args.name
    validate_name(name)

    lavender_dir = os.environ.get("LAVENDER_DIR")
    if not lavender_dir:
        print("Error: LAVENDER_DIR environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    name_lower = name.lower()

    # Parse UI XML if supplied
    ui_config = None
    if args.ui_xml is not None:
        ui_config = parse_ui_xml(args.ui_xml)
        print(f"Parsed UI XML: aliased_texture={ui_config['aliased_texture']!r}, "
              f"tile_map_size={ui_config['tile_map_size']!r}")

    update_scene_kind(name)
    copy_and_rename_header(name_lower, lavender_dir)
    copy_and_rename_source(name_lower, lavender_dir, ui_config)
    update_scene_registrar(name, name_lower)

    print(f"Scene '{name}' generated successfully.")


if __name__ == "__main__":
    main()
