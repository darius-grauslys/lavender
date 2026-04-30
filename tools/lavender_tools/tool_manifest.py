"""tool_manifest.py — Unified file-operation tracking for Lavender tools.

Records file creates, modifies, and reads performed by any Lavender tool
script into per-tool JSON manifests under ``.lavender/tool-manifest/``.

Manifests are blocked by UTC day to keep individual files manageable and
minimize UUID collision probability over year-long projects.

Each record carries a UUID4, a timestamp, the callee chain (tool scripts
on the call stack), and either a file path or a sub-tool reference.

Usage from any tool script::

    import tool_manifest

    tool_manifest.record_create("/abs/path/to/new_file.h")
    tool_manifest.record_modify("/abs/path/to/existing_file.c")

The module silently no-ops if ``.lavender/`` does not exist (engine dir
or non-Lavender project).
"""

from __future__ import annotations

import inspect
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LAVENDER_DIR: Path | None = None
_DOTLAVENDER: str = ".lavender"
_MANIFEST_DIR: str = "tool-manifest"
_CONFIG_NAME: str = "lavender.json"


def _get_lavender_dir() -> Path:
    """Resolve and cache $LAVENDER_DIR."""
    global _LAVENDER_DIR
    if _LAVENDER_DIR is None:
        env = os.environ.get("LAVENDER_DIR")
        if env:
            _LAVENDER_DIR = Path(env).resolve()
        else:
            # Two levels up from tools/tool_manifest.py → project root
            _LAVENDER_DIR = Path(__file__).resolve().parents[1]
    return _LAVENDER_DIR


# ---------------------------------------------------------------------------
# Config reading
# ---------------------------------------------------------------------------

def _get_dotlavender() -> Path | None:
    """Return the .lavender/ directory path if it exists, else None."""
    p = Path.cwd() / _DOTLAVENDER
    return p if p.is_dir() else None


def _read_config() -> dict | None:
    """Read .lavender/lavender.json.  Returns None if missing or invalid."""
    dot = _get_dotlavender()
    if dot is None:
        return None
    config_path = dot / _CONFIG_NAME
    if not config_path.exists():
        return None
    try:
        return json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _is_operation_enabled(op: str) -> bool:
    """Check if the given operation type is enabled in config.

    *op* is one of ``"create"``, ``"modify"``, ``"read"``.
    Defaults: create=True, modify=True, read=False.
    """
    config = _read_config()
    if config is None:
        return False  # No .lavender dir or config → no-op
    tm = config.get("tool-manifest", {})
    defaults = {"create": True, "modify": True, "read": False}
    return tm.get(op, defaults.get(op, False))


# ---------------------------------------------------------------------------
# Stack introspection
# ---------------------------------------------------------------------------

def _get_callee_chain() -> list[str]:
    """Walk the call stack and return tool script paths.

    Returns paths relative to $LAVENDER_DIR for all frames whose
    ``__file__`` is under ``$LAVENDER_DIR/tools/``.  The bottom-most
    originator (the actual tool doing I/O) is first; ascending callers
    follow.

    Deduplicates consecutive entries (same file appearing in adjacent
    frames due to helper functions within the same module).
    """
    lavender_dir = _get_lavender_dir()
    tools_dir = lavender_dir / "tools"
    chain: list[str] = []

    # Walk from caller outward (skip _get_callee_chain and record_* frames)
    for frame_info in inspect.stack():
        fpath = frame_info.filename
        try:
            resolved = Path(fpath).resolve()
            resolved.relative_to(tools_dir)
        except (ValueError, OSError):
            continue
        rel = str(resolved.relative_to(lavender_dir))
        # Deduplicate consecutive (same module calling itself)
        if not chain or chain[-1] != rel:
            chain.append(rel)

    # Reverse so bottom-most originator is first
    chain.reverse()
    return chain


def _get_tool_name(chain: list[str]) -> str | None:
    """Derive the manifest tool name from the callee chain.

    The FIRST entry (bottom-most originator) determines the manifest
    file.  E.g. ``"tools/gen_entity.py"`` → ``"gen_entity"``.
    """
    if not chain:
        return None
    # First entry is the originator
    basename = Path(chain[0]).stem  # "gen_entity"
    return basename


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------

def _manifest_path(tool_name: str) -> Path | None:
    """Return the path to .lavender/tool-manifest/{tool_name}.json."""
    dot = _get_dotlavender()
    if dot is None:
        return None
    manifest_dir = dot / _MANIFEST_DIR
    manifest_dir.mkdir(parents=True, exist_ok=True)
    return manifest_dir / f"{tool_name}.json"


def _load_manifest(tool_name: str) -> list:
    """Load or create the manifest for *tool_name*."""
    mp = _manifest_path(tool_name)
    if mp is None:
        return []
    if mp.exists():
        try:
            return json.loads(mp.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_manifest(tool_name: str, data: list) -> None:
    """Write the manifest for *tool_name*."""
    mp = _manifest_path(tool_name)
    if mp is None:
        return
    mp.write_text(json.dumps(data, indent=2) + "\n")


def _get_today_block(data: list) -> dict:
    """Find or create today's UTC block in the manifest data."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for block in data:
        if block.get("timestamp") == today:
            return block
    new_block = {"timestamp": today, "block": []}
    data.append(new_block)
    return new_block


# ---------------------------------------------------------------------------
# Record creation
# ---------------------------------------------------------------------------

def _make_record(
    record_type: str,
    chain: list[str],
    file_path: str | None = None,
    sub_tool: str | None = None,
    sub_tool_uuid: str | None = None,
) -> dict:
    """Build a single history record."""
    rec: dict = {
        "uuid": str(uuid.uuid4()),
        "type": record_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "callee-chain": chain,
    }
    if record_type == "file":
        rec["record"] = {"file": file_path}
    elif record_type == "sub-tool":
        rec["record"] = {
            "sub-tool": sub_tool,
            "sub-tool-uuid": sub_tool_uuid,
        }
    return rec


def _record_operation(op: str, file_path: str) -> str | None:
    """Core recording logic.  Returns the UUID of the file record, or None.

    1. Check if operation is enabled in config.
    2. Walk the stack to get the callee chain.
    3. Write a "file" record under the originator tool's manifest.
    4. Write "sub-tool" records under all other tools in the chain.
    """
    if not _is_operation_enabled(op):
        return None

    abs_path = str(Path(file_path).resolve())
    chain = _get_callee_chain()
    if not chain:
        return None

    tool_name = _get_tool_name(chain)
    if tool_name is None:
        return None

    # --- File record for the originator tool ---
    file_record = _make_record("file", chain, file_path=abs_path)
    file_uuid = file_record["uuid"]

    manifest_data = _load_manifest(tool_name)
    block = _get_today_block(manifest_data)
    block["block"].append(file_record)
    _save_manifest(tool_name, manifest_data)

    # --- Sub-tool records for all parent tools in the chain ---
    if len(chain) > 1:
        for parent_path in chain[1:]:
            parent_name = Path(parent_path).stem
            if parent_name == tool_name:
                continue  # Don't self-reference
            parent_data = _load_manifest(parent_name)
            parent_block = _get_today_block(parent_data)
            sub_record = _make_record(
                "sub-tool", chain,
                sub_tool=tool_name,
                sub_tool_uuid=file_uuid,
            )
            parent_block["block"].append(sub_record)
            _save_manifest(parent_name, parent_data)

    return file_uuid


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def record_create(file_path: str) -> str | None:
    """Record a file creation operation.

    Args:
        file_path: Absolute or relative path to the created file.

    Returns:
        UUID4 string of the record, or None if tracking is disabled/unavailable.
    """
    return _record_operation("create", file_path)


def record_modify(file_path: str) -> str | None:
    """Record a file modification operation.

    Args:
        file_path: Absolute or relative path to the modified file.

    Returns:
        UUID4 string of the record, or None if tracking is disabled/unavailable.
    """
    return _record_operation("modify", file_path)


def record_read(file_path: str) -> str | None:
    """Record a file read operation.

    Disabled by default in .lavender/lavender.json (``"read": false``).

    Args:
        file_path: Absolute or relative path to the read file.

    Returns:
        UUID4 string of the record, or None if tracking is disabled/unavailable.
    """
    return _record_operation("read", file_path)
