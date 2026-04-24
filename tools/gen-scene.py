#!/usr/bin/env python3

import argparse
import os
import re
import sys


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


def copy_and_rename_source(name_lower, lavender_dir):
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
    args = parser.parse_args()

    name = args.name
    validate_name(name)

    lavender_dir = os.environ.get("LAVENDER_DIR")
    if not lavender_dir:
        print("Error: LAVENDER_DIR environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    name_lower = name.lower()

    update_scene_kind(name)
    copy_and_rename_header(name_lower, lavender_dir)
    copy_and_rename_source(name_lower, lavender_dir)
    update_scene_registrar(name, name_lower)

    print(f"Scene '{name}' generated successfully.")


if __name__ == "__main__":
    main()
