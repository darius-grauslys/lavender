#!/usr/bin/env python3
"""gen_tile_logic.py — Add/remove tile logic and animation entries.

Usage:
    python tools/lavender_tools/gen_tile_logic.py --layer <Layer> --name <Name> [options]

Manages entries in ``tile_logic_table__<layer>.c`` within GEN markers.
Logic entries define passability, height, and sight-blocking for tile kinds.
Animation entries define frame sequences for animated tiles.

Maximum 255 entries per layer (index 0 is reserved for "no entry").

**Note**: Tile animation runtime is NOT yet implemented in Lavender CORE.
The animation sub-bit-field exists in the Tile struct byte-packing, but
no engine code steps animation state at runtime. Animation entries are
registered for future use.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from lavender_tools import tool_history

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
_MAX_ENTRIES = 255  # 0 reserved for no entry

_TILE_LOGIC_SOURCE_REL = "source/world/implemented/tile_logic_table__{layer_lower}.c"
_TILE_LOGIC_HEADER_REL = "include/world/implemented/tile_logic_table__{layer_lower}.h"

_GEN_LOGIC_BEGIN = "// GEN-LOGIC-BEGIN"
_GEN_LOGIC_END = "// GEN-LOGIC-END"
_GEN_NO_LOGIC_BEGIN = "// GEN-NO-LOGIC-BEGIN"
_GEN_NO_LOGIC_END = "// GEN-NO-LOGIC-END"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_name(name: str) -> bool:
    for seg in name.split("__"):
        if not _NAME_RE.match(seg):
            return False
    return True


def _find_gen_block(content: str, begin_tag: str, end_tag: str):
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


def _count_entries_in_block(content: str, begin_tag: str, end_tag: str, pattern: str) -> int:
    bounds = _find_gen_block(content, begin_tag, end_tag)
    if bounds is None:
        return 0
    block = content[bounds[0]:bounds[1]]
    return len(re.findall(pattern, block))


def _append_to_block(content: str, begin_tag: str, end_tag: str,
                     new_text: str, dedup_key: str) -> str:
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


def _remove_from_block(content: str, begin_tag: str, end_tag: str,
                       pattern: str) -> str:
    bounds = _find_gen_block(content, begin_tag, end_tag)
    if bounds is None:
        return content
    block = content[bounds[0]:bounds[1]]
    new_block = re.sub(pattern, "", block)
    # Clean up double blank lines
    while "\n\n\n" in new_block:
        new_block = new_block.replace("\n\n\n", "\n\n")
    return content[:bounds[0]] + new_block + content[bounds[1]:]


# ---------------------------------------------------------------------------
# Logic entry management
# ---------------------------------------------------------------------------

def add_logic_entry(layer: str, name: str, *,
                    passable: bool = True,
                    height: int = 0,
                    sight_blocking: bool = False,
                    is_logical: bool = False) -> bool:
    layer_lower = layer.lower()
    path = _TILE_LOGIC_SOURCE_REL.format(layer_lower=layer_lower)

    if not os.path.isfile(path):
        print(f"ERROR: {path} not found.")
        return False

    with open(path, "r") as fh:
        content = fh.read()

    entry_name = f"Tile_{layer}_Kind__{name}" if layer != "Ground" else f"Tile_Kind__{name}"
    dedup = entry_name

    # Check max entries
    begin = _GEN_LOGIC_BEGIN if is_logical else _GEN_NO_LOGIC_BEGIN
    end = _GEN_LOGIC_END if is_logical else _GEN_NO_LOGIC_END

    total = _count_entries_in_block(content, _GEN_LOGIC_BEGIN, _GEN_LOGIC_END, r"Tile_\w+Kind__\w+")
    total += _count_entries_in_block(content, _GEN_NO_LOGIC_BEGIN, _GEN_NO_LOGIC_END, r"Tile_\w+Kind__\w+")
    if total >= _MAX_ENTRIES:
        print(f"ERROR: Maximum {_MAX_ENTRIES} entries reached for layer {layer}.")
        return False

    # Build the logic entry comment/code
    flags = []
    if passable:
        flags.append("passable")
    else:
        flags.append("impassable")
    if sight_blocking:
        flags.append("sight-blocking")
    if height != 0:
        flags.append(f"height={height}")

    comment = f"    // {entry_name}: {', '.join(flags)}"
    content = _append_to_block(content, begin, end, comment, dedup)

    with open(path, "w") as fh:
        fh.write(content)
    tool_history.record_modify(path)
    print(f"  [tile_logic] added {entry_name} to {path}")
    return True


def remove_logic_entry(layer: str, name: str) -> bool:
    layer_lower = layer.lower()
    path = _TILE_LOGIC_SOURCE_REL.format(layer_lower=layer_lower)

    if not os.path.isfile(path):
        print(f"ERROR: {path} not found.")
        return False

    with open(path, "r") as fh:
        content = fh.read()

    entry_name = f"Tile_{layer}_Kind__{name}" if layer != "Ground" else f"Tile_Kind__{name}"
    if entry_name not in content:
        print(f"  [skip] {entry_name} not found in {path}.")
        return True

    # Remove from both possible blocks
    pattern = rf"[^\n]*{re.escape(entry_name)}[^\n]*\n"
    content = _remove_from_block(content, _GEN_LOGIC_BEGIN, _GEN_LOGIC_END, pattern)
    content = _remove_from_block(content, _GEN_NO_LOGIC_BEGIN, _GEN_NO_LOGIC_END, pattern)

    with open(path, "w") as fh:
        fh.write(content)
    tool_history.record_modify(path)
    print(f"  [tile_logic] removed {entry_name} from {path}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gen_tile_logic.py",
        description="Add or remove tile logic/animation entries.",
    )
    parser.add_argument("--layer", required=True, help="Tile layer name (e.g., Ground, Cover, Wall).")
    parser.add_argument("--name", required=True, help="Tile kind name (e.g., Grass, Stone_Brick).")
    parser.add_argument("--passable", action="store_true", default=True, help="Mark tile as passable (default).")
    parser.add_argument("--impassable", action="store_true", default=False, help="Mark tile as impassable.")
    parser.add_argument("--sight-blocking", action="store_true", default=False, dest="sight_blocking")
    parser.add_argument("--height", type=int, default=0, help="Tile height value (default: 0).")
    parser.add_argument("--is-logical", action="store_true", default=False, dest="is_logical",
                        help="Place in the logical region of the tile kind header.")
    parser.add_argument("--remove", action="store_true", default=False, help="Remove the entry instead of adding.")

    args = parser.parse_args()

    if not _validate_name(args.name):
        print(f"ERROR: Invalid name '{args.name}'.")
        sys.exit(1)
    if not _validate_name(args.layer):
        print(f"ERROR: Invalid layer '{args.layer}'.")
        sys.exit(1)

    passable = not args.impassable

    if args.remove:
        ok = remove_logic_entry(args.layer, args.name)
    else:
        ok = add_logic_entry(
            args.layer, args.name,
            passable=passable,
            height=args.height,
            sight_blocking=args.sight_blocking,
            is_logical=args.is_logical,
        )

    if not ok:
        sys.exit(1)
    print("Done.")


if __name__ == "__main__":
    main()
