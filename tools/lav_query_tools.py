"""lav_query_tools.py — Read-only inspection of the Lavender MCP tool registry.

Introspects the FastMCP instance from lav_ai_app to report on registered tools,
their parameter schemas, and descriptions.  All operations are read-only.

Subcommands:
    list      — Print sorted tool names, one per line.
    count     — Print the integer count of registered tools.
    search    — Print tool names matching a regex pattern.
    describe  — Print name, parameter schema, and description summary.
    params    — Print required and optional parameters with types/defaults.

Usage:
    python tools/lav_query_tools.py list
    python tools/lav_query_tools.py count
    python tools/lav_query_tools.py search --pattern "mod_png.*"
    python tools/lav_query_tools.py describe --name gen_entity
    python tools/lav_query_tools.py params --name gen_entity
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Ensure tools/ is importable so lav_ai is a top-level package.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lav_ai.lav_ai_app import mcp as _mcp  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_tools() -> dict:
    """Return the internal tools dict from the FastMCP tool manager."""
    return _mcp._tool_manager._tools


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _cmd_list(_args: argparse.Namespace) -> int:
    tools = _get_tools()
    for name in sorted(tools.keys()):
        print(name)
    return 0


def _cmd_count(_args: argparse.Namespace) -> int:
    print(len(_get_tools()))
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    try:
        pattern = re.compile(args.pattern)
    except re.error as exc:
        print(f"ERROR: Invalid regex: {exc}", file=sys.stderr)
        return 2

    matches = sorted(n for n in _get_tools() if pattern.search(n))
    if not matches:
        print("No tools matched.", file=sys.stderr)
        return 1
    for name in matches:
        print(name)
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    tools = _get_tools()
    if args.name not in tools:
        print(f"ERROR: Tool '{args.name}' not found.", file=sys.stderr)
        return 1

    tool = tools[args.name]
    desc_lines = (tool.description or "").strip().splitlines()
    summary = "\n".join(desc_lines[:5])

    print(f"name: {tool.name}")
    print(f"description_length: {len(tool.description or '')} chars")
    print(f"parameters: {json.dumps(tool.parameters, indent=2)}")
    print(f"summary: {summary}")
    return 0


def _cmd_params(args: argparse.Namespace) -> int:
    tools = _get_tools()
    if args.name not in tools:
        print(f"ERROR: Tool '{args.name}' not found.", file=sys.stderr)
        return 1

    schema = tools[args.name].parameters or {}
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for pname, pspec in props.items():
        kind = "REQUIRED" if pname in required else "optional"
        ptype = pspec.get("type", "unknown")
        default = pspec.get("default", "<none>")
        if kind == "REQUIRED":
            print(f"  {pname} ({ptype}) — {kind}")
        else:
            print(f"  {pname} ({ptype}) — {kind}, default={default}")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only inspection of the Lavender MCP tool registry.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Print sorted tool names.")
    sub.add_parser("count", help="Print tool count.")

    p_search = sub.add_parser("search", help="Search tool names by regex.")
    p_search.add_argument("--pattern", required=True, help="Regex pattern.")

    p_describe = sub.add_parser("describe", help="Describe a tool.")
    p_describe.add_argument("--name", required=True, help="Tool name.")

    p_params = sub.add_parser("params", help="Show tool parameters.")
    p_params.add_argument("--name", required=True, help="Tool name.")

    args = parser.parse_args()

    handlers = {
        "list": _cmd_list,
        "count": _cmd_count,
        "search": _cmd_search,
        "describe": _cmd_describe,
        "params": _cmd_params,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
