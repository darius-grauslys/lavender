#!/usr/bin/env python3
"""build.py — Build the Lavender engine or a game project.

Wraps the Makefile build system with automatic parallelization and
performance metrics.  Always produces build metrics in the build
output directory under performance-metrics/.

Usage:
    python tools/build.py --platform sdl
    python tools/build.py --platform sdl --flags "-ggdb -DIS_SERVER"
    python tools/build.py --platform sdl --clean
    python tools/build.py --platform sdl --game-dir /path/to/MyGame
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import subprocess
import sys
import time


def _get_lavender_dir() -> str:
    """Resolve LAVENDER_DIR from environment or script location."""
    env = os.environ.get("LAVENDER_DIR")
    if env:
        return env
    # Three levels up from tools/lavender_tools/build.py → project root
    return str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _build_make_args(args: argparse.Namespace, lavender_dir: str) -> list[str]:
    """Construct the make command list."""
    nproc = multiprocessing.cpu_count()

    # Base flags always include -w to suppress warnings (see docs/BUILD.md)
    flags = args.flags if args.flags else "-w"

    cmd = [
        "make",
        f"-j{nproc}",
        "-f", os.path.join(lavender_dir, "Makefile"),
    ]

    if args.clean:
        # Run clean as a separate make invocation first
        pass  # Handled in main()

    cmd.extend([
        "-e", f"PLATFORM={args.platform}",
        "-e", f"FLAGS={flags}",
        "-e", "PERF_METRICS=1",
    ])

    if args.game_dir:
        cmd.extend(["-e", f"GAME_DIR={os.path.abspath(args.game_dir)}"])

    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Lavender engine or game project.",
    )
    parser.add_argument(
        "--platform", required=True,
        choices=["sdl", "nds", "no_gui"],
        help="Target platform.",
    )
    parser.add_argument(
        "--flags", default="-w",
        help='Compiler FLAGS passed to make (default: "-w"). '
             'Example: "--flags \\"-ggdb -w -DIS_SERVER\\""',
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Run make clean before building.",
    )
    parser.add_argument(
        "--game-dir", default=None,
        help="Path to a game project directory. "
             "Omit to build the engine standalone.",
    )
    args = parser.parse_args()

    lavender_dir = _get_lavender_dir()

    # Clean if requested
    if args.clean:
        clean_cmd = [
            "make", "-f", os.path.join(lavender_dir, "Makefile"), "clean",
        ]
        if args.game_dir:
            clean_cmd.extend(["-e", f"GAME_DIR={os.path.abspath(args.game_dir)}"])
        print("=== Cleaning ===")
        subprocess.run(clean_cmd, check=False)

    # Build
    cmd = _build_make_args(args, lavender_dir)

    nproc = multiprocessing.cpu_count()
    print(f"=== Building ({args.platform}, -j{nproc}, perf_metrics=on) ===")

    wall_start = time.monotonic()
    result = subprocess.run(cmd)
    wall_end = time.monotonic()

    wall_ms = int((wall_end - wall_start) * 1000)
    print(f"\n=== Wall-clock time: {wall_ms} ms ({wall_ms / 1000:.2f} s) ===")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
