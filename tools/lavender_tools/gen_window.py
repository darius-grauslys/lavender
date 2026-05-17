#!/usr/bin/env python3
"""gen_window.py — Register Graphics_Window_Kind entries and UI window wiring.

Usage:
    python tools/lavender_tools/gen_window.py --name <Name> [--ui] [--load-func F] [--close-func F] [--sprites N] [--ui-elements N]

Manages the ``Graphics_Window_Kind`` enum in
``include/types/implemented/rendering/graphics_window_kind.h``.
When ``--ui`` is given, also wires an entry into
``source/ui/implemented/ui_window_registrar.c``.

For UI windows, the enum entry is auto-prefixed with ``UI__`` so the
final name becomes ``Graphics_Window_Kind__UI__<Name>``.
For non-UI windows the entry is ``Graphics_Window_Kind__<Name>``.
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

_ENUM_HEADER_REL = (
    "include/types/implemented/rendering/graphics_window_kind.h"
)
_REGISTRAR_SOURCE_REL = "source/ui/implemented/ui_window_registrar.c"
_REGISTRAR_HEADER_REL = "include/ui/implemented/ui_window_registrar.h"

_GEN_BEGIN = "// GEN-BEGIN"
_GEN_END = "// GEN-END"
_GEN_INCLUDE_BEGIN = "// GEN-INCLUDE-BEGIN"
_GEN_INCLUDE_END = "// GEN-INCLUDE-END"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_path(base_dir: str, rel: str) -> str:
    return os.path.join(base_dir, rel)


def _read_file(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    with open(path, "r") as fh:
        return fh.read()


def _write_file(path: str, content: str) -> None:
    with open(path, "w") as fh:
        fh.write(content)


def _validate_name(name: str) -> bool:
    """Each segment separated by __ must match [a-zA-Z][a-zA-Z0-9_]*."""
    for segment in name.split("__"):
        if not _NAME_RE.match(segment):
            return False
    return True


# ---------------------------------------------------------------------------
# Enum management – graphics_window_kind.h
# ---------------------------------------------------------------------------

def _enum_entry_name(name: str, *, ui: bool) -> str:
    """Build the full enum entry name."""
    if ui:
        return f"Graphics_Window_Kind__UI__{name}"
    return f"Graphics_Window_Kind__{name}"


def register_window_kind(
    name: str,
    *,
    ui: bool = False,
    base_dir: str = "./",
) -> str | None:
    """Add a Graphics_Window_Kind entry to the enum header.

    Returns the full enum entry name on success, or None on failure.
    Prints status/error messages to stdout.
    """
    entry = _enum_entry_name(name, ui=ui)
    header_path = _resolve_path(base_dir, _ENUM_HEADER_REL)
    text = _read_file(header_path)

    if text is None:
        print(f"ERROR: {header_path} not found.")
        return None

    # Duplicate check BEFORE any modification.
    if entry in text:
        print(f"  [enum] {entry} already exists, skipping.")
        return entry

    # Find GEN-BEGIN / GEN-END markers.
    begin_idx = text.find(_GEN_BEGIN)
    end_idx = text.find(_GEN_END)
    if begin_idx == -1 or end_idx == -1 or end_idx <= begin_idx:
        print(f"ERROR: GEN-BEGIN/GEN-END markers not found in {header_path}.")
        return None

    # Insert just before GEN-END.
    insert_pos = end_idx
    indent = "    "
    new_line = f"{indent}{entry},\n"
    text = text[:insert_pos] + new_line + text[insert_pos:]

    _write_file(header_path, text)
    tool_history.record_modify(header_path)
    print(f"  [enum] added {entry} to {header_path}")
    return entry


# ---------------------------------------------------------------------------
# Registrar management – ui_window_registrar.c
# ---------------------------------------------------------------------------

def register_ui_window(
    name: str,
    *,
    load_func: str = "",
    close_func: str = "f_ui_window__close__default",
    sprites: int = 0,
    ui_elements: int = 16,
    base_dir: str = "./",
) -> bool:
    """Wire a UI window into ui_window_registrar.c.

    Adds a #include and a register_ui_window_into__ui_context() call.
    Returns True on success.
    """
    entry = _enum_entry_name(name, ui=True)
    registrar_path = _resolve_path(base_dir, _REGISTRAR_SOURCE_REL)
    text = _read_file(registrar_path)

    if text is None:
        print(f"ERROR: {registrar_path} not found.")
        return False

    # Derive defaults from name.
    source_name = f"ui_window__{name.lower()}"
    if not load_func:
        load_func = f"allocate_ui_for__{source_name}"
    include_path = f"ui/implemented/generated/game/{source_name}.h"

    # Duplicate check.
    if load_func in text:
        print(f"  [registrar] {load_func} already registered, skipping.")
        return True

    lines = text.split("\n")

    # --- Add include in GEN-INCLUDE-BEGIN / END block ---
    include_line = f'#include "{include_path}"'
    gi_begin = -1
    gi_end = -1
    for i, line in enumerate(lines):
        if line.strip() == _GEN_INCLUDE_BEGIN.strip():
            gi_begin = i
        if line.strip() == _GEN_INCLUDE_END.strip():
            gi_end = i
            break

    if gi_begin != -1 and gi_end != -1 and include_line not in text:
        lines.insert(gi_end, include_line)
        # Re-parse since we shifted.
        text = "\n".join(lines)
        lines = text.split("\n")

    # --- Add registration call in GEN-BEGIN / END block ---
    g_begin = -1
    g_end = -1
    for i, line in enumerate(lines):
        if line.strip() == _GEN_BEGIN.strip():
            g_begin = i
        if line.strip() == _GEN_END.strip() and g_begin != -1:
            g_end = i
            break

    if g_begin == -1 or g_end == -1:
        print(f"ERROR: GEN-BEGIN/GEN-END markers not found in {registrar_path}.")
        return False

    reg_call = (
        f"    register_ui_window_into__ui_context(\n"
        f"            p_ui_context,\n"
        f"            {load_func},\n"
        f"            {close_func},\n"
        f"            {entry},\n"
        f"            {sprites}, {ui_elements});"
    )

    lines.insert(g_end, reg_call)
    text = "\n".join(lines)

    _write_file(registrar_path, text)
    tool_history.record_modify(registrar_path)
    print(f"  [registrar] added {load_func} to {registrar_path}")
    return True


# ---------------------------------------------------------------------------
# Verification (used by gen_ui.py and gen_ui_code.py)
# ---------------------------------------------------------------------------

def verify_window_exists(
    name: str,
    *,
    ui: bool = False,
    base_dir: str = "./",
) -> bool:
    """Check that a Graphics_Window_Kind entry exists in the enum header.

    Returns True if the entry is found, False otherwise.
    Prints an actionable error message on failure.
    """
    entry = _enum_entry_name(name, ui=ui)
    header_path = _resolve_path(base_dir, _ENUM_HEADER_REL)
    text = _read_file(header_path)

    if text is None:
        print(
            f"ERROR: {header_path} not found. "
            f"Cannot verify {entry}."
        )
        return False

    if entry not in text:
        ui_flag = " --ui" if ui else ""
        print(
            f"ERROR: {entry} not found in {header_path}.\n"
            f"  Run: gen_window.py --name {name}{ui_flag}"
        )
        return False

    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gen_window.py",
        description=(
            "Register a Graphics_Window_Kind entry and optionally wire "
            "a UI window into ui_window_registrar.c."
        ),
    )
    parser.add_argument(
        "--name",
        required=True,
        help=(
            "Window name.  E.g. 'Game__Hud', 'World__Ground'.  "
            "For UI windows (--ui), 'UI__' is auto-prepended."
        ),
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        default=False,
        help=(
            "Mark as a UI-centric window.  Adds 'UI__' prefix to the "
            "enum entry and wires ui_window_registrar.c."
        ),
    )
    parser.add_argument(
        "--load-func",
        default="",
        help=(
            "Load function name for the UI window.  Defaults to "
            "'allocate_ui_for__ui_window__<name_lower>'."
        ),
    )
    parser.add_argument(
        "--close-func",
        default="f_ui_window__close__default",
        help=(
            "Close function name for the UI window.  "
            "(default: f_ui_window__close__default)"
        ),
    )
    parser.add_argument(
        "--sprites",
        type=int,
        default=0,
        help=(
            "Sprite allocation quantity.  Positive = allocate, "
            "negative = share from parent, 0 = none.  (default: 0)"
        ),
    )
    parser.add_argument(
        "--ui-elements",
        type=int,
        default=16,
        help=(
            "UI element allocation quantity.  Positive = allocate, "
            "negative = share from parent, 0 = none.  (default: 16)"
        ),
    )

    args = parser.parse_args()

    if not _validate_name(args.name):
        print(
            f"ERROR: Invalid name '{args.name}'.  "
            "Each segment must start with a letter and contain only "
            "alphanumeric characters or underscores."
        )
        sys.exit(1)

    # --- Step 1: Register enum entry (always) ---
    entry = register_window_kind(
        args.name, ui=args.ui, base_dir="./"
    )
    if entry is None:
        sys.exit(1)

    # --- Step 2: Wire registrar (only for --ui) ---
    if args.ui:
        ok = register_ui_window(
            args.name,
            load_func=args.load_func,
            close_func=args.close_func,
            sprites=args.sprites,
            ui_elements=args.ui_elements,
            base_dir="./",
        )
        if not ok:
            sys.exit(1)

    print(f"Done: {entry}")


if __name__ == "__main__":
    main()
