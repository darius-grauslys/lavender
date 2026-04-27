#!/usr/bin/env python3
"""
mod_png.py - Modify or inspect regions of a PNG image at pixel or tile
             granularity.

Usage:
    python mod_png.py \\
        --tile-size "NxN" \\
        --path <path_to_png> \\
        --op '<json_operation>' \\
        [--output <output_path>]

Operations (passed as JSON via --op):
    set    - Fill area(s) with a pixel color or tile pattern.
    swap   - Swap two equally-sized, non-overlapping areas.
    copy   - Copy the first area onto all subsequent areas.
    read   - Write sub-image(s) to stdout as concatenated PNG streams
             (pixel-only).
    resize - Resize the image canvas to the given area dimensions.  Only
             enlarging is allowed; shrinking fails at input validation.
             New pixels are filled with the specified value.

JSON schema for --op:
    {
        "op":         "set" | "swap" | "copy" | "read" | "resize",
        "type":       "pixel" | "tile",
        "areas":      [{"x": int, "y": int, "width": int, "height": int}, ...],
        "value":      "<pixel_color_or_tile_index>",   (required for 'set', 'resize')
        "value-type": "pixel" | "tile"                  (required for 'set', 'resize')
    }

Coordinate system:
    x=0, y=0 is the top-left corner of the image.
    "width" and "height" in each area are optional (default 1).

Stride ("type"):
    "pixel" - x, y, width, height are 1:1 with pixel measurements.
    "tile"  - x, y, width, height are multiplied by the tile size N.

Value formats:
    pixel value  - "R,G,B,A", "R,G,B", "#RRGGBB", or "#RRGGBBAA".
    tile index   - "col,row" identifying a tile on the tile grid.

Output path (--output):
    Optional.  When specified, the result is written to this path instead
    of modifying --path (for mutating ops) or stdout (for read).  The
    parent directory must exist and be writable.
"""

import argparse
import io
import json
import os
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


# ---------------------------------------------------------------------------
# Operation dispatch & JSON validation
# ---------------------------------------------------------------------------

VALID_OPS = {"set", "swap", "copy", "read", "resize"}
VALID_TYPES = {"pixel", "tile"}
VALID_VALUE_TYPES = {"pixel", "tile"}

# Operations that require 'value' and 'value-type'
OPS_REQUIRING_VALUE = {"set", "resize"}
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

    return op_name, img


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Modify or inspect regions of a PNG image at pixel or "
                    "tile granularity.")
    parser.add_argument(
        "--tile-size", required=True,
        help="Tile dimensions as 'NxN' where N is a power of 2 "
             "(e.g. '16x16').")
    parser.add_argument(
        "--path", required=True,
        help="Path to the target PNG file (must exist and be readable).")
    parser.add_argument(
        "--op", required=True,
        help="JSON operation object (see --help header for schema).")
    parser.add_argument(
        "--output", required=False, default=None,
        help="Optional output path.  When specified, save results here "
             "instead of modifying --path (for mutating ops) or stdout "
             "(for read).")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- Validate --tile-size ---
    try:
        tile_size = parse_tile_size(args.tile_size)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # --- Validate --path ---
    try:
        path = validate_path(args.path)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # --- Validate --output ---
    output_path = None
    if args.output:
        try:
            output_path = validate_output_path(args.output)
        except argparse.ArgumentTypeError as e:
            parser.error(str(e))

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

    # --- Save ---
    if op_name != "read":
        save_path = output_path if output_path else path
        try:
            img.save(save_path)
            print(f"Saved: {save_path}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving image: {e}", file=sys.stderr)
            sys.exit(1)
    elif output_path:
        print(f"Saved: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
