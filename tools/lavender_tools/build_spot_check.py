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


def _resolve_game_dir(explicit: str | None) -> str | None:
    """Resolve game_dir and determine if GAME_DIR should be passed to make.

    Resolution:
        1. Use --game-dir if given, otherwise use CWD.
        2. If the resolved dir has .lavender/lavender.json AND is not
           $LAVENDER_DIR itself, it is a game project → return its path.
        3. Otherwise it is an engine-only context → return None.
    """
    game_dir = os.path.abspath(explicit) if explicit else os.getcwd()
    lavender_dir = os.path.realpath(_get_lavender_dir())
    # Engine directory → engine-only build, no GAME_DIR
    if os.path.realpath(game_dir) == lavender_dir:
        return None
    # Game project → has .lavender/lavender.json
    if os.path.isfile(os.path.join(game_dir, ".lavender", "lavender.json")):
        return game_dir
    return None


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
             "Defaults to CWD if CWD is a Lavender project.",
    )
    args = parser.parse_args()

    lavender_dir = _get_lavender_dir()
    game_dir = _resolve_game_dir(args.game_dir)

    cmd = [
        "make",
        "-f", os.path.join(lavender_dir, "Makefile"),
        "check-file",
        "-e", f"PLATFORM={args.platform}",
        "-e", f"FLAGS={args.flags}",
        "-e", f"FILE={args.file}",
    ]

    if game_dir:
        cmd.extend(["-e", f"GAME_DIR={game_dir}"])

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
