#!/usr/bin/env python3
"""scan_assets.py — Discover and classify project assets.

Usage:
    python tools/lavender_tools/scan_assets.py [--project-root <path>]

Recursively scans ``CWD/assets/`` and produces ``file_inventory.json``
in ``CWD/.lavender/``.  Each file is classified by type (sprite, tile,
ui, audio, save, unknown) and tagged with metadata.

Also validates directory structure against Lavender conventions and
reports missing expected directories.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------

_CATEGORY_MAP = {
    "assets/entities": "sprite",
    "assets/world": "tile",
    "assets/ui": "ui",
    "assets/audio": "audio",
    "assets/disk": "save",
}

_EXPECTED_DIRS = [
    "assets/entities",
    "assets/world",
    "assets/ui",
    "assets/audio",
    "assets/disk",
]


def _classify_file(rel_path: str) -> str:
    """Classify a file by its directory location."""
    for prefix, category in _CATEGORY_MAP.items():
        if rel_path.startswith(prefix):
            return category
    return "unknown"


def _get_file_info(full_path: str, root: str) -> dict:
    rel = os.path.relpath(full_path, root)
    ext = os.path.splitext(full_path)[1].lower()
    stat = os.stat(full_path)
    return {
        "path": rel,
        "extension": ext,
        "category": _classify_file(rel),
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Directory validation
# ---------------------------------------------------------------------------

def _validate_structure(root: str) -> List[dict]:
    """Check for expected Lavender directories."""
    diagnostics = []
    for expected in _EXPECTED_DIRS:
        full = os.path.join(root, expected)
        if os.path.isdir(full):
            diagnostics.append({
                "directory": expected,
                "status": "present",
            })
        else:
            diagnostics.append({
                "directory": expected,
                "status": "missing",
            })
    return diagnostics


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def run(project_root: str = "", output_path: str = "") -> dict:
    root = project_root or str(Path.cwd())
    assets_dir = os.path.join(root, "assets")

    result = {
        "tool": "scan_assets",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": root,
        "files": [],
        "directory_validation": _validate_structure(root),
        "summary": {
            "total_files": 0,
            "by_category": {},
            "missing_directories": 0,
        },
    }

    # Count missing dirs
    result["summary"]["missing_directories"] = sum(
        1 for d in result["directory_validation"] if d["status"] == "missing"
    )

    if not os.path.isdir(assets_dir):
        print(f"  [scan_assets] WARNING: {assets_dir} not found.")
    else:
        for dirpath, _dirnames, filenames in os.walk(assets_dir):
            for fname in sorted(filenames):
                full_path = os.path.join(dirpath, fname)
                info = _get_file_info(full_path, root)
                result["files"].append(info)
                result["summary"]["total_files"] += 1
                cat = info["category"]
                result["summary"]["by_category"][cat] = \
                    result["summary"]["by_category"].get(cat, 0) + 1

    # Write output
    if not output_path:
        lavender_dir = os.path.join(root, ".lavender")
        os.makedirs(lavender_dir, exist_ok=True)
        output_path = os.path.join(lavender_dir, "file_inventory.json")

    with open(output_path, "w") as fh:
        json.dump(result, fh, indent=2)

    print(f"  [scan_assets] wrote {output_path}")
    print(f"  files: {result['summary']['total_files']}, "
          f"categories: {result['summary']['by_category']}, "
          f"missing dirs: {result['summary']['missing_directories']}")

    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="scan_assets.py")
    parser.add_argument("--project-root", default="", dest="project_root")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    run(project_root=args.project_root, output_path=args.output)


if __name__ == "__main__":
    main()
