"""lav_ai_fs_readonly.py — Read-only MCP filesystem server for Lavender engine files.

Exposes engine source and header files as read-only to game project agents.
Allowed directories are determined by the .lavender.json ``platforms`` field
in the caller's CWD.  Always exposes ``core/include`` and ``core/source``;
additionally exposes ``{platform}/include`` and ``{platform}/source`` for
each platform listed in .lavender.json.

NO write operations are exposed.  This server provides only:
  - engine_read_text_file
  - engine_read_multiple_files
  - engine_list_directory
  - engine_directory_tree
  - engine_search_files
  - engine_get_file_info

Run with:
    python tools/lavender_tools/lav_ai/lav_ai_fs_readonly.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Resolve engine root and allowed directories
# ---------------------------------------------------------------------------

def _get_lavender_dir() -> Path:
    env = os.environ.get("LAVENDER_DIR")
    if env:
        return Path(env).resolve()
    # Three levels up: lav_ai_fs_readonly.py → lav_ai/ → lavender_tools/ → tools/ → <root>
    return Path(__file__).resolve().parents[3]


def _load_allowed_roots() -> list[Path]:
    """Read .lavender.json from CWD and compute allowed engine directories."""
    lavender_dir = _get_lavender_dir()
    roots = [
        lavender_dir / "core" / "include",
        lavender_dir / "core" / "source",
    ]

    config_path = Path.cwd() / ".lavender" / "lavender.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            platforms = config.get("platforms", [])
            for p in platforms:
                p_lower = p.strip().lower()
                roots.append(lavender_dir / p_lower / "include")
                roots.append(lavender_dir / p_lower / "source")
        except (json.JSONDecodeError, OSError):
            pass  # Fallback to core-only

    # Filter to directories that actually exist
    return [r for r in roots if r.is_dir()]


ALLOWED_ROOTS = _load_allowed_roots()

mcp = FastMCP("lav-ai-engine-fs",
              warn_on_duplicate_tools=True)


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

def _validate_path(path_str: str) -> Path | str:
    """Resolve a path and verify it's under an allowed root.

    Returns the resolved Path on success, or an error string on failure.
    """
    try:
        resolved = Path(path_str).resolve()
    except (OSError, ValueError) as e:
        return f"ERROR: Invalid path: {e}"

    for root in ALLOWED_ROOTS:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue

    return (f"ERROR: Path '{path_str}' is outside allowed engine directories. "
            f"Allowed roots: {[str(r) for r in ALLOWED_ROOTS]}")


def _validate_paths(paths: list[str]) -> list[Path] | str:
    """Validate multiple paths. Returns list of Paths or first error."""
    result = []
    for p in paths:
        v = _validate_path(p)
        if isinstance(v, str):
            return v
        result.append(v)
    return result


# ---------------------------------------------------------------------------
# Read-only tools
# ---------------------------------------------------------------------------

@mcp.tool()
def engine_read_text_file(path: str, head: int = 0, tail: int = 0) -> str:
    """Read a text file from the Lavender engine (read-only).

    Only files under engine core/ and platform include/source directories
    are accessible.  Scoped by .lavender.json platforms.

    Args:
        path: Absolute path to the engine file.
        head: Return only the first N lines (0 = no limit).
        tail: Return only the last N lines (0 = no limit).

    Returns:
        File contents as text.  Prefixed with ``ERROR:`` on failure.
    """
    validated = _validate_path(path)
    if isinstance(validated, str):
        return validated
    try:
        text = validated.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=True)
        if head > 0:
            lines = lines[:head]
        elif tail > 0:
            lines = lines[-tail:]
        return "".join(lines)
    except OSError as e:
        return f"ERROR: Cannot read file: {e}"


@mcp.tool()
def engine_read_multiple_files(paths: list[str]) -> str:
    """Read multiple engine files simultaneously (read-only).

    Args:
        paths: List of absolute paths to engine files.

    Returns:
        Each file's contents prefixed with its path.  Individual read
        failures are reported inline without stopping the operation.
    """
    results = []
    for p in paths:
        validated = _validate_path(p)
        if isinstance(validated, str):
            results.append(f"--- {p} ---\n{validated}\n")
            continue
        try:
            text = validated.read_text(encoding="utf-8", errors="replace")
            results.append(f"--- {p} ---\n{text}\n")
        except OSError as e:
            results.append(f"--- {p} ---\nERROR: {e}\n")
    return "\n".join(results)


@mcp.tool()
def engine_list_directory(path: str) -> str:
    """List contents of an engine directory (read-only).

    Args:
        path: Absolute path to an engine directory.

    Returns:
        Entries with [FILE] or [DIR] prefix, one per line.
    """
    validated = _validate_path(path)
    if isinstance(validated, str):
        return validated
    if not validated.is_dir():
        return f"ERROR: Not a directory: {path}"
    try:
        entries = sorted(validated.iterdir(), key=lambda p: (p.is_file(), p.name))
        lines = []
        for e in entries:
            prefix = "[DIR]" if e.is_dir() else "[FILE]"
            lines.append(f"{prefix} {e.name}")
        return "\n".join(lines)
    except OSError as e:
        return f"ERROR: {e}"


@mcp.tool()
def engine_directory_tree(path: str, max_depth: int = 5) -> str:
    """Get a recursive tree view of an engine directory (read-only).

    Args:
        path: Absolute path to an engine directory.
        max_depth: Maximum recursion depth (default: 5).

    Returns:
        Indented tree view of the directory structure.
    """
    validated = _validate_path(path)
    if isinstance(validated, str):
        return validated
    if not validated.is_dir():
        return f"ERROR: Not a directory: {path}"

    lines = []

    def _walk(p: Path, indent: int, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        except OSError:
            return
        for e in entries:
            prefix = "  " * indent
            if e.is_dir():
                lines.append(f"{prefix}{e.name}/")
                _walk(e, indent + 1, depth + 1)
            else:
                lines.append(f"{prefix}{e.name}")

    lines.append(f"{validated.name}/")
    _walk(validated, 1, 1)
    return "\n".join(lines)


@mcp.tool()
def engine_search_files(path: str, pattern: str) -> str:
    """Search for files matching a glob pattern in engine directories (read-only).

    Args:
        path: Starting directory (must be under an allowed engine root).
        pattern: Glob pattern (e.g. ``"*.h"``, ``"**/*entity*.h"``).

    Returns:
        Matching file paths, one per line.
    """
    validated = _validate_path(path)
    if isinstance(validated, str):
        return validated
    if not validated.is_dir():
        return f"ERROR: Not a directory: {path}"
    try:
        matches = sorted(validated.glob(pattern))
        # Filter to only files under allowed roots
        safe_matches = []
        for m in matches:
            check = _validate_path(str(m))
            if isinstance(check, Path):
                safe_matches.append(str(m))
        return "\n".join(safe_matches) if safe_matches else "No matches found."
    except OSError as e:
        return f"ERROR: {e}"


@mcp.tool()
def engine_get_file_info(path: str) -> str:
    """Get metadata about an engine file or directory (read-only).

    Args:
        path: Absolute path to an engine file or directory.

    Returns:
        File metadata including size, type, and modification time.
    """
    validated = _validate_path(path)
    if isinstance(validated, str):
        return validated
    try:
        stat = validated.stat()
        ftype = "directory" if validated.is_dir() else "file"
        import datetime
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        return (f"path: {validated}\n"
                f"type: {ftype}\n"
                f"size: {stat.st_size} bytes\n"
                f"modified: {mtime}\n"
                f"permissions: {oct(stat.st_mode)}")
    except OSError as e:
        return f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
