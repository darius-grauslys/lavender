#!/usr/bin/env python3
"""build_compile_commands.py — Generate compile_commands.json.

Delegates to ``make compile_commands`` which handles Bear invocation,
output paths (``build/<platform>/compile_commands.json``), and symlinking
the result to the project root.  Includes performance metrics by default.

Usage:
    python tools/lavender_tools/build_compile_commands.py --platform sdl
    python tools/lavender_tools/build_compile_commands.py --platform sdl --flags "-ggdb -w"
    python tools/lavender_tools/build_compile_commands.py --platform sdl --game-dir /path/to/MyGame
"""

from __future__ import annotations

import argparse
import multiprocessing
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
    if os.path.realpath(game_dir) == lavender_dir:
        return None
    if os.path.isfile(os.path.join(game_dir, ".lavender", "lavender.json")):
        return game_dir
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate compile_commands.json via make compile_commands.",
    )
    parser.add_argument(
        "--platform", required=True,
        choices=["sdl", "nds", "no_gui"],
        help="Target platform.",
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
    nproc = multiprocessing.cpu_count()
    game_dir = _resolve_game_dir(args.game_dir)

    # Determine output reporting path (Makefile symlinks here)
    output_dir = game_dir if game_dir else lavender_dir
    output_json = os.path.join(output_dir, "compile_commands.json")

    # Delegate to the Makefile's compile_commands target which handles
    # bear invocation, output path (build/<platform>/), and symlinking.
    cmd = [
        "make",
        "compile_commands",
        f"-j{nproc}",
        "-f", os.path.join(lavender_dir, "Makefile"),
        "-e", f"PLATFORM={args.platform}",
        "-e", f"FLAGS={args.flags}",
        "-e", "PERF_METRICS=1",
    ]

    if game_dir:
        cmd.extend(["-e", f"GAME_DIR={game_dir}"])

    print(f"=== Generating compile_commands.json ({args.platform}, -j{nproc}) ===")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"compile_commands.json written to: {output_json}")
    else:
        print(f"Build failed with exit code {result.returncode}", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
