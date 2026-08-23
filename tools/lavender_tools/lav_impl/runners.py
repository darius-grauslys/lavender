from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ._project_root import PROJECT_ROOT


def _run(cmd: list[str], project_dir: str = "") -> str:
    """Run *cmd*, inheriting the caller's CWD, capture stdout+stderr, return combined.

    Refuses to run when CWD is the Lavender engine directory.

    On non-zero exit code the return value is prefixed with
    ``ERROR (exit <code>):\n``.
    """
    cwd = Path(project_dir).resolve() if project_dir else Path.cwd().resolve()
    if cwd == PROJECT_ROOT:
        err = (
            "ERROR: Refusing to run — CWD is the Lavender engine directory "
            f"({PROJECT_ROOT}). Tools MUST be run from a game project "
            "directory, not from the engine root. Set your working directory "
            "to your game project and try again."
        )
        print(err, file=sys.stderr)
        return f"ERROR (exit 1):\n{err}"

    kwargs = {}
    if project_dir:
        kwargs["cwd"] = project_dir
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    output = result.stdout + result.stderr
    if result.returncode != 0:
        return f"ERROR (exit {result.returncode}):\n{output}"
    return output


def _run_build(cmd: list[str], project_dir: str = "") -> str:
    """Run a build command, capturing stdout+stderr.

    Unlike ``_run()``, this does NOT refuse to run from the Lavender engine
    directory — build tools legitimately operate on the engine itself.

    On non-zero exit code the return value is prefixed with
    ``ERROR (exit <code>):\n``.
    """
    kwargs = {}
    if project_dir:
        kwargs["cwd"] = project_dir
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    output = result.stdout + result.stderr
    if result.returncode != 0:
        return f"ERROR (exit {result.returncode}):\n{output}"
    return output


def _read_lavender_config(project_dir: str = "") -> dict | None:
    """Read .lavender/lavender.json from CWD.  Returns parsed dict or None if not found."""
    if project_dir:
        config_path = Path(project_dir) / ".lavender" / "lavender.json"
    else:
        config_path = Path.cwd() / ".lavender" / "lavender.json"
    if not config_path.exists():
        return None
    try:
        return json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _validate_platform(platform: str, project_dir: str = "") -> str | None:
    """Validate *platform* against the ``.lavender/lavender.json`` whitelist.

    Returns ``None`` if valid (or no config file exists).
    Returns an error string if the platform is not allowed.
    """
    config = _read_lavender_config(project_dir)
    if config is None:
        return None  # No .lavender/ config = no restriction
    allowed = config.get("platforms", [])
    if not allowed:
        return None  # Empty platforms list = no restriction
    if platform.lower() not in [p.lower() for p in allowed]:
        return (
            f"ERROR: Platform '{platform}' is not in .lavender/lavender.json "
            f"platforms whitelist: {allowed}"
        )
    return None


def _parse_areas(areas: str) -> list[dict]:
    """Parse semicolon-separated ``key:value`` area specs into dicts."""
    parsed = []
    for area_str in areas.split(";"):
        area = {}
        for pair in area_str.split(","):
            k, v = pair.split(":")
            area[k.strip()] = int(v.strip())
        parsed.append(area)
    return parsed


_MOD_PNG_SCRIPT = str(PROJECT_ROOT / "tools" / "lavender_tools" / "mod_png.py")


def _build_mod_png_op_cmd(
    path: str,
    tile_size: str,
    op: str,
    coord_type: str,
    areas: str,
    value: str = "",
    value_type: str = "",
    output: str = "",
) -> list[str]:
    """Build the full subprocess command list for a mod_png operation."""
    op_obj: dict = {"op": op, "type": coord_type, "areas": _parse_areas(areas)}
    if value:
        op_obj["value"] = value
    if value_type:
        op_obj["value-type"] = value_type

    cmd = [
        sys.executable, _MOD_PNG_SCRIPT,
        "--tile-size", tile_size,
        "--path", path,
        "--op", json.dumps(op_obj, separators=(",", ":")),
    ]
    if output:
        cmd += ["--output", output]
    return cmd
