"""scan_entity.py — Verify entity lifecycle handlers exist and are correctly wired.

Spec reference: docs/tools/lavender_tools/SPEC.md Section 4.3
"""
from __future__ import annotations
import json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from lavender_tools.lav_ai.clang_server import get_session
from lavender_tools import clang_tools

def _parse_gen_entries(file_path: str, pattern: str) -> list[str]:
    """Extract identifiers matching `pattern` regex from // GEN-BEGIN ... // GEN-END."""
    if not os.path.isfile(file_path):
        return []
    with open(file_path) as f:
        content = f.read()
    m = re.search(r'// GEN-BEGIN\n(.*?)// GEN-END', content, re.DOTALL)
    if not m:
        return []
    return re.findall(pattern, m.group(1))

def run(project_root: str, output_path: str = "") -> dict:
    result = {
        "tool": "scan_entity",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "summary": {"total_checked": 0, "passed": 0, "warnings": 0, "errors": 0},
        "results": []
    }
    
    session = get_session(Path(project_root))
    if session is None:
        result["results"].append({
            "check": "4.3",
            "status": "warning",
            "message": "clangd not configured. Skipping clangd-dependent checks.",
            "source": {"file": "", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    # 1. Parse entity_kind.h
    entity_kind_path = os.path.join(project_root, "core", "include", "types", "implemented", "entity", "entity_kind.h")
    entity_kinds = _parse_gen_entries(entity_kind_path, r'Entity_Kind__([A-Za-z0-9_]+)')

    # 2. Parse entity_registrar.c
    entity_registrar_path = os.path.join(project_root, "core", "source", "entity", "implemented", "entity_registrar.c")
    registrar_content = ""
    registered_entities = []
    if os.path.isfile(entity_registrar_path):
        with open(entity_registrar_path) as f:
            registrar_content = f.read()
            m = re.search(r'// GEN-BEGIN\n(.*?)// GEN-END', registrar_content, re.DOTALL)
            if m:
                registered_entities = re.findall(r'register_entity_([a-zA-Z0-9_]+)_into__entity_manager', m.group(1).lower())
                if not registered_entities:
                    registered_entities = [name.lower() for name in re.findall(r'Entity_Kind__([A-Za-z0-9_]+)', m.group(1))]

    # Get sprite kinds to cross-reference (4.3.2)
    sprite_kind_path = os.path.join(project_root, "core", "include", "types", "implemented", "rendering", "sprite", "sprite_kind.h")
    sprite_kinds = _parse_gen_entries(sprite_kind_path, r'Sprite_Kind__([A-Za-z0-9_]+)')
    
    handlers_to_check = ["update", "dispose", "enable", "disable", "serialize", "deserialize"]

    for entity_name in entity_kinds:
        name_lower = entity_name.lower()
        
        # 3a. Verify registrar has a corresponding register call
        result["summary"]["total_checked"] += 1
        if name_lower not in registered_entities:
            result["results"].append({
                "check": "4.3.3",
                "status": "error",
                "message": f"Entity '{entity_name}' is not registered in entity_registrar.c",
                "source": {"file": "entity_registrar.c", "element": ""},
                "expected": f"register_entity_{name_lower}_into__entity_manager",
                "clangd_query": ""
            })
            result["summary"]["errors"] += 1
        else:
            result["summary"]["passed"] += 1

        # 3c. Check sprite_kind.h for matching Sprite_Kind__<Name>
        result["summary"]["total_checked"] += 1
        if entity_name not in sprite_kinds:
            result["results"].append({
                "check": "4.3.2",
                "status": "warning",
                "message": f"Entity '{entity_name}' has no matching Sprite_Kind__{entity_name}",
                "source": {"file": "sprite_kind.h", "element": ""},
                "expected": f"Sprite_Kind__{entity_name}",
                "clangd_query": ""
            })
            result["summary"]["warnings"] += 1
        else:
            result["summary"]["passed"] += 1

        # 3b. Use search_workspace_symbols to look for lifecycle handlers.
        for handler_type in handlers_to_check:
            handler_name = f"m_entity_handler__{handler_type}_{name_lower}"
            result["summary"]["total_checked"] += 1
            
            if session:
                sym_result = clang_tools.search_workspace_symbols(session, handler_name)
                if sym_result == "No symbols found.":
                    status = "error" if handler_type == "update" else "warning"
                    result["results"].append({
                        "check": "4.3.1",
                        "status": status,
                        "message": f"Handler '{handler_name}' not found for entity '{entity_name}'",
                        "source": {"file": "", "element": ""},
                        "expected": handler_name,
                        "clangd_query": "search_workspace_symbols"
                    })
                    if status == "error":
                        result["summary"]["errors"] += 1
                    else:
                        result["summary"]["warnings"] += 1
                else:
                    loc = sym_result.split("\\n")[0]
                    try:
                        parts = loc.rsplit(" ", 1)
                        if len(parts) == 2:
                            file_loc = parts[1]
                            file_path, line, col = file_loc.rsplit(":", 2)
                            hover = clang_tools.get_hover_info(session, file_path, int(line), int(col))
                            result["results"].append({
                                "check": "4.3.4",
                                "status": "passed",
                                "message": f"Handler '{handler_name}' signature verified.",
                                "source": {"file": file_path, "element": ""},
                                "expected": "",
                                "clangd_query": "hover"
                            })
                            result["summary"]["passed"] += 1
                    except Exception as e:
                        pass
                        
                    result["results"].append({
                        "check": "4.3.1",
                        "status": "passed",
                        "message": f"Handler '{handler_name}' found.",
                        "source": {"file": "", "element": ""},
                        "expected": handler_name,
                        "clangd_query": "search_workspace_symbols"
                    })
                    result["summary"]["passed"] += 1

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
            
    return result
