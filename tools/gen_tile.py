#!/usr/bin/env python3
"""
gen_tile.py - Tile kind entry generator for Lavender projects.

Run from the root of a Lavender project directory (the one that contains
./include and ./source).

Usage examples:
    python tools/gen_tile.py --layer Ground --name Lava --is-logical
    python tools/gen_tile.py --layer Ground --name Grass
    python tools/gen_tile.py --layer Cover --name Door__Horizontal --is-logical
    python tools/gen_tile.py --layer Cover --name Plant__Grass
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.getcwd()

_SPEC_FILE = os.path.join(PROJECT_ROOT, ".tile_layer_specs.json")

_TILE_LAYER_H = os.path.join(
    PROJECT_ROOT, "include", "types", "implemented", "world", "tile_layer.h")


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


def _to_pascal(name):
    return "_".join(seg.capitalize() for seg in name.split("_"))


def _to_lower(name):
    return name.lower()


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
# Spec loading
# ---------------------------------------------------------------------------

def _load_specs():
    if os.path.exists(_SPEC_FILE):
        with open(_SPEC_FILE, "r") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Parse existing tile_layer.h layers
# ---------------------------------------------------------------------------

def _parse_existing_layers():
    if not os.path.exists(_TILE_LAYER_H):
        return []
    text = _read(_TILE_LAYER_H)
    parts = _get_region(text, "// GEN-BEGIN", "// GEN-END")
    if parts is None:
        return []
    _pre, region, _post, _indent = parts
    layers = []
    for line in region:
        m = re.match(r'\s*Tile_Layer__(\w+)\s*,?', line)
        if m:
            layers.append(m.group(1))
    return layers


# ---------------------------------------------------------------------------
# Resolve the kind header path for a layer
# ---------------------------------------------------------------------------

def _get_kind_header_path(layer_pascal, ordered_layers):
    """Return the path to the tile kind header for the given layer.

    The first layer in the ordered list uses ``tile_kind.h``;
    subsequent layers use ``tile_<lower>_kind.h``.
    """
    is_first = (ordered_layers and ordered_layers[0] == layer_pascal)
    if is_first:
        return os.path.join(
            PROJECT_ROOT, "include", "types", "implemented", "world",
            "tile_kind.h")
    else:
        lower = _to_lower(layer_pascal)
        return os.path.join(
            PROJECT_ROOT, "include", "types", "implemented", "world",
            f"tile_{lower}_kind.h")


# ---------------------------------------------------------------------------
# Build the enum entry prefix for a layer
# ---------------------------------------------------------------------------

def _get_enum_prefix(layer_pascal, ordered_layers):
    """Return the enum entry prefix.

    First layer: ``Tile_Kind``
    Other layers: ``Tile_<Pascal>_Kind``
    """
    is_first = (ordered_layers and ordered_layers[0] == layer_pascal)
    if is_first:
        return "Tile_Kind"
    else:
        return f"Tile_{layer_pascal}_Kind"


# ---------------------------------------------------------------------------
# Count existing logical entries
# ---------------------------------------------------------------------------

def _count_logical_entries(region_lines):
    """Count non-empty, non-comment lines in the GEN-LOGIC region."""
    count = 0
    for line in region_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("//"):
            count += 1
    return count


def _get_last_logical_entry(region_lines):
    """Return the enum name of the last logical entry, or None."""
    last = None
    for line in region_lines:
        m = re.match(r'\s*(\w+)\s*,?\s*$', line)
        if m and not line.strip().startswith("//"):
            last = m.group(1)
    return last


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add a tile kind entry to a tile layer's kind enum.")
    parser.add_argument("--layer", required=True,
                        help="Layer name (e.g. Ground, Cover)")
    parser.add_argument("--name", required=True,
                        help="Tile kind name (e.g. Lava, Door__Horizontal)")
    parser.add_argument("--is-logical", action="store_true",
                        dest="is_logical",
                        help="Insert into the logical (GEN-LOGIC) region")
    args = parser.parse_args()

    _validate_name(args.layer)
    _validate_name(args.name)

    layer_pascal = _to_pascal(args.layer)
    tile_name_pascal = _to_pascal(args.name)

    # --- Validate layer exists ---
    existing_layers = _parse_existing_layers()
    if layer_pascal not in existing_layers:
        msg = (f"Layer 'Tile_Layer__{layer_pascal}' not found in "
               f"tile_layer.h. Existing layers: {existing_layers}")
        print(f"ERROR: {msg}", file=sys.stdout)
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    specs = _load_specs()
    if layer_pascal not in specs:
        msg = (f"Layer '{layer_pascal}' has no spec in "
               f".tile_layer_specs.json. Run gen_tile_layer.py first.")
        print(f"ERROR: {msg}", file=sys.stdout)
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    layer_spec = specs[layer_pascal]
    logic_bits = layer_spec["logic_bits"]

    # --- Resolve paths and prefixes ---
    kind_header_path = _get_kind_header_path(layer_pascal, existing_layers)
    enum_prefix = _get_enum_prefix(layer_pascal, existing_layers)

    if not os.path.exists(kind_header_path):
        _fatal(f"Kind header not found: {kind_header_path}")

    text = _read(kind_header_path)

    # Build the full enum entry name
    entry_name = f"{enum_prefix}__{tile_name_pascal}"

    # Check for duplicates
    if entry_name in text:
        _fatal(f"Entry '{entry_name}' already exists in {kind_header_path}")

    if args.is_logical:
        # --- Insert into GEN-LOGIC region ---
        parts = _get_region(text, "// GEN-LOGIC-BEGIN", "// GEN-LOGIC-END")
        if parts is None:
            _fatal(f"Could not find GEN-LOGIC region in {kind_header_path}")
        _pre, logic_region, _post, indent = parts

        # Check capacity: logical entries must fit in logic_bits
        # The max number of logical entries is (2^logic_bits - 1) because
        # index 0 is Tile_Kind__None
        current_count = _count_logical_entries(logic_region)
        max_logical = (1 << logic_bits) - 1  # reserve 0 for None
        if current_count + 1 > max_logical:
            msg = (f"Cannot add logical entry '{entry_name}': "
                   f"would have {current_count + 1} logical entries but "
                   f"logic bit-field is {logic_bits} bits "
                   f"(max {max_logical} entries, excluding None).")
            print(f"ERROR: {msg}", file=sys.stdout)
            print(f"ERROR: {msg}", file=sys.stderr)
            sys.exit(1)

        # Add the new entry at the end of the logic region
        new_logic_region = logic_region + [f"{indent}{entry_name},"]
        text = _set_region(text,
                           "// GEN-LOGIC-BEGIN", "// GEN-LOGIC-END",
                           new_logic_region)

        # Update Tile_Kind__Logical to point to the new last entry
        # Pattern: Tile_Kind__Logical = <something>,
        # or: Tile_Kind__Logical = Tile_Kind__None,
        logical_pattern = re.compile(
            r'(Tile_Kind__Logical\s*=\s*)\w+',
            re.MULTILINE)
        if logical_pattern.search(text):
            text = logical_pattern.sub(
                rf'\g<1>{entry_name}', text)
        else:
            _fatal("Could not find 'Tile_Kind__Logical = ...' in "
                   f"{kind_header_path}")

        print(f"[gen_tile] Added logical entry '{entry_name}' to "
              f"{kind_header_path}")
        print(f"  Updated Tile_Kind__Logical = {entry_name}")

    else:
        # --- Insert into GEN-NO-LOGIC region ---
        parts = _get_region(text,
                            "// GEN-NO-LOGIC-BEGIN", "// GEN-NO-LOGIC-END")
        if parts is None:
            _fatal(f"Could not find GEN-NO-LOGIC region in "
                   f"{kind_header_path}")
        _pre, no_logic_region, _post, indent = parts

        # Add the new entry at the end of the no-logic region
        new_no_logic_region = no_logic_region + [f"{indent}{entry_name},"]
        text = _set_region(text,
                           "// GEN-NO-LOGIC-BEGIN", "// GEN-NO-LOGIC-END",
                           new_no_logic_region)

        print(f"[gen_tile] Added entry '{entry_name}' to "
              f"{kind_header_path}")

    _write(kind_header_path, text)
    print(f"  [updated] {kind_header_path}")
    print("[gen_tile] Done.")


if __name__ == "__main__":
    main()
