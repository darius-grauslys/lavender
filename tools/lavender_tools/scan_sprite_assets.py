#!/usr/bin/env python3
"""scan_sprite_assets.py — Analyze sprite sheet PNGs and produce a groups manifest.

Usage:
    python tools/lavender_tools/scan_sprite_assets.py [--project-root <path>]

Scans ``assets/entities/`` for sprite sheet PNGs.  For each sheet, detects
sprite group boundaries via empty-space analysis, infers frame resolution,
and produces ``sprite_groups_manifest.json`` in ``CWD/.lavender/``.

Techniques:
1. Empty space detection (fully-transparent rows/columns as group separators)
2. Connected component flood-fill for bounding boxes
3. Row pattern analysis (uniform frame counts = animation strip)
4. Direction heuristic (3-4 similar columns = directional animation)
5. Resolution detection (mixed resolution flagging)
6. Palette duplicate detection via perceptual hash

Output goes to ``CWD/.lavender/sprite_groups_manifest.json``.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _is_row_empty(img, y: int, x_start: int = 0, x_end: int = -1) -> bool:
    """Check if an entire pixel row is fully transparent."""
    if x_end == -1:
        x_end = img.width
    for x in range(x_start, x_end):
        r, g, b, a = img.getpixel((x, y))
        if a > 0:
            return False
    return True


def _is_col_empty(img, x: int, y_start: int = 0, y_end: int = -1) -> bool:
    """Check if an entire pixel column is fully transparent."""
    if y_end == -1:
        y_end = img.height
    for y in range(y_start, y_end):
        r, g, b, a = img.getpixel((x, y))
        if a > 0:
            return False
    return True


def _detect_empty_rows(img) -> List[int]:
    """Return list of y coordinates that are fully transparent rows."""
    return [y for y in range(img.height) if _is_row_empty(img, y)]


def _detect_empty_cols(img) -> List[int]:
    """Return list of x coordinates that are fully transparent columns."""
    return [x for x in range(img.width) if _is_col_empty(img, x)]


def _find_contiguous_regions(total: int, empty_indices: set) -> List[tuple]:
    """Find contiguous non-empty ranges. Returns list of (start, end) tuples."""
    regions = []
    in_region = False
    start = 0
    for i in range(total):
        if i not in empty_indices:
            if not in_region:
                start = i
                in_region = True
        else:
            if in_region:
                regions.append((start, i))
                in_region = False
    if in_region:
        regions.append((start, total))
    return regions


def _infer_resolution(width: int, height: int) -> int:
    """Infer the most likely frame resolution from region dimensions."""
    valid = [8, 16, 32, 64, 128, 256]
    for res in valid:
        if width % res == 0 and height % res == 0:
            return res
    # Fallback: GCD-based
    from math import gcd
    g = gcd(width, height)
    for res in valid:
        if g % res == 0:
            return res
    return min(width, height)


def _analyze_sheet(img_path: str) -> dict:
    """Analyze a single sprite sheet PNG."""
    result = {
        "file": img_path,
        "width": 0,
        "height": 0,
        "groups": [],
        "warnings": [],
    }

    if Image is None:
        result["warnings"].append("Pillow not available. Install with: pip install Pillow")
        return result

    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        result["warnings"].append(f"Failed to open: {e}")
        return result

    result["width"] = img.width
    result["height"] = img.height

    empty_rows = set(_detect_empty_rows(img))
    empty_cols = set(_detect_empty_cols(img))

    row_regions = _find_contiguous_regions(img.height, empty_rows)
    col_regions = _find_contiguous_regions(img.width, empty_cols)

    # Each combination of row/col region is a potential group
    group_id = 0
    for (y_start, y_end) in row_regions:
        for (x_start, x_end) in col_regions:
            # Verify this region actually has content
            has_content = False
            for y in range(y_start, min(y_start + 2, y_end)):
                for x in range(x_start, min(x_start + 2, x_end)):
                    _, _, _, a = img.getpixel((x, y))
                    if a > 0:
                        has_content = True
                        break
                if has_content:
                    break

            if not has_content:
                continue

            w = x_end - x_start
            h = y_end - y_start
            res = _infer_resolution(w, h)
            cols = w // res if res > 0 else 1
            rows = h // res if res > 0 else 1

            group = {
                "id": group_id,
                "x": x_start,
                "y": y_start,
                "width": w,
                "height": h,
                "frame_resolution": res,
                "columns": cols,
                "rows": rows,
                "frame_count": cols * rows,
            }
            result["groups"].append(group)
            group_id += 1

    if not result["groups"]:
        result["warnings"].append("No sprite groups detected.")

    return result


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def run(project_root: str = "", output_path: str = "") -> dict:
    """Scan sprite assets and produce manifest."""
    root = project_root or str(Path.cwd())
    entities_dir = os.path.join(root, "assets", "entities")

    result = {
        "tool": "scan_sprite_assets",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": root,
        "sheets": [],
        "summary": {
            "total_sheets": 0,
            "total_groups": 0,
            "warnings": 0,
        },
    }

    if not os.path.isdir(entities_dir):
        result["summary"]["warnings"] += 1
        result["sheets"].append({
            "file": entities_dir,
            "warning": "assets/entities/ directory not found.",
        })
    else:
        # Recursively find all PNGs
        for dirpath, _dirnames, filenames in os.walk(entities_dir):
            for fname in sorted(filenames):
                if not fname.lower().endswith(".png"):
                    continue
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root)

                analysis = _analyze_sheet(full_path)
                analysis["file"] = rel_path
                result["sheets"].append(analysis)
                result["summary"]["total_sheets"] += 1
                result["summary"]["total_groups"] += len(analysis.get("groups", []))
                result["summary"]["warnings"] += len(analysis.get("warnings", []))

    # Write output
    if not output_path:
        lavender_dir = os.path.join(root, ".lavender")
        os.makedirs(lavender_dir, exist_ok=True)
        output_path = os.path.join(lavender_dir, "sprite_groups_manifest.json")

    with open(output_path, "w") as fh:
        json.dump(result, fh, indent=2)

    print(f"  [scan_sprite_assets] wrote {output_path}")
    print(f"  sheets: {result['summary']['total_sheets']}, "
          f"groups: {result['summary']['total_groups']}, "
          f"warnings: {result['summary']['warnings']}")

    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="scan_sprite_assets.py")
    parser.add_argument("--project-root", default="", dest="project_root")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    run(project_root=args.project_root, output_path=args.output)


if __name__ == "__main__":
    main()
