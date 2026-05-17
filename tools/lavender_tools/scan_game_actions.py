"""scan_game_actions.py — Verify game action handlers and registration modes.

Spec reference: docs/tools/lavender_tools/SPEC.md Section 4.6
"""
from __future__ import annotations
import json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from lavender_tools.lav_ai.clang_server import get_session
from lavender_tools import clang_tools

def run(project_root: str, output_path: str = "") -> dict:
    result = {
        "tool": "scan_game_actions",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "summary": {"total_checked": 0, "passed": 0, "warnings": 0, "errors": 0},
        "results": []
    }
    
    session = get_session(Path(project_root))
    if session is None:
        result["results"].append({
            "check": "4.6",
            "status": "warning",
            "message": "clangd not configured. Skipping clangd-dependent checks.",
            "source": {"file": "", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    # 1. Parse game_action_kind.h
    kind_h_paths = [
        os.path.join(project_root, "source", "game_action", "types", "implemented", "game_action_kind.h"),
        os.path.join(project_root, "core", "include", "types", "implemented", "game_action", "game_action_kind.h")
    ]
    kind_h_path = next((p for p in kind_h_paths if os.path.isfile(p)), None)
    
    game_actions = []
    if kind_h_path:
        with open(kind_h_path) as f:
            content = f.read()
            actions = re.findall(r'Game_Action_Kind__([A-Za-z0-9_]+)', content)
            for a in actions:
                if a not in ["None", "Unknown", "End", "Custom", "Hitbox__End"]:
                    game_actions.append(a)

    # 2. Parse game_action_registrar.c
    registrar_c_paths = [
        os.path.join(project_root, "source", "game_action", "implemented", "game_action_registrar.c"),
        os.path.join(project_root, "core", "source", "game_action", "implemented", "game_action_registrar.c")
    ]
    registrar_c_path = next((p for p in registrar_c_paths if os.path.isfile(p)), None)
    
    registered_actions = set()
    if registrar_c_path:
        with open(registrar_c_path) as f:
            content = f.read()
            # find all register_game_action__ calls
            matches = re.findall(r'register_game_action__([a-zA-Z0-9_]+)', content)
            for m in matches:
                # strip _for__offline etc if present
                base = re.sub(r'_for__(offline|client|server)$', '', m)
                registered_actions.add(base)

    for action in game_actions:
        action_lower = action.lower()
        
        # Check registration mode context
        # (For now, we'll just check if it's registered at all and warn if not)
        result["summary"]["total_checked"] += 1
        if action_lower not in registered_actions:
            # We don't fail because maybe it's not implemented yet, but warn
            result["results"].append({
                "check": "4.6.2",
                "status": "warning",
                "message": f"Game action '{action}' is not registered in any mode",
                "source": {"file": "game_action_registrar.c", "element": ""},
                "expected": f"register_game_action__{action_lower}",
                "clangd_query": ""
            })
            result["summary"]["warnings"] += 1
        else:
            result["summary"]["passed"] += 1

        # 4.6.1 Verify handler exists via clangd
        handler_name = f"m_process__game_action__{action_lower}"
        result["summary"]["total_checked"] += 1
        
        if session:
            sym_result = clang_tools.search_workspace_symbols(session, handler_name)
            
            if sym_result == "No symbols found.":
                result["results"].append({
                    "check": "4.6.1",
                    "status": "error",
                    "message": f"Handler function '{handler_name}' not found",
                    "source": {"file": "", "element": action},
                    "expected": handler_name,
                    "clangd_query": "search_workspace_symbols"
                })
                result["summary"]["errors"] += 1
            else:
                result["results"].append({
                    "check": "4.6.1",
                    "status": "passed",
                    "message": f"Handler function '{handler_name}' found",
                    "source": {"file": "", "element": action},
                    "expected": handler_name,
                    "clangd_query": "search_workspace_symbols"
                })
                result["summary"]["passed"] += 1

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
            
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = run(project_root=args.project_root, output_path=args.output)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
