#!/usr/bin/env python3
"""gen_lav_project.py — Initialize a Lavender game project in the current directory.

Works like ``git init .`` — operates on the current working directory,
derives the project name from the directory name, and refuses to run if
already initialized (.lavender.json exists) or if CWD is the Lavender
engine directory.

Usage:
    cd /path/to/MyGame
    python $LAVENDER_DIR/tools/gen_lav_project.py --platforms sdl
    python $LAVENDER_DIR/tools/gen_lav_project.py --platforms sdl,nds
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

from lavender_tools import tool_history


VALID_PLATFORMS = {"sdl", "nds", "no_gui", "gba", "dreamcast", "android", "ios"}


def _get_lavender_dir() -> Path:
    """Resolve LAVENDER_DIR from environment or script location."""
    env = os.environ.get("LAVENDER_DIR")
    if env:
        return Path(env).resolve()
    # Two levels up from tools/gen_lav_project.py → project root
    return Path(__file__).resolve().parents[1]


def _derive_prefix(project_name: str) -> str:
    """Derive a short lowercase prefix from a CamelCase project name.

    AncientsGame → ag
    DungeonGame  → dg
    MyProject    → mp
    Lavender     → lv
    """
    # Extract uppercase letters
    uppers = [c for c in project_name if c.isupper()]
    if len(uppers) >= 2:
        return "".join(uppers[:2]).lower()
    # Fallback: first two chars
    return project_name[:2].lower()


def _copy_implemented_templates(lavender_dir: Path, dest: Path):
    """Copy core/*/implemented/ template directories to the project."""
    core_dir = lavender_dir / "core"
    for root, dirs, files in os.walk(core_dir):
        root_path = Path(root)
        for d in dirs:
            if d == "implemented":
                impl_path = root_path / d
                # Relative path from core/ (e.g. source/entity/implemented)
                rel = impl_path.relative_to(core_dir)
                dest_impl = dest / rel
                if not dest_impl.exists():
                    shutil.copytree(impl_path, dest_impl, dirs_exist_ok=True)
                    print(f"  Copied {rel}")


def _copy_makefiles(lavender_dir: Path, dest: Path):
    """Copy example Makefiles to the project root."""
    examples_dir = lavender_dir / "examples" / "Makefiles"
    if not examples_dir.exists():
        print(f"Warning: {examples_dir} not found, skipping Makefile copy.",
              file=sys.stderr)
        return
    for f in examples_dir.iterdir():
        if f.is_file():
            shutil.copy2(f, dest / f.name)
            print(f"  Copied {f.name}")


def _copy_assets(lavender_dir: Path, dest: Path):
    """Copy core/assets/ to the project."""
    src = lavender_dir / "core" / "assets"
    if not src.exists():
        print(f"Warning: {src} not found, skipping assets copy.",
              file=sys.stderr)
        return
    dest_assets = dest / "assets"
    if not dest_assets.exists():
        shutil.copytree(src, dest_assets)
        print(f"  Copied core/assets/")
    else:
        print(f"  assets/ already exists, skipping.")


def _copy_pipelines(lavender_dir: Path, dest: Path):
    """Copy .lavender/pipelines/ to the project.

    Copies the full pipeline runner configuration:
    - pipeline__default.json (top-level orchestrator)
    - agents/*.json (LLM agent configs)
    - sub/*.json (sub-pipeline definitions)
    - templates/*.md (prompt templates)
    - templates/*.py (validation/helper scripts)

    Excludes __pycache__/ directories.
    """
    src = lavender_dir / ".lavender" / "pipelines"
    if not src.exists():
        print(f"Warning: {src} not found, skipping pipeline config copy.",
              file=sys.stderr)
        return

    dest_pipelines = dest / ".lavender" / "pipelines"
    if dest_pipelines.exists():
        print(f"  .lavender/pipelines/ already exists, skipping.")
        return

    shutil.copytree(
        src, dest_pipelines,
        ignore=shutil.ignore_patterns("__pycache__"),
    )

    # Count what was copied
    copied = list(dest_pipelines.rglob("*"))
    file_count = sum(1 for f in copied if f.is_file())
    print(f"  Copied .lavender/pipelines/ ({file_count} files)")


def _generate_defines_headers(dest: Path, prefix: str, project_name: str):
    """Generate <prefix>__defines.h and <prefix>__defines_weak.h."""
    include_dir = dest / "include"
    include_dir.mkdir(parents=True, exist_ok=True)

    guard_upper = prefix.upper()
    name_upper = re.sub(r'([a-z])([A-Z])', r'\1_\2', project_name).upper()

    # <prefix>__defines.h
    defines_h = include_dir / f"{prefix}__defines.h"
    if not defines_h.exists():
        defines_h.write_text(
            f"#ifndef {guard_upper}__DEFINES_H\n"
            f"#define {guard_upper}__DEFINES_H\n"
            f"\n"
            f"#include \"defines.h\"\n"
            f"#include \"{prefix}__defines_weak.h\"\n"
            f"\n"
            f"// {name_upper} project-specific defines go here.\n"
            f"// This file is included AFTER the engine's defines.h,\n"
            f"// so all engine types are available.\n"
            f"\n"
            f"#endif\n"
        )
        tool_history.record_create(str(defines_h))
        print(f"  Generated {prefix}__defines.h")
    else:
        print(f"  {prefix}__defines.h already exists, skipping.")

    # <prefix>__defines_weak.h
    defines_weak_h = include_dir / f"{prefix}__defines_weak.h"
    if not defines_weak_h.exists():
        defines_weak_h.write_text(
            f"#ifndef {guard_upper}__DEFINES_WEAK_H\n"
            f"#define {guard_upper}__DEFINES_WEAK_H\n"
            f"\n"
            f"#include \"defines_weak.h\"\n"
            f"\n"
            f"// {name_upper} project-specific weak defines go here.\n"
            f"// This file is included by {prefix}__defines.h and provides\n"
            f"// forward declarations and typedefs used across the project.\n"
            f"\n"
            f"#endif\n"
        )
        tool_history.record_create(str(defines_weak_h))
        print(f"  Generated {prefix}__defines_weak.h")
    else:
        print(f"  {prefix}__defines_weak.h already exists, skipping.")


def _generate_lavender_json(dest: Path, platforms: list[str]):
    """Generate .lavender/lavender.json project config."""
    dotlavender = dest / ".lavender"
    dotlavender.mkdir(parents=True, exist_ok=True)
    config = {
        "platforms": platforms,
        "tool-history": {
            "create": True,
            "modify": True,
            "read": False,
        },
    }
    config_path = dotlavender / "lavender.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    tool_history.record_create(str(config_path))
    print(f"  Generated .lavender/lavender.json (platforms: {platforms})")


def _generate_opencode_json(dest: Path, lavender_dir: Path, platforms: list[str]):
    """Generate opencode.json with full agent suite.

    The filesystem MCP server is scoped to the game project directory ONLY.
    Engine files are accessed through the lav-ai-engine-fs read-only server,
    which is scoped per-platform based on .lavender.json.
    """
    # Build the read-only engine FS root list from platforms
    # Each platform exposes {platform}/include and {platform}/source
    # Plus core/include and core/source always
    engine_roots = [
        f"$LAVENDER_DIR/core/include",
        f"$LAVENDER_DIR/core/source",
    ]
    for p in platforms:
        engine_roots.append(f"$LAVENDER_DIR/{p}/include")
        engine_roots.append(f"$LAVENDER_DIR/{p}/source")

    config = {
        "$schema": "https://opencode.ai/config.json",
        "mcp": {
            "lavender-tools": {
                "type": "local",
                "enabled": True,
                "command": [
                    "sh", "-c",
                    "python3 \"$LAVENDER_DIR/tools/lavender_tools/lav_ai/lav_ai_app.py\""
                ]
            },
            "lav-ai-engine-fs": {
                "type": "local",
                "enabled": True,
                "command": [
                    "sh", "-c",
                    "python3 \"$LAVENDER_DIR/tools/lavender_tools/lav_ai/lav_ai_fs_readonly.py\""
                ]
            },
            "filesystem": {
                "type": "local",
                "enabled": True,
                "command": [
                    "sh", "-c",
                    "npx -y @modelcontextprotocol/server-filesystem ."
                ]
            }
        },
    }

    # We include the full agent suite from the engine's opencode.json
    # but the agents are defined in the engine config and shared.
    # The game project only needs the MCP server definitions — agents
    # are loaded from the engine's opencode.json via the tooling harness.

    config_path = dest / "opencode.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    tool_history.record_create(str(config_path))
    print(f"  Generated opencode.json")


def _ensure_directories(dest: Path):
    """Create standard project directory structure."""
    dirs = [
        dest / "include",
        dest / "source",
        dest / "assets",
        dest / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a Lavender game project in the current directory.",
    )
    parser.add_argument(
        "--platforms", required=True,
        help="Comma-separated list of target platforms. "
             f"Valid: {', '.join(sorted(VALID_PLATFORMS))}. "
             'Example: --platforms sdl  or  --platforms sdl,nds',
    )
    args = parser.parse_args()

    # Parse and validate platforms
    platforms = [p.strip().lower() for p in args.platforms.split(",") if p.strip()]
    for p in platforms:
        if p not in VALID_PLATFORMS:
            print(f"Error: Invalid platform '{p}'. "
                  f"Valid platforms: {', '.join(sorted(VALID_PLATFORMS))}",
                  file=sys.stderr)
            return 1

    if not platforms:
        print("Error: At least one platform must be specified.", file=sys.stderr)
        return 1

    lavender_dir = _get_lavender_dir()
    cwd = Path.cwd().resolve()

    # Guard: refuse to run in LAVENDER_DIR
    if cwd == lavender_dir:
        print("Error: Cannot initialize a project in the Lavender engine "
              f"directory ({lavender_dir}). Run from your game project directory.",
              file=sys.stderr)
        return 1

    # Guard: refuse to run if already initialized
    if (cwd / ".lavender" / "lavender.json").exists():
        print("Error: .lavender/lavender.json already exists in this directory. "
              "This project is already initialized.",
              file=sys.stderr)
        return 1

    project_name = cwd.name
    prefix = _derive_prefix(project_name)

    print(f"=== Initializing Lavender project: {project_name} ===")
    print(f"  Directory: {cwd}")
    print(f"  Prefix: {prefix}")
    print(f"  Platforms: {platforms}")
    print(f"  Engine: {lavender_dir}")
    print()

    _ensure_directories(cwd)
    _generate_lavender_json(cwd, platforms)
    _copy_pipelines(lavender_dir, cwd)
    _copy_implemented_templates(lavender_dir, cwd)
    _copy_makefiles(lavender_dir, cwd)
    _copy_assets(lavender_dir, cwd)
    _generate_defines_headers(cwd, prefix, project_name)
    _generate_opencode_json(cwd, lavender_dir, platforms)

    print(f"\nProject '{project_name}' initialized successfully.")
    print(f"  Prefix: {prefix}__ (used in {prefix}__defines.h)")
    print(f"  Build:  $LAVENDER_DIR/tools/lav_build -e PLATFORM={platforms[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
