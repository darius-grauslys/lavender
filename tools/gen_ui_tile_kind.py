#!/usr/bin/env python3
"""
gen_ui_tile_kind.py - UI tile kind entry generator for Lavender projects.

Run from the root of a Lavender project directory (the one that contains
./include and ./source).

Usage examples:
    python tools/gen_ui_tile_kind.py --name Background_Fill --value 104
    python tools/gen_ui_tile_kind.py --name Button_Fill --value 98
    python tools/gen_ui_tile_kind.py --name Button_Toggled_Fill --value "UI_Tile_Kind__Button_Fill"
    python tools/gen_ui_tile_kind.py --name Slider_Box_Vertical_Fill --value "98 + (32*14)"
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.getcwd()

UI_TILE_KIND_H = os.path.join(
    PROJECT_ROOT, "include", "types", "implemented", "ui", "ui_tile_kind.h")


def _fatal(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(f"ERROR: {msg}", file=sys.stdout)
    sys.exit(1)


def _read(path):
    with open(path, "r") as f:
        return f.read()


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def _validate_name(name):
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
        _fatal(f"Invalid name '{name}'. Must start with [a-zA-Z] and "
               f"contain only alphanumeric/underscore characters.")


# ---------------------------------------------------------------------------
# Value validation
# ---------------------------------------------------------------------------

def _validate_value(value, text):
    """Validate that *value* is a non-negative integer 0-1023 or an existing
    enum entry name (UI_Tile_Kind__<Something>) already present in *text*.

    Returns the validated value string to use in the enum assignment.
    """
    # Try parsing as integer first
    try:
        int_val = int(value)
        if int_val < 0 or int_val > 1023:
            _fatal(f"Integer value {int_val} is out of range. "
                   f"Must be 0-1023.")
        return str(int_val)
    except ValueError:
        pass

    # Must be a string referencing an existing enum entry
    if not re.match(r'^UI_Tile_Kind__[a-zA-Z][a-zA-Z0-9_]*$', value):
        _fatal(f"Invalid value '{value}'. Must be a positive integer 0-1023 "
               f"or an existing UI_Tile_Kind__<Name> enum entry.")

    # Check that the referenced enum entry exists in the file
    if value not in text:
        _fatal(f"Referenced enum entry '{value}' not found in "
               f"{UI_TILE_KIND_H}. The value must refer to an "
               f"existing entry.")

    return value


# ---------------------------------------------------------------------------
# Region helpers
# ---------------------------------------------------------------------------

def _get_region(text, begin_tag, end_tag):
    lines = text.split("\n")
    begin_idx = end_idx = None
    indent = ""
    for i, line in enumerate(lines):
        if begin_tag in line:
            begin_idx = i
            indent = line[: len(line) - len(line.lstrip())]
        if end_tag in line and begin_idx is not None:
            end_idx = i
            break
    if begin_idx is None or end_idx is None:
        return None
    pre = lines[: begin_idx + 1]
    region = lines[begin_idx + 1: end_idx]
    post = lines[end_idx:]
    return pre, region, post, indent


def _set_region(text, begin_tag, end_tag, new_lines):
    parts = _get_region(text, begin_tag, end_tag)
    if parts is None:
        _fatal(f"Could not find region {begin_tag}..{end_tag}")
    pre, _old, post, _indent = parts
    return "\n".join(pre + new_lines + post)


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add a UI_Tile_Kind entry to ui_tile_kind.h.")
    parser.add_argument("--name", required=True,
                        help="Tile kind name (e.g. Background_Fill, "
                             "Button_Corner__Top_Left)")
    parser.add_argument("--value", required=True,
                        help="Enum value: a positive integer 0-1023 or "
                             "an existing UI_Tile_Kind__<Name> enum entry")
    args = parser.parse_args()

    _validate_name(args.name)

    if not os.path.exists(UI_TILE_KIND_H):
        _fatal(f"Header not found: {UI_TILE_KIND_H}")

    text = _read(UI_TILE_KIND_H)

    entry_name = f"UI_Tile_Kind__{args.name}"

    # Check for duplicates
    if entry_name in text:
        _fatal(f"Entry '{entry_name}' already exists in {UI_TILE_KIND_H}")

    # Validate the value
    validated_value = _validate_value(args.value, text)

    # Ensure GEN markers exist
    parts = _get_region(text, "// GEN-BEGIN", "// GEN-END")
    if parts is None:
        _fatal(f"Could not find // GEN-BEGIN .. // GEN-END region in "
               f"{UI_TILE_KIND_H}")

    _pre, region, _post, indent = parts

    # Build the new entry line (indent matches the GEN-BEGIN marker line)
    new_entry = f"    {entry_name} = {validated_value},"

    # Insert at the end of the region
    new_region = region + [new_entry]
    text = _set_region(text, "// GEN-BEGIN", "// GEN-END", new_region)

    _write(UI_TILE_KIND_H, text)
    print(f"[gen_ui_tile_kind] Added '{entry_name} = {validated_value}' to "
          f"{UI_TILE_KIND_H}")
    print(f"  [updated] {UI_TILE_KIND_H}")
    print("[gen_ui_tile_kind] Done.")


if __name__ == "__main__":
    main()
