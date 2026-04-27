#!/usr/bin/env python3
"""
gen_aliased_texture.py - Aliased texture entry generator for Lavender projects.

Run from the root of a Lavender project directory (the one that contains
./include and ./source).

Usage examples:
    python tools/gen_aliased_texture.py --name ground --path assets/world/ground.png
    python tools/gen_aliased_texture.py --name player --path assets/entities/entities__16x16/player.png
    python tools/gen_aliased_texture.py --name ui_sprites__16x16 --path assets/ui/sprites/ui_sprite__16x16/ui_sprites__16x16.png
"""

import argparse
import os
import re
import struct
import sys
import zlib

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.getcwd()

REGISTRAR_C_PATH = os.path.join(
    PROJECT_ROOT, "source", "rendering", "implemented",
    "aliased_texture_registrar.c")

REGISTRAR_H_PATH = os.path.join(
    PROJECT_ROOT, "include", "rendering", "implemented",
    "aliased_texture_registrar.h")

# Known TEXTURE_FLAG__SIZE_WxH definitions from defines.h.
# Maps (width, height) -> macro name.
# Only power-of-two aligned sizes that exist in the engine are listed.
_TEXTURE_SIZE_FLAGS = {
    (8, 8):       "TEXTURE_FLAG__SIZE_8x8",
    (8, 16):      "TEXTURE_FLAG__SIZE_8x16",
    (8, 32):      "TEXTURE_FLAG__SIZE_8x32",
    (16, 8):      "TEXTURE_FLAG__SIZE_16x8",
    (16, 16):     "TEXTURE_FLAG__SIZE_16x16",
    (16, 32):     "TEXTURE_FLAG__SIZE_16x32",
    (32, 8):      "TEXTURE_FLAG__SIZE_32x8",
    (32, 16):     "TEXTURE_FLAG__SIZE_32x16",
    (32, 32):     "TEXTURE_FLAG__SIZE_32x32",
    (32, 64):     "TEXTURE_FLAG__SIZE_32x64",
    (64, 64):     "TEXTURE_FLAG__SIZE_64x64",
    (128, 128):   "TEXTURE_FLAG__SIZE_128x128",
    (256, 256):   "TEXTURE_FLAG__SIZE_256x256",
    (512, 256):   "TEXTURE_FLAG__SIZE_512x256",
    (256, 512):   "TEXTURE_FLAG__SIZE_256x512",
    (512, 512):   "TEXTURE_FLAG__SIZE_512x512",
    (512, 1024):  "TEXTURE_FLAG__SIZE_512x1024",
    (1024, 512):  "TEXTURE_FLAG__SIZE_1024x512",
    (1024, 1024): "TEXTURE_FLAG__SIZE_1024x1024",
    (2048, 2048): "TEXTURE_FLAG__SIZE_2048x2048",
    (4096, 4096): "TEXTURE_FLAG__SIZE_4096x4096",
    (8192, 8192): "TEXTURE_FLAG__SIZE_8192x8192",
}


def _fatal(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(f"ERROR: {msg}", file=sys.stdout)
    sys.exit(1)


def _read(path):
    if not os.path.isfile(path):
        _fatal(f"File not found: {path}")
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


def _to_lower(name):
    return name.lower()


# ---------------------------------------------------------------------------
# PNG dimension reader (no external dependencies)
# ---------------------------------------------------------------------------

def _read_png_dimensions(png_path):
    """Read the width and height from a PNG file's IHDR chunk.

    Returns (width, height) or calls _fatal on error.
    """
    try:
        with open(png_path, "rb") as f:
            header = f.read(8)
            if header[:8] != b'\x89PNG\r\n\x1a\n':
                _fatal(f"'{png_path}' is not a valid PNG file.")
            # IHDR is always the first chunk
            chunk_len = struct.unpack(">I", f.read(4))[0]
            chunk_type = f.read(4)
            if chunk_type != b'IHDR':
                _fatal(f"'{png_path}' is malformed: first chunk is not IHDR.")
            ihdr_data = f.read(chunk_len)
            width, height = struct.unpack(">II", ihdr_data[:8])
            return width, height
    except (IOError, OSError) as e:
        _fatal(f"Cannot read PNG file '{png_path}': {e}")


def _get_texture_size_flag(width, height):
    """Return the TEXTURE_FLAG__SIZE_WxH macro for the given dimensions.

    Falls back to the smallest flag whose dimensions are >= the image.
    If no exact match exists, returns None.
    """
    key = (width, height)
    if key in _TEXTURE_SIZE_FLAGS:
        return _TEXTURE_SIZE_FLAGS[key]
    return None


# ---------------------------------------------------------------------------
# Region helpers (matching gen_tile.py / gen_sprite.py style)
# ---------------------------------------------------------------------------

def _insert_between_markers(text, begin_marker, end_marker, new_line,
                            *, duplicate_check=None):
    """Insert *new_line* just before *end_marker* inside *text*.

    If *duplicate_check* is given and already appears between the markers the
    text is returned unchanged.
    """
    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)
    if begin_idx == -1 or end_idx == -1:
        _fatal(f"Could not find markers "
               f"'{begin_marker}' / '{end_marker}'")

    region = text[begin_idx:end_idx]
    if duplicate_check and duplicate_check in region:
        return text  # already present

    insert_pos = end_idx
    return text[:insert_pos] + new_line + "\n" + text[insert_pos:]


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add an aliased texture entry to the "
                    "aliased_texture_registrar for a Lavender project.")
    parser.add_argument("--name", required=True,
                        help="Texture name identifier (e.g. ground, "
                             "player, ui_sprites__16x16)")
    parser.add_argument("--path", required=True,
                        help="Path to the .png file, relative to the "
                             "project root (e.g. assets/world/ground.png)")
    args = parser.parse_args()

    name = args.name
    png_path_arg = args.path

    # --- Validate name ---
    _validate_name(name)

    name_lower = _to_lower(name)

    # --- Validate PNG path ---
    if not png_path_arg.endswith(".png"):
        _fatal(f"Path '{png_path_arg}' must point to a .png file.")

    png_abs_path = os.path.join(PROJECT_ROOT, png_path_arg)
    if not os.path.isfile(png_abs_path):
        _fatal(f"PNG file not found: {png_abs_path}")

    width, height = _read_png_dimensions(png_abs_path)

    if width % 8 != 0:
        _fatal(f"PNG width ({width}) is not divisible by 8.")
    if height % 8 != 0:
        _fatal(f"PNG height ({height}) is not divisible by 8.")

    # Resolve the TEXTURE_FLAG__SIZE macro
    size_flag = _get_texture_size_flag(width, height)
    if size_flag is None:
        _fatal(f"No matching TEXTURE_FLAG__SIZE for {width}x{height}. "
               f"Supported sizes: "
               + ", ".join(f"{w}x{h}" for w, h in sorted(_TEXTURE_SIZE_FLAGS)))

    # --- Variable names (matching AncientsGame conventions) ---
    var_name = f"name_of__texture__{name_lower}"
    var_path = f"path_to__texture__{name_lower}"

    # --- Validate registrar files exist ---
    if not os.path.isfile(REGISTRAR_C_PATH):
        _fatal(f"Registrar source not found: {REGISTRAR_C_PATH}")
    if not os.path.isfile(REGISTRAR_H_PATH):
        _fatal(f"Registrar header not found: {REGISTRAR_H_PATH}")

    # ===================================================================
    # 1. Update the .c file — GEN-EXTERN region (global definitions)
    # ===================================================================
    c_text = _read(REGISTRAR_C_PATH)

    name_def_line = (
        f"Texture_Name__c_str {var_name} = \"{name_lower}\";"
    )
    path_def_line = (
        f"IO_path {var_path} = \"{png_path_arg}\";"
    )

    c_text = _insert_between_markers(
        c_text,
        "// GEN-EXTERN-BEGIN",
        "// GEN-EXTERN-END",
        name_def_line + "\n" + path_def_line,
        duplicate_check=var_name,
    )

    # ===================================================================
    # 2. Update the .c file — GEN-BEGIN region (registration call)
    # ===================================================================
    register_call = (
        f"\n"
        f"    load_texture_from__path_with__alias(\n"
        f"            p_PLATFORM_gfx_context, \n"
        f"            0, \n"
        f"            p_aliased_texture_manager, \n"
        f"            {var_name}, \n"
        f"            TEXTURE_FLAGS(\n"
        f"                {size_flag},\n"
        f"                TEXTURE_FLAG__RENDER_METHOD__0,\n"
        f"                TEXTURE_FLAG__FORMAT__RGBA8888),\n"
        f"            {var_path},\n"
        f"            0);\n"
    )

    c_text = _insert_between_markers(
        c_text,
        "// GEN-BEGIN",
        "// GEN-END",
        register_call,
        duplicate_check=var_name,
    )

    _write(REGISTRAR_C_PATH, c_text)
    print(f"[gen_aliased_texture] Updated {REGISTRAR_C_PATH}")
    print(f"  Added definition: {var_name} = \"{name_lower}\"")
    print(f"  Added definition: {var_path} = \"{png_path_arg}\"")
    print(f"  Added load_texture_from__path_with__alias call "
          f"(size: {size_flag})")

    # ===================================================================
    # 3. Update the .h file — GEN-EXTERN region (extern declarations)
    # ===================================================================
    h_text = _read(REGISTRAR_H_PATH)

    extern_name_line = f"extern Texture_Name__c_str {var_name};"
    extern_path_line = f"extern IO_path {var_path};"

    h_text = _insert_between_markers(
        h_text,
        "// GEN-EXTERN-BEGIN",
        "// GEN-EXTERN-END",
        extern_name_line + "\n" + extern_path_line,
        duplicate_check=var_name,
    )

    _write(REGISTRAR_H_PATH, h_text)
    print(f"[gen_aliased_texture] Updated {REGISTRAR_H_PATH}")
    print(f"  Added extern: {extern_name_line}")
    print(f"  Added extern: {extern_path_line}")

    print(f"[gen_aliased_texture] Done.")


if __name__ == "__main__":
    main()
