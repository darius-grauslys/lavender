#!/usr/bin/env python3
"""
mod_png.py - Modify or inspect regions of a PNG image at pixel or tile
             granularity.

Usage:
    # Standard operation mode:
    python mod_png.py \\
        --tile-size "NxN" \\
        --path <path_to_png> \\
        --op '<json_operation>' \\
        [--output <output_path>]

    # Image info mode (no --op or --tile-size required):
    python mod_png.py --path <path_to_png>

Operations (passed as JSON via --op):
    set      - Fill area(s) with a pixel color or tile pattern.
    swap     - Swap two equally-sized, non-overlapping areas.
    copy     - Copy the first area onto all subsequent areas.
    read     - Write sub-image(s) to stdout as concatenated PNG streams
               (pixel-only).
    resize   - Resize the image canvas to the given area dimensions.  Only
               enlarging is allowed; shrinking fails at input validation.
               New pixels are filled with the specified value.
    condense - Identify fill-only tiles within area(s) and pack non-fill
               tiles into the smallest possible rectangle.  The image is
               then cropped to remove trailing fill regions.  Requires
               --output (must be in same directory or subdirectory as
               --path).  See 'Condense operation' section below.

JSON schema for --op:
    {
        "op":         "set" | "swap" | "copy" | "read" | "resize"
                      | "condense",
        "type":       "pixel" | "tile",
        "areas":      [{"x": int, "y": int, "width": int, "height": int},
                       ...],
        "value":      "<pixel_color_or_tile_index>",
                      (required for 'set', 'resize', 'condense')
        "value-type": "pixel" | "tile"
                      (required for 'set', 'resize';
                       must be "pixel" for 'condense')
    }

Coordinate system:
    x=0, y=0 is the top-left corner of the image.
    "width" and "height" in each area are optional (default 1).

Stride ("type"):
    "pixel" - x, y, width, height are 1:1 with pixel measurements.
    "tile"  - x, y, width, height are multiplied by the tile size N.

Value formats ("value"):
    pixel color  - "R,G,B,A", "R,G,B", "#RRGGBB", or "#RRGGBBAA".
                   Each component is an integer 0-255.  For RGBA images,
                   "R,G,B" is treated as "R,G,B,255" (fully opaque).
                   For transparent fill use "0,0,0,0".
    tile index   - "col,row" identifying a tile on the tile grid.

Output path (--output):
    Optional for most ops; required for 'condense'.  When specified,
    results are written here instead of modifying --path.  The parent
    directory must exist and be writable.

    For 'condense', --output must reside in the same directory as --path
    or in a subdirectory thereof.  --output must NOT have a basename
    starting with "ORIGINAL_" (that prefix is reserved).

Condense operation:
    The condense op removes empty (fill-only) tiles from within
    specified area(s) and packs the remaining tiles compactly.

    Algorithm:
      1. For each area, build a boolean grid (tile_w x tile_h).
      2. Each tile whose pixel data exactly matches the fill color
         (given by "value" with "value-type": "pixel") is marked fill.
      3. All non-fill tiles are collected as sub-images.
      4. Non-fill tiles are packed left-to-right, top-to-bottom into
         the area starting from the area origin, using a near-square
         layout.
      5. Remaining area space is filled with the fill color.
      6. After all areas are processed, the image is cropped to the
         tight tile-aligned bounding box of non-fill content.

    The resulting image dimensions are printed to stdout as "WxH".

Original-file preservation (.lav_ai_mod_png.json):
    ALL modifying operations (set, swap, copy, resize, condense)
    preserve the original input file and track the relationship in a
    JSON file named ".lav_ai_mod_png.json" in the same directory as
    --path.

    Behaviour:
      - If the --path basename does not start with "ORIGINAL_" and no
        file named "ORIGINAL_<basename>" exists, --path is renamed to
        "ORIGINAL_<basename>" before saving the result.
      - The JSON file records mappings from modified/output filenames
        to their true original.  Keys are paths relative to the JSON
        file's directory.
      - When re-modifying a previously modified file, the tool follows
        the JSON chain to preserve the link to the true original
        (never the intermediate).
      - "ORIGINAL_"-prefixed files are never overwritten by the rename.

    JSON format example:
        {
            "Frames.png": "ORIGINAL_Frames.png",
            "condensed/Frames.png": "ORIGINAL_Frames.png"
        }

Image-info mode:
    When only --path is supplied (no --op or --tile-size), the tool
    prints the image format (mode), pixel dimensions, and the full
    image contents as a Base64-encoded PNG to stdout, then exits
    without modifying any file:
        format=RGBA size=848x928
        base64=iVBORw0KGgoAAAANSUhEUgAA...

    The base64 line contains the complete PNG file encoded in
    standard Base64 (RFC 4648).  AI agents can decode this value to
    inspect image contents programmatically.

Size reporting:
    After every operation, the resulting image dimensions are printed
    to stdout as "WxH" (e.g. "576x576").

Timeout:
    A 15-second wall-clock timeout protects against infinite loops or
    unexpectedly long operations.  If the timeout triggers, no files
    are written and the tool exits with a non-zero status.
"""

import argparse
import base64
import io
import json
import math
import os
import signal
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow",
          file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_power_of_two(n):
    """Return True if *n* is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


def parse_tile_size(value):
    """Parse 'NxN' and validate N is a power of 2.  Returns N."""
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"--tile-size must be in 'NxN' format, got: '{value}'")
    try:
        w, h = int(parts[0]), int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--tile-size components must be integers, got: '{value}'")
    if w != h:
        raise argparse.ArgumentTypeError(
            f"--tile-size must be square (NxN), got: '{value}'")
    if not is_power_of_two(w):
        raise argparse.ArgumentTypeError(
            f"--tile-size N must be a power of 2, got: {w}")
    return w


def validate_path(path):
    """Validate that *path* exists and is a readable file."""
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File not found: '{path}'")
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(f"File is not readable: '{path}'")
    return path


def validate_output_path(path):
    """Validate that the parent directory of *path* exists and is writable."""
    parent = os.path.dirname(path) or "."
    if not os.path.isdir(parent):
        raise argparse.ArgumentTypeError(
            f"Output directory does not exist: '{parent}'")
    if not os.access(parent, os.W_OK):
        raise argparse.ArgumentTypeError(
            f"Output directory is not writable: '{parent}'")
    return path


# ---------------------------------------------------------------------------
# Timeout guard
# ---------------------------------------------------------------------------

_TIMEOUT_SECONDS = 15


def _timeout_handler(_signum, _frame):
    """SIGALRM handler -- abort without writing any files."""
    print(f"Error: Operation timed out ({_TIMEOUT_SECONDS}s). "
          "No files written.", file=sys.stderr)
    # Use os._exit to guarantee immediate termination without cleanup
    # that might itself hang.
    os._exit(1)


# ---------------------------------------------------------------------------
# .lav_ai_mod_png.json helpers
#
# Every modifying operation (set, swap, copy, resize, condense) preserves
# the original input file by renaming it with an "ORIGINAL_" prefix and
# recording the mapping in a per-directory JSON tracking file.  See the
# module docstring for full details.
# ---------------------------------------------------------------------------

_LAV_JSON_NAME = ".lav_ai_mod_png.json"


def _load_lav_json(directory):
    """Load the tracking JSON from *directory*, or return ``{}``."""
    p = os.path.join(directory, _LAV_JSON_NAME)
    if os.path.isfile(p):
        with open(p, "r") as fh:
            return json.load(fh)
    return {}


def _save_lav_json(directory, data):
    """Persist *data* as the tracking JSON in *directory*."""
    p = os.path.join(directory, _LAV_JSON_NAME)
    with open(p, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _resolve_true_original(path):
    """Return the true-original basename for *path*, or ``None``.

    * If *basename* starts with ``ORIGINAL_``, it **is** the original.
    * Otherwise consult the tracking JSON for an existing mapping.
    * If no mapping is found return ``None`` -- the caller should treat
      the file itself as the original and rename it.
    """
    abspath = os.path.abspath(path)
    directory = os.path.dirname(abspath)
    basename = os.path.basename(abspath)

    if basename.startswith("ORIGINAL_"):
        return basename

    data = _load_lav_json(directory)
    return data.get(basename)


def _handle_original_preservation(path, output_path):
    """Rename *path* to ``ORIGINAL_<name>`` and update the tracking JSON.

    Called for every mutating operation so that the pristine input is
    always recoverable.  Returns the true-original basename.

    Rules applied in order:

    1. If *path* basename already starts with ``ORIGINAL_``, skip the
       rename -- it **is** the original.
    2. If the JSON already maps *basename* to an original, reuse that
       mapping (supports re-modification without losing the chain).
    3. Otherwise rename *path* -> ``ORIGINAL_<basename>`` on disk
       (unless that file already exists -- never overwrite the
       original).
    4. Update the JSON so both the working file and (if provided) the
       ``--output`` file point to the true original.
    """
    abspath = os.path.abspath(path)
    directory = os.path.dirname(abspath)
    basename = os.path.basename(abspath)

    true_original = _resolve_true_original(path)

    if true_original is None:
        # This file is the (first-ever) original -- rename it.
        original_name = "ORIGINAL_" + basename
        original_disk = os.path.join(directory, original_name)
        if not os.path.exists(original_disk):
            os.rename(abspath, original_disk)
        true_original = original_name

    # ---- Update tracking JSON ----
    data = _load_lav_json(directory)

    if output_path:
        out_abs = os.path.abspath(output_path)
        out_rel = os.path.relpath(out_abs, directory)
        data[out_rel] = true_original

    # Ensure the working-path basename is mapped too (in-place or alias).
    if not basename.startswith("ORIGINAL_"):
        data[basename] = true_original

    _save_lav_json(directory, data)
    return true_original


# ---------------------------------------------------------------------------
# Pixel / tile value parsing
# ---------------------------------------------------------------------------

def parse_pixel_value(value_str, mode):
    """
    Parse a pixel color string into a tuple matching *mode*.

    Accepted formats:
        "R,G,B,A"    -> (R, G, B, A)         for RGBA
        "R,G,B"      -> (R, G, B) or + A=255  for RGBA
        "#RRGGBB"    -> (R, G, B[, 255])
        "#RRGGBBAA"  -> (R, G, B, A)
    """
    value_str = value_str.strip()

    if value_str.startswith("#"):
        hex_str = value_str[1:]
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            if mode == "RGBA":
                return (r, g, b, 255)
            return (r, g, b)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            if mode == "RGBA":
                return (r, g, b, a)
            return (r, g, b)
        else:
            raise ValueError(
                f"Hex color must be #RRGGBB or #RRGGBBAA, "
                f"got: '{value_str}'")

    # Comma-separated decimal components
    parts = [int(p.strip()) for p in value_str.split(",")]
    for v in parts:
        if v < 0 or v > 255:
            raise ValueError(
                f"Color component out of range 0-255: {v} in '{value_str}'")

    if mode == "RGBA":
        if len(parts) == 4:
            return tuple(parts)
        elif len(parts) == 3:
            return (parts[0], parts[1], parts[2], 255)
        else:
            raise ValueError(
                f"Pixel value '{value_str}' needs 3 or 4 components for "
                f"RGBA mode, got {len(parts)}")
    elif mode == "RGB":
        if len(parts) == 3:
            return tuple(parts)
        else:
            raise ValueError(
                f"Pixel value '{value_str}' needs 3 components for "
                f"RGB mode, got {len(parts)}")
    elif mode in ("L", "P"):
        if len(parts) == 1:
            return parts[0]
        else:
            raise ValueError(
                f"Pixel value '{value_str}' needs 1 component for "
                f"'{mode}' mode, got {len(parts)}")
    else:
        raise ValueError(f"Unsupported image mode '{mode}'")


def parse_tile_index(value_str):
    """Parse 'col,row' tile index string.  Returns (col, row) as ints."""
    parts = value_str.strip().split(",")
    if len(parts) != 2:
        raise ValueError(
            f"Tile index must be 'col,row', got: '{value_str}'")
    try:
        col, row = int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        raise ValueError(
            f"Tile index components must be integers, got: '{value_str}'")
    if col < 0 or row < 0:
        raise ValueError(
            f"Tile index must be non-negative, got: ({col},{row})")
    return col, row


# ---------------------------------------------------------------------------
# Area / rectangle helpers
# ---------------------------------------------------------------------------

def resolve_area(area_dict, tile_size, stride_type, img_width, img_height):
    """
    Convert an area dict to pixel-space (px_x, px_y, px_w, px_h).
    Validates that the area lies within image bounds.
    """
    x = area_dict["x"]
    y = area_dict["y"]
    w = area_dict.get("width", 1)
    h = area_dict.get("height", 1)

    if w <= 0 or h <= 0:
        raise ValueError(
            f"Area width and height must be positive non-zero, "
            f"got width={w}, height={h}")

    if stride_type == "tile":
        px_x = x * tile_size
        px_y = y * tile_size
        px_w = w * tile_size
        px_h = h * tile_size
    else:
        px_x = x
        px_y = y
        px_w = w
        px_h = h

    if px_x < 0 or px_y < 0:
        raise ValueError(
            f"Area origin must be non-negative, got ({px_x}, {px_y})")
    if px_x + px_w > img_width or px_y + px_h > img_height:
        raise ValueError(
            f"Area ({px_x},{px_y})+({px_w}x{px_h}) extends beyond "
            f"image bounds ({img_width}x{img_height})")

    return px_x, px_y, px_w, px_h


def areas_overlap(a, b):
    """Check if two pixel-space rectangles (x, y, w, h) overlap."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or
                ay + ah <= by or by + bh <= ay)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def op_set(img, areas, tile_size, stride_type, value_str, value_type):
    """
    Set area(s) to a pixel color or tile pattern.

    value-type "pixel": fill every pixel in each area with the given color.
    value-type "tile":  copy the referenced tile, repeating it to fill each
                        area.
    """
    if value_str is None:
        raise ValueError("'set' operation requires a 'value'.")
    if value_type is None:
        raise ValueError("'set' operation requires a 'value-type'.")

    img_w, img_h = img.size

    if value_type == "pixel":
        color = parse_pixel_value(value_str, img.mode)
        for area_dict in areas:
            px_x, px_y, px_w, px_h = resolve_area(
                area_dict, tile_size, stride_type, img_w, img_h)
            # Use a solid-color image + paste for speed on large regions
            fill = Image.new(img.mode, (px_w, px_h), color)
            img.paste(fill, (px_x, px_y))

    elif value_type == "tile":
        col, row = parse_tile_index(value_str)
        src_x = col * tile_size
        src_y = row * tile_size
        if src_x + tile_size > img_w or src_y + tile_size > img_h:
            raise ValueError(
                f"Source tile ({col},{row}) at pixel ({src_x},{src_y}) "
                f"extends beyond image bounds ({img_w}x{img_h}).")
        tile_img = img.crop(
            (src_x, src_y, src_x + tile_size, src_y + tile_size)).copy()

        for area_dict in areas:
            px_x, px_y, px_w, px_h = resolve_area(
                area_dict, tile_size, stride_type, img_w, img_h)
            # Tile the source tile across the target area
            for ty in range(0, px_h, tile_size):
                for tx in range(0, px_w, tile_size):
                    paste_w = min(tile_size, px_w - tx)
                    paste_h = min(tile_size, px_h - ty)
                    if paste_w == tile_size and paste_h == tile_size:
                        img.paste(tile_img, (px_x + tx, px_y + ty))
                    else:
                        cropped = tile_img.crop((0, 0, paste_w, paste_h))
                        img.paste(cropped, (px_x + tx, px_y + ty))
    else:
        raise ValueError(f"Invalid value-type for 'set': '{value_type}'")


def op_swap(img, areas, tile_size, stride_type):
    """Swap two equally-sized, non-overlapping areas."""
    if len(areas) != 2:
        raise ValueError("'swap' operation requires exactly 2 areas.")

    img_w, img_h = img.size
    a = resolve_area(areas[0], tile_size, stride_type, img_w, img_h)
    b = resolve_area(areas[1], tile_size, stride_type, img_w, img_h)

    if (a[2], a[3]) != (b[2], b[3]):
        raise ValueError(
            f"'swap' areas must be the same size. "
            f"Got {a[2]}x{a[3]} and {b[2]}x{b[3]}.")

    if areas_overlap(a, b):
        raise ValueError("'swap' areas must not overlap.")

    ax, ay, aw, ah = a
    bx, by, _bw, _bh = b

    region_a = img.crop((ax, ay, ax + aw, ay + ah)).copy()
    region_b = img.crop((bx, by, bx + aw, by + ah)).copy()

    img.paste(region_b, (ax, ay))
    img.paste(region_a, (bx, by))


def op_copy(img, areas, tile_size, stride_type):
    """Copy the first area onto all subsequent areas."""
    if len(areas) < 2:
        raise ValueError("'copy' operation requires at least 2 areas.")

    img_w, img_h = img.size
    src = resolve_area(areas[0], tile_size, stride_type, img_w, img_h)
    sx, sy, sw, sh = src

    source_region = img.crop((sx, sy, sx + sw, sy + sh)).copy()

    for area_dict in areas[1:]:
        dst = resolve_area(area_dict, tile_size, stride_type, img_w, img_h)
        dx, dy, dw, dh = dst
        if (dw, dh) != (sw, sh):
            raise ValueError(
                f"'copy' destination area ({dw}x{dh}) differs from "
                f"source area ({sw}x{sh}).")
        img.paste(source_region, (dx, dy))


def op_read(img, areas, tile_size, stride_type, output_path=None):
    """Write sub-images to stdout (or to *output_path*) as concatenated PNG streams (pixel-only)."""
    if stride_type != "pixel":
        raise ValueError("'read' operation only supports type 'pixel'.")

    img_w, img_h = img.size

    if output_path is not None:
        sink = open(output_path, 'wb')
    else:
        sink = sys.stdout.buffer

    try:
        for area_dict in areas:
            px_x, px_y, px_w, px_h = resolve_area(
                area_dict, tile_size, stride_type, img_w, img_h)
            sub = img.crop((px_x, px_y, px_x + px_w, px_y + px_h))
            buf = io.BytesIO()
            sub.save(buf, format="PNG")
            sink.write(buf.getvalue())
        sink.flush()
    finally:
        if output_path is not None:
            sink.close()


def op_resize(img, areas, tile_size, stride_type, value_str, value_type):
    """Resize the image canvas to the dimensions given by a single area.

    Only enlarging is permitted — if the requested dimensions are smaller
    than the current image in either axis the operation fails immediately
    at input validation (before any pixel work).  The original image
    content is pasted at (0, 0) and all new pixels are filled with the
    colour specified by *value_str* (value-type must be "pixel").

    Returns a **new** Image instance with the resized canvas.
    """
    if len(areas) != 1:
        raise ValueError("'resize' operation requires exactly 1 area.")
    if value_str is None:
        raise ValueError("'resize' operation requires a 'value'.")
    if value_type is None:
        raise ValueError("'resize' operation requires a 'value-type'.")
    if value_type != "pixel":
        raise ValueError(
            "'resize' value-type must be 'pixel', got: "
            f"'{value_type}'.")

    area = areas[0]
    # For resize the area x,y must be 0,0 (we resize the canvas, not a
    # sub-region) and width/height are required.
    if area.get("x", 0) != 0 or area.get("y", 0) != 0:
        raise ValueError(
            "'resize' area must have x=0 and y=0 (canvas resize).")
    if "width" not in area or "height" not in area:
        raise ValueError(
            "'resize' area must specify both 'width' and 'height'.")

    if stride_type == "tile":
        new_w = area["width"] * tile_size
        new_h = area["height"] * tile_size
    else:
        new_w = area["width"]
        new_h = area["height"]

    img_w, img_h = img.size

    if new_w < img_w or new_h < img_h:
        raise ValueError(
            f"'resize' can only enlarge the image.  Current size "
            f"({img_w}x{img_h}), requested ({new_w}x{new_h}).")

    if new_w == img_w and new_h == img_h:
        # No-op — nothing to resize.
        return img

    fill_color = parse_pixel_value(value_str, img.mode)
    new_img = Image.new(img.mode, (new_w, new_h), fill_color)
    new_img.paste(img, (0, 0))
    return new_img


def op_condense(img, areas, tile_size, stride_type, value_str, value_type):
    """Condense tiles within area(s) by removing fill-only tiles.

    Identifies tiles whose pixel data exactly matches the fill colour
    (given by *value_str*) and packs all remaining (non-fill) tiles
    into the smallest near-square rectangle, arranged left-to-right
    then top-to-bottom from each area's origin.  Remaining space is
    filled with the fill colour.

    After all areas are processed the image is cropped to the tight
    tile-aligned bounding box of non-fill content.

    Returns a (possibly smaller) ``Image``.
    """
    if value_str is None:
        raise ValueError("'condense' operation requires a 'value'.")
    if value_type is None:
        raise ValueError("'condense' operation requires a 'value-type'.")
    if value_type != "pixel":
        raise ValueError(
            "'condense' value-type must be 'pixel', got: "
            f"'{value_type}'.")

    img_w, img_h = img.size
    fill_color = parse_pixel_value(value_str, img.mode)

    # Pre-build a reference fill tile for fast byte-level comparison.
    fill_tile_ref = Image.new(img.mode, (tile_size, tile_size), fill_color)
    fill_bytes = fill_tile_ref.tobytes()

    for area_dict in areas:
        px_x, px_y, px_w, px_h = resolve_area(
            area_dict, tile_size, stride_type, img_w, img_h)

        # Area dimensions must be evenly divisible by tile_size.
        if px_w % tile_size != 0 or px_h % tile_size != 0:
            raise ValueError(
                f"Area pixel dimensions ({px_w}x{px_h}) must be evenly "
                f"divisible by tile size ({tile_size}).  "
                f"Remainders: w%{tile_size}={px_w % tile_size}, "
                f"h%{tile_size}={px_h % tile_size}.")

        grid_w = px_w // tile_size
        grid_h = px_h // tile_size

        # ----- Collect non-fill tiles (BEFORE any area mutation) -----
        non_fill_tiles = []
        for gy in range(grid_h):
            for gx in range(grid_w):
                tx = px_x + gx * tile_size
                ty = px_y + gy * tile_size
                crop = img.crop((tx, ty, tx + tile_size, ty + tile_size))
                if crop.tobytes() != fill_bytes:
                    # .copy() severs the lazy reference so the data is
                    # safe even after we overwrite the area below.
                    non_fill_tiles.append(crop.copy())

        n = len(non_fill_tiles)

        # ----- Fill the entire area with fill colour -----
        area_fill = Image.new(img.mode, (px_w, px_h), fill_color)
        img.paste(area_fill, (px_x, px_y))

        if n == 0:
            continue  # Entire area was fill -- nothing to paste back.

        # ----- Compute packing layout (near-square, bounded by area) -----
        cols = min(grid_w, math.ceil(math.sqrt(n)))
        rows = math.ceil(n / cols)

        # If the computed rows exceed the area height, widen until it
        # fits.  The loop is bounded: at worst cols == grid_w and
        # rows <= grid_h (since n <= grid_w * grid_h).
        attempts = 0
        max_attempts = grid_w  # Upper bound on widening
        while rows > grid_h and attempts < max_attempts:
            cols += 1
            rows = math.ceil(n / cols)
            attempts += 1

        if cols > grid_w or rows > grid_h:
            raise ValueError(
                f"Internal error: packing {n} tiles into "
                f"{grid_w}x{grid_h} grid failed (computed "
                f"{cols}x{rows}).  This should not happen.")

        # ----- Paste non-fill tiles back into the area -----
        for i, tile_img in enumerate(non_fill_tiles):
            dc = i % cols
            dr = i // cols
            dx = px_x + dc * tile_size
            dy = px_y + dr * tile_size
            img.paste(tile_img, (dx, dy))

    # ----- Crop image to tight tile-aligned bounding box -----
    img_w, img_h = img.size
    max_x = 0
    max_y = 0
    for ty in range(0, img_h, tile_size):
        for tx in range(0, img_w, tile_size):
            crop = img.crop((tx, ty, tx + tile_size, ty + tile_size))
            if crop.tobytes() != fill_bytes:
                max_x = max(max_x, tx + tile_size)
                max_y = max(max_y, ty + tile_size)

    # Degenerate case: entire image is fill.
    if max_x == 0 or max_y == 0:
        max_x = tile_size
        max_y = tile_size

    if max_x < img_w or max_y < img_h:
        img = img.crop((0, 0, max_x, max_y)).copy()

    return img


# ---------------------------------------------------------------------------
# Operation dispatch & JSON validation
# ---------------------------------------------------------------------------

VALID_OPS = {"set", "swap", "copy", "read", "resize", "condense"}
VALID_TYPES = {"pixel", "tile"}
VALID_VALUE_TYPES = {"pixel", "tile"}

# Operations that require 'value' and 'value-type'
OPS_REQUIRING_VALUE = {"set", "resize", "condense"}
# Operations restricted to pixel stride only
OPS_PIXEL_ONLY = {"read"}


def validate_op_schema(op_obj):
    """
    Validate the --op JSON object against the expected schema.
    Returns (op_name, stride_type, areas, value_str, value_type).
    """
    if not isinstance(op_obj, dict):
        raise ValueError("--op must be a JSON object.")

    # --- op ---
    op_name = op_obj.get("op")
    if op_name not in VALID_OPS:
        raise ValueError(
            f"'op' must be one of {sorted(VALID_OPS)}, got: '{op_name}'")

    # --- type ---
    stride_type = op_obj.get("type")
    if stride_type not in VALID_TYPES:
        raise ValueError(
            f"'type' must be one of {sorted(VALID_TYPES)}, "
            f"got: '{stride_type}'")

    if op_name in OPS_PIXEL_ONLY and stride_type != "pixel":
        raise ValueError(
            f"'{op_name}' operation only supports type 'pixel'.")

    # --- areas ---
    areas = op_obj.get("areas")
    if not isinstance(areas, list) or len(areas) == 0:
        raise ValueError("'areas' must be a non-empty list.")

    for i, area in enumerate(areas):
        if not isinstance(area, dict):
            raise ValueError(f"areas[{i}] must be an object.")
        if "x" not in area or "y" not in area:
            raise ValueError(f"areas[{i}] must have 'x' and 'y' keys.")
        if not isinstance(area["x"], int) or not isinstance(area["y"], int):
            raise ValueError(f"areas[{i}] 'x' and 'y' must be integers.")
        for dim in ("width", "height"):
            if dim in area:
                if not isinstance(area[dim], int) or area[dim] <= 0:
                    raise ValueError(
                        f"areas[{i}] '{dim}' must be a positive non-zero "
                        f"integer, got: {area.get(dim)}")

    # --- value / value-type ---
    value_str = op_obj.get("value")
    value_type = op_obj.get("value-type")

    if op_name in OPS_REQUIRING_VALUE:
        if value_str is None:
            raise ValueError(f"'{op_name}' operation requires 'value'.")
        if value_type is None:
            raise ValueError(f"'{op_name}' operation requires 'value-type'.")
    if value_type is not None and value_type not in VALID_VALUE_TYPES:
        raise ValueError(
            f"'value-type' must be one of {sorted(VALID_VALUE_TYPES)}, "
            f"got: '{value_type}'")

    # --- condense-specific checks ---
    if op_name == "condense" and value_type != "pixel":
        raise ValueError(
            "'condense' requires value-type 'pixel', "
            f"got: '{value_type}'.")

    return op_name, stride_type, areas, value_str, value_type


def execute_op(img, tile_size, op_name, stride_type, areas, value_str,
               value_type, output_path=None):
    """Dispatch to the appropriate operation handler.

    Returns ``(op_name, img)`` — the image reference may change for
    operations like ``resize`` that produce a new canvas.
    """
    if op_name == "set":
        op_set(img, areas, tile_size, stride_type, value_str, value_type)
    elif op_name == "swap":
        op_swap(img, areas, tile_size, stride_type)
    elif op_name == "copy":
        op_copy(img, areas, tile_size, stride_type)
    elif op_name == "read":
        op_read(img, areas, tile_size, stride_type, output_path=output_path)
    elif op_name == "resize":
        img = op_resize(img, areas, tile_size, stride_type, value_str,
                        value_type)
    elif op_name == "condense":
        img = op_condense(img, areas, tile_size, stride_type, value_str,
                          value_type)

    return op_name, img


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Modify or inspect regions of a PNG image at pixel or "
                    "tile granularity.  Supply only --path for image-info "
                    "mode (prints format and size).")
    parser.add_argument(
        "--tile-size", required=False, default=None,
        help="Tile dimensions as 'NxN' where N is a power of 2 "
             "(e.g. '16x16').  Required for all operations; omit "
             "together with --op for image-info mode.")
    parser.add_argument(
        "--path", required=True,
        help="Path to the target PNG file (must exist and be readable).")
    parser.add_argument(
        "--op", required=False, default=None,
        help="JSON operation object (see --help header for schema).  "
             "Omit together with --tile-size for image-info mode.")
    parser.add_argument(
        "--output", required=False, default=None,
        help="Optional output path.  When specified, save results here "
             "instead of modifying --path (for mutating ops) or stdout "
             "(for read).  REQUIRED for 'condense'; must be in same "
             "directory or subdirectory of --path; must not start with "
             "'ORIGINAL_'.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- Install timeout guard (Linux SIGALRM) ---
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(_TIMEOUT_SECONDS)

    # --- Validate --path ---
    try:
        path = validate_path(args.path)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # --- Image-info mode (only --path supplied) ---
    if args.op is None and args.tile_size is None:
        try:
            img = Image.open(path)
            img.load()
        except Exception as e:
            parser.error(f"Failed to open image '{path}': {e}")
        w, h = img.size
        print(f"format={img.mode} size={w}x{h}")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        print(f"base64={b64}")
        signal.alarm(0)
        return

    # Both --tile-size and --op are required for operation mode.
    if args.tile_size is None:
        parser.error("--tile-size is required when --op is specified.")
    if args.op is None:
        parser.error("--op is required when --tile-size is specified.")

    # --- Validate --tile-size ---
    try:
        tile_size = parse_tile_size(args.tile_size)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # --- Validate --output ---
    output_path = None
    if args.output:
        try:
            output_path = validate_output_path(args.output)
        except argparse.ArgumentTypeError as e:
            parser.error(str(e))

    # --- Reject ORIGINAL_-prefixed output targets ---
    if output_path is not None:
        out_basename = os.path.basename(output_path)
        if out_basename.startswith("ORIGINAL_"):
            parser.error(
                f"--output must not target an ORIGINAL_-prefixed file "
                f"(reserved for original preservation).  "
                f"Got: '{out_basename}'")

    # --- Parse --op JSON ---
    try:
        op_obj = json.loads(args.op)
    except json.JSONDecodeError as e:
        parser.error(f"Invalid JSON for --op: {e}")

    # --- Validate schema ---
    try:
        op_name, stride_type, areas, value_str, value_type = \
            validate_op_schema(op_obj)
    except ValueError as e:
        parser.error(str(e))

    # --- Condense-specific validation ---
    if op_name == "condense":
        if not path.lower().endswith(".png"):
            parser.error("--path must be a .png file for 'condense'.")
        if output_path is None:
            parser.error("--output is required for 'condense' operation.")
        # --output must be in same directory or a subdirectory of --path
        path_dir = os.path.abspath(os.path.dirname(os.path.abspath(path)))
        out_dir = os.path.abspath(
            os.path.dirname(os.path.abspath(output_path)))
        # Use os.sep to ensure proper prefix comparison.
        if out_dir != path_dir and not out_dir.startswith(path_dir + os.sep):
            parser.error(
                f"--output directory must be the same as or a "
                f"subdirectory of --path directory.\n"
                f"  --path dir:   {path_dir}\n"
                f"  --output dir: {out_dir}")

    # --- Load image ---
    try:
        img = Image.open(path)
        img.load()  # Force load so we detect read errors early
    except Exception as e:
        parser.error(f"Failed to open image '{path}': {e}")

    # --- Execute operation ---
    try:
        op_name, img = execute_op(img, tile_size, op_name, stride_type,
                                  areas, value_str, value_type,
                                  output_path=output_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Save (mutating operations) ---
    if op_name != "read":
        save_path = output_path if output_path else path

        # -- Original-file preservation --
        try:
            _handle_original_preservation(path, output_path)
        except Exception as e:
            print(f"Warning: original preservation failed: {e}",
                  file=sys.stderr)

        try:
            img.save(save_path)
            print(f"Saved: {save_path}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving image: {e}", file=sys.stderr)
            sys.exit(1)
    elif output_path:
        print(f"Saved: {output_path}", file=sys.stderr)

    # --- Always report resulting image size ---
    w, h = img.size
    if op_name == "read" and not output_path:
        # Binary PNG data already occupies stdout -- use stderr.
        print(f"{w}x{h}", file=sys.stderr)
    else:
        print(f"{w}x{h}")

    # --- Cancel timeout ---
    signal.alarm(0)


if __name__ == "__main__":
    main()
