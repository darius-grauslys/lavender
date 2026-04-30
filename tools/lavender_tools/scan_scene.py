"""scan_scene.py — Verify scene handlers and trace scene-UI relationships.

Spec reference: docs/tools/lavender_tools/SPEC.md Section 4.4
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
        "tool": "scan_scene",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "summary": {"total_checked": 0, "passed": 0, "warnings": 0, "errors": 0},
        "results": []
    }
    
    session = get_session(Path(project_root))
    if session is None:
        result["results"].append({
            "check": "4.4",
            "status": "warning",
            "message": "clangd not configured. Skipping clangd-dependent checks.",
            "source": {"file": "", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    # 1. Parse scene_kind.h
    scene_kind_path = os.path.join(project_root, "core", "include", "types", "implemented", "scene", "scene_kind.h")
    scene_kinds = _parse_gen_entries(scene_kind_path, r'Scene_Kind__([A-Za-z0-9_]+)')

    # 2. Parse scene_registrar.c
    scene_registrar_path = os.path.join(project_root, "core", "source", "scene", "implemented", "scene_registrar.c")
    registrar_content = ""
    registered_scenes = []
    if os.path.isfile(scene_registrar_path):
        with open(scene_registrar_path) as f:
            registrar_content = f.read()
            m = re.search(r'// GEN-BEGIN\n(.*?)// GEN-END', registrar_content, re.DOTALL)
            if m:
                registered_scenes = re.findall(r'register_scene__([a-zA-Z0-9_]+)', m.group(1).lower())
                if not registered_scenes:
                    registered_scenes = [name.lower() for name in re.findall(r'Scene_Kind__([A-Za-z0-9_]+)', m.group(1))]

    # 3. For each Scene_Kind
    for scene_name in scene_kinds:
        name_lower = scene_name.lower()
        
        # 3a. Verify registrar completeness
        result["summary"]["total_checked"] += 1
        if name_lower not in registered_scenes:
            result["results"].append({
                "check": "4.4.2",
                "status": "error",
                "message": f"Scene '{scene_name}' is not registered in scene_registrar.c",
                "source": {"file": "scene_registrar.c", "element": ""},
                "expected": f"register_scene__{name_lower}",
                "clangd_query": ""
            })
            result["summary"]["errors"] += 1
        else:
            result["summary"]["passed"] += 1

        # 3b. Use search_workspace_symbols for register_scene__<name_lower>
        handlers_to_check = [
            f"m_load_scene_as__{name_lower}",
            f"m_enter_scene_as__{name_lower}",
            f"m_unload_scene_as__{name_lower}",
            f"register_scene__{name_lower}"
        ]
        
        for handler_name in handlers_to_check:
            result["summary"]["total_checked"] += 1
            if session:
                sym_result = clang_tools.search_workspace_symbols(session, handler_name)
                if sym_result == "No symbols found.":
                    result["results"].append({
                        "check": "4.4.1",
                        "status": "error",
                        "message": f"Handler/Symbol '{handler_name}' not found for scene '{scene_name}'",
                        "source": {"file": "", "element": ""},
                        "expected": handler_name,
                        "clangd_query": "search_workspace_symbols"
                    })
                    result["summary"]["errors"] += 1
                else:
                    result["results"].append({
                        "check": "4.4.1",
                        "status": "passed",
                        "message": f"Handler/Symbol '{handler_name}' found.",
                        "source": {"file": "", "element": ""},
                        "expected": handler_name,
                        "clangd_query": "search_workspace_symbols"
                    })
                    result["summary"]["passed"] += 1

        # 3c/d. Try to find scene__<name_lower>.c under source/scene/implemented/
        import glob
        scene_files = glob.glob(os.path.join(project_root, "**", "source", "scene", "implemented", f"scene__{name_lower}.c"), recursive=True)
        if not scene_files:
            scene_file_path = os.path.join(project_root, "core", "source", "scene", "implemented", f"scene__{name_lower}.c")
            if os.path.isfile(scene_file_path):
                scene_files = [scene_file_path]
        
        for scene_file in scene_files:
            try:
                with open(scene_file) as sf:
                    content = sf.read()
                    
                    # 4.4.3 UI window cross-ref
                    ui_refs = re.findall(r'UI_Window_Kind__([A-Za-z0-9_]+)', content)
                    if ui_refs:
                        for ui in set(ui_refs):
                            result["summary"]["total_checked"] += 1
                            result["results"].append({
                                "check": "4.4.3",
                                "status": "passed",
                                "message": f"Scene references UI_Window_Kind__{ui}",
                                "source": {"file": os.path.relpath(scene_file, project_root), "element": ui},
                                "expected": "",
                                "clangd_query": ""
                            })
                            result["summary"]["passed"] += 1
                            
                    # 4.4.4 Scene transitions
                    scene_refs = re.findall(r'Scene_Kind__([A-Za-z0-9_]+)', content)
                    scene_refs = [r for r in scene_refs if r != scene_name and r != "None" and r != "Unknown"]
                    if scene_refs:
                        for ref in set(scene_refs):
                            result["summary"]["total_checked"] += 1
                            result["results"].append({
                                "check": "4.4.4",
                                "status": "passed",
                                "message": f"Scene can transition to Scene_Kind__{ref}",
                                "source": {"file": os.path.relpath(scene_file, project_root), "element": ref},
                                "expected": "",
                                "clangd_query": ""
                            })
                            result["summary"]["passed"] += 1
            except Exception as e:
                pass

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
            
    return result
