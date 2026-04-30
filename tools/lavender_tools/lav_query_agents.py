"""lav_query_agents.py — Read-only inspection of opencode.json agent configs.

Loads the project's opencode.json and reports on agent names, permissions,
prompt contents, and stale-reference checks.  All operations are read-only.

Subcommands:
    list                — Print agent names, one per line.
    show                — Print an agent's description, model, permissions,
                          and prompt length.
    search-prompts      — Search agent prompt text with a regex, showing
                          match counts and context snippets.
    search-permissions  — Search agent permission keys/values with a regex.
    verify-clean        — Verify a regex does NOT appear in agent prompts.
                          Exit 0 = clean, exit 1 = stale references found.

Usage:
    python tools/lav_query_agents.py list
    python tools/lav_query_agents.py show --agent planner
    python tools/lav_query_agents.py search-prompts --pattern "mod_png"
    python tools/lav_query_agents.py search-permissions --pattern "lavender-tools_gen"
    python tools/lav_query_agents.py verify-clean --pattern "mod_png(?!_)"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_agents(config_path: str) -> dict:
    """Load and return the ``agent`` dict from opencode.json."""
    path = Path(config_path)
    if not path.is_file():
        print(f"ERROR: Config file not found: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    agents = data.get("agent", {})
    if not agents:
        print(f"ERROR: No 'agent' key in {path}", file=sys.stderr)
        sys.exit(2)
    return agents


def _filter_agents(agents: dict, name: str | None) -> dict:
    """Filter to a single agent if *name* is provided."""
    if not name:
        return agents
    if name not in agents:
        print(f"ERROR: Agent '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    return {name: agents[name]}


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _cmd_list(args: argparse.Namespace) -> int:
    agents = _load_agents(args.config)
    for name in sorted(agents.keys()):
        print(name)
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    agents = _load_agents(args.config)
    if args.agent not in agents:
        print(f"ERROR: Agent '{args.agent}' not found.", file=sys.stderr)
        return 1
    cfg = agents[args.agent]
    perms = cfg.get("permission", {})
    prompt_len = len(cfg.get("prompt", ""))

    print(f"name: {args.agent}")
    print(f"description: {cfg.get('description', '<none>')}")
    print(f"model: {cfg.get('model', '<default>')}")
    print(f"mode: {cfg.get('mode', '<default>')}")
    print(f"hidden: {cfg.get('hidden', False)}")
    print(f"prompt_length: {prompt_len} chars")
    print(f"permissions ({len(perms)}):")
    for key in sorted(perms.keys()):
        print(f"  {key}: {perms[key]}")
    return 0


def _cmd_search_prompts(args: argparse.Namespace) -> int:
    try:
        pattern = re.compile(args.pattern)
    except re.error as exc:
        print(f"ERROR: Invalid regex: {exc}", file=sys.stderr)
        return 2

    agents = _filter_agents(_load_agents(args.config), args.agent)
    ctx = args.context
    found_any = False

    for name in sorted(agents.keys()):
        prompt = agents[name].get("prompt", "")
        matches = list(pattern.finditer(prompt))
        if not matches:
            continue
        found_any = True
        print(f"{name}: {len(matches)} match(es)")
        for m in matches:
            start = max(0, m.start() - ctx)
            end = min(len(prompt), m.end() + ctx)
            snippet = prompt[start:end].replace("\n", "\\n")
            print(f"  ...{snippet}...")

    if not found_any:
        print("No matches found.", file=sys.stderr)
        return 1
    return 0


def _cmd_search_permissions(args: argparse.Namespace) -> int:
    try:
        pattern = re.compile(args.pattern)
    except re.error as exc:
        print(f"ERROR: Invalid regex: {exc}", file=sys.stderr)
        return 2

    agents = _filter_agents(_load_agents(args.config), args.agent)
    found_any = False

    for name in sorted(agents.keys()):
        perms = agents[name].get("permission", {})
        for key, val in sorted(perms.items()):
            val_str = str(val)
            if pattern.search(key) or pattern.search(val_str):
                if not found_any:
                    found_any = True
                print(f"  {name}: {key} = {val_str}")

    if not found_any:
        print("No matching permissions found.", file=sys.stderr)
        return 1
    return 0


def _cmd_verify_clean(args: argparse.Namespace) -> int:
    try:
        pattern = re.compile(args.pattern)
    except re.error as exc:
        print(f"ERROR: Invalid regex: {exc}", file=sys.stderr)
        return 2

    agents = _filter_agents(_load_agents(args.config), args.agent)
    dirty = False

    for name in sorted(agents.keys()):
        prompt = agents[name].get("prompt", "")
        matches = list(pattern.finditer(prompt))
        if matches:
            dirty = True
            print(f"WARNING: {name} has {len(matches)} stale reference(s)")
            for m in matches:
                start = max(0, m.start() - 30)
                end = min(len(prompt), m.end() + 30)
                snippet = prompt[start:end].replace("\n", "\\n")
                print(f"  ...{snippet}...")
        else:
            print(f"{name}: clean")

    return 1 if dirty else 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only inspection of opencode.json agent configs.",
    )
    parser.add_argument(
        "--config", default="./opencode.json",
        help="Path to opencode.json (default: ./opencode.json).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="Print agent names.")

    # show
    p_show = sub.add_parser("show", help="Show agent details.")
    p_show.add_argument("--agent", required=True, help="Agent name.")

    # search-prompts
    p_sp = sub.add_parser("search-prompts", help="Search agent prompts.")
    p_sp.add_argument("--pattern", required=True, help="Regex pattern.")
    p_sp.add_argument("--agent", default=None, help="Filter to one agent.")
    p_sp.add_argument("--context", type=int, default=40,
                       help="Context chars around matches (default: 40).")

    # search-permissions
    p_spe = sub.add_parser("search-permissions",
                            help="Search agent permissions.")
    p_spe.add_argument("--pattern", required=True, help="Regex pattern.")
    p_spe.add_argument("--agent", default=None, help="Filter to one agent.")

    # verify-clean
    p_vc = sub.add_parser("verify-clean",
                           help="Verify pattern absent from prompts.")
    p_vc.add_argument("--pattern", required=True, help="Regex pattern.")
    p_vc.add_argument("--agent", default=None, help="Filter to one agent.")

    args = parser.parse_args()

    handlers = {
        "list": _cmd_list,
        "show": _cmd_show,
        "search-prompts": _cmd_search_prompts,
        "search-permissions": _cmd_search_permissions,
        "verify-clean": _cmd_verify_clean,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
