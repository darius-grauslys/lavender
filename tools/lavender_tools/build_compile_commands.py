#!/usr/bin/env python3
"""build_compile_commands.py — Generate compile_commands.json.

Runs a build via Bear to intercept compiler invocations and produce
compile_commands.json at the project root.  Includes performance
metrics by default.

Usage:
    python tools/build_compile_commands.py --platform sdl
    python tools/build_compile_commands.py --platform sdl --flags "-ggdb -w"
    python tools/build_compile_commands.py --platform sdl --game-dir /path/to/MyGame
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate compile_commands.json via Bear.",
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
             "Omit to build the engine standalone.",
    )
    args = parser.parse_args()

    lavender_dir = _get_lavender_dir()
    nproc = multiprocessing.cpu_count()

    # Determine output location for compile_commands.json
    game_dir = os.path.abspath(args.game_dir) if args.game_dir else lavender_dir
    output_json = os.path.join(game_dir, "compile_commands.json")

    make_cmd = [
        "make",
        f"-j{nproc}",
        "-f", os.path.join(lavender_dir, "Makefile"),
        "-e", f"PLATFORM={args.platform}",
        "-e", f"FLAGS={args.flags}",
        "-e", "PERF_METRICS=1",
    ]

    if args.game_dir:
        make_cmd.extend(["-e", f"GAME_DIR={os.path.abspath(args.game_dir)}"])

    # Wrap with Bear
    cmd = [
        "bear",
        "--output", output_json,
        "--force-preload",
        "--",
    ] + make_cmd

    print(f"=== Generating compile_commands.json ({args.platform}, -j{nproc}) ===")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"compile_commands.json written to: {output_json}")
    else:
        print(f"Build failed with exit code {result.returncode}", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
