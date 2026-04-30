#!/usr/bin/env python3
"""build_spot_check.py — Validate a single C module without producing an object file.

Runs clang -fsyntax-only with the full build flag chain (CFLAGS, INCLUDE,
FLAGS) to perform preprocessing, parsing, and semantic analysis.  This is
the fastest possible correctness check for a single source file.

Exit 0 means the module compiles cleanly.  Non-zero means errors were found;
diagnostics are printed to stderr.

Usage:
    python tools/build_spot_check.py --platform sdl --file core/source/input/input.c
    python tools/build_spot_check.py --platform sdl --file /abs/path/to/file.c --flags "-ggdb"
    python tools/build_spot_check.py --platform sdl --file source/my_scene.c --game-dir /path/to/MyGame
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _get_lavender_dir() -> str:
    """Resolve LAVENDER_DIR from environment or script location."""
    env = os.environ.get("LAVENDER_DIR")
    if env:
        return env
    return str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Spot-check a single C module with -fsyntax-only.",
    )
    parser.add_argument(
        "--platform", required=True,
        choices=["sdl", "nds", "no_gui"],
        help="Target platform.",
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to the .c file to check. "
             "Absolute or relative to CWD.",
    )
    parser.add_argument(
        "--flags", default="-w",
        help='Compiler FLAGS passed to make (default: "-w").',
    )
    parser.add_argument(
        "--game-dir", default=None,
        help="Path to a game project directory. "
             "Omit to check against the engine standalone.",
    )
    args = parser.parse_args()

    lavender_dir = _get_lavender_dir()

    cmd = [
        "make",
        "-f", os.path.join(lavender_dir, "Makefile"),
        "check-file",
        "-e", f"PLATFORM={args.platform}",
        "-e", f"FLAGS={args.flags}",
        "-e", f"FILE={args.file}",
    ]

    if args.game_dir:
        cmd.extend(["-e", f"GAME_DIR={os.path.abspath(args.game_dir)}"])

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
