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
import json
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


def _build_make_args(args: argparse.Namespace, lavender_dir: str, game_dir: str | None) -> list[str]:
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

    if game_dir:
        cmd.extend(["-e", f"GAME_DIR={game_dir}"])

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
             "Defaults to CWD if CWD is a Lavender project.",
    )
    args = parser.parse_args()

    lavender_dir = _get_lavender_dir()
    game_dir = _resolve_game_dir(args.game_dir)

    # Clean if requested
    if args.clean:
        clean_cmd = [
            "make", "-f", os.path.join(lavender_dir, "Makefile"), "clean",
        ]
        if game_dir:
            clean_cmd.extend(["-e", f"GAME_DIR={game_dir}"])
        sys.stderr.write("=== Cleaning ===\n")
        subprocess.run(clean_cmd, check=False)

    # Build
    cmd = _build_make_args(args, lavender_dir, game_dir)

    nproc = multiprocessing.cpu_count()
    sys.stderr.write(f"=== Building ({args.platform}, -j{nproc}, perf_metrics=on) ===\n")

    wall_start = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True)
    wall_end = time.monotonic()

    wall_ms = int((wall_end - wall_start) * 1000)
    sys.stderr.write(f"\n=== Wall-clock time: {wall_ms} ms ({wall_ms / 1000:.2f} s) ===\n")

    # Compute expected binary path
    if game_dir:
        game_name = os.path.basename(game_dir)
        binary_path = os.path.join(game_dir, "build", args.platform, game_name)
    else:
        lav_name = os.path.basename(os.path.realpath(lavender_dir))
        binary_path = os.path.join(lavender_dir, "build", args.platform, lav_name)

    build_output_lines = []
    build_output_lines.append(f"=== Building ({args.platform}, -j{nproc}, perf_metrics=on) ===")
    build_output_lines.append(result.stdout or "")
    if result.stderr:
        build_output_lines.append(result.stderr)
    build_output_lines.append(f"\n=== Wall-clock time: {wall_ms} ms ({wall_ms / 1000:.2f} s) ===")

    build_output = "\n".join(build_output_lines)

    exit_code = result.returncode
    binary_exists = os.path.isfile(binary_path) if exit_code == 0 else False

    if exit_code == 0 and not binary_exists:
        build_output += f"\nERROR: Build reported success but binary not found at {binary_path}"
        exit_code = 1  # Override to failure

    output = {
        "build_exit_code": exit_code,
        "build_output": build_output,
        "binary_path": binary_path,
        "binary_exists": binary_exists,
    }
    print(json.dumps(output))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
