"""scan_ui.py — Verify UI XML handler references resolve to C symbols.

Spec reference: docs/tools/lavender_tools/SPEC.md Section 4.2
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
        "tool": "scan_ui",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "summary": {"total_checked": 0, "passed": 0, "warnings": 0, "errors": 0},
        "results": []
    }
    
    session = get_session(Path(project_root))
    if session is None:
        result["results"].append({
            "check": "4.2",
            "status": "warning",
            "message": "clangd not configured. Skipping clangd-dependent checks.",
            "source": {"file": "", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    # 1. Find all XML files under <project_root>/assets/ui/xml/ recursively.
    import glob
    xml_files = glob.glob(os.path.join(project_root, "assets", "ui", "xml", "**", "*.xml"), recursive=True)
    
    xml_window_names = set()
    
    # 2. For each XML file, parse the <config> section for <ui_func_signature> entries.
    import xml.etree.ElementTree as ET
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            config = root.find("config")
            
            # Record window name based on output c_path if possible, or filename
            output_tag = config.find("output") if config is not None else None
            if output_tag is not None and "c_path" in output_tag.attrib:
                c_path = output_tag.attrib["c_path"]
                # e.g. ./source/ui/implemented/generated/game/main_menu.c -> main_menu
                name = os.path.splitext(os.path.basename(c_path))[0]
                xml_window_names.add(name)
            else:
                xml_window_names.add(os.path.splitext(os.path.basename(xml_file))[0])

            if config is not None:
                for sig in config.findall("ui_func_signature"):
                    c_signatures = sig.get("c_signatures", "")
                    tag_name = sig.get("for", "unknown")
                    
                    # 4. Filter out entries with empty c_signatures
                    if not c_signatures.strip():
                        continue
                        
                    # 3. Extract the c_signatures attribute value
                    # 5. verify it exists as a C symbol
                    for name in c_signatures.split():
                        name = name.strip()
                        if not name:
                            continue
                            
                        result["summary"]["total_checked"] += 1
                        
                        if session:
                            sym_result = clang_tools.search_workspace_symbols(session, name)
                            if sym_result == "No symbols found.":
                                result["results"].append({
                                    "check": "4.2.1",
                                    "status": "error",
                                    "message": f"Handler '{name}' referenced in {os.path.relpath(xml_file, project_root)} not found as C symbol",
                                    "source": {"file": os.path.relpath(xml_file, project_root), "element": tag_name},
                                    "expected": name,
                                    "clangd_query": "search_workspace_symbols"
                                })
                                result["summary"]["errors"] += 1
                            else:
                                loc = sym_result.split("\\n")[0] if sym_result else ""
                                result["results"].append({
                                    "check": "4.2.2",
                                    "status": "passed",
                                    "message": f"Handler '{name}' found at {loc}",
                                    "source": {"file": os.path.relpath(xml_file, project_root), "element": tag_name},
                                    "expected": name,
                                    "clangd_query": "search_workspace_symbols"
                                })
                                result["summary"]["passed"] += 1
        except Exception as e:
            result["results"].append({
                "check": "4.2",
                "status": "error",
                "message": f"Failed to parse XML file {os.path.relpath(xml_file, project_root)}: {e}",
                "source": {"file": os.path.relpath(xml_file, project_root), "element": ""},
                "expected": "",
                "clangd_query": ""
            })
            result["summary"]["errors"] += 1
            result["summary"]["total_checked"] += 1

    # 6. Parse ui_window_registrar.c GEN-BEGIN/END block.
    registrar_paths = [
        os.path.join(project_root, "source", "ui", "implemented", "ui_window_registrar.c"),
        os.path.join(project_root, "core", "source", "ui", "implemented", "ui_window_registrar.c")
    ]
    registrar_path = next((p for p in registrar_paths if os.path.isfile(p)), registrar_paths[0])

    registered_windows = set()
    registrar_content = ""
    if os.path.isfile(registrar_path):
        with open(registrar_path) as f:
            registrar_content = f.read()
            m = re.search(r'// GEN-BEGIN\n(.*?)// GEN-END', registrar_content, re.DOTALL)
            if m:
                registered_windows = set(re.findall(r'Graphics_Window_Kind__(?:UI__)?([A-Za-z0-9_]+)', m.group(1)))
                if not registered_windows:
                    registered_windows = set(re.findall(r'register_ui_window(?:__|_into__ui_window_manager_as__)([A-Za-z0-9_]+)', m.group(1).lower()))

    registered_lower = {w.lower() for w in registered_windows}
    xml_lower = {w.lower() for w in xml_window_names}
    
    # Check registered but unused (in registrar but no XML)
    for w in registered_lower - xml_lower:
        result["summary"]["total_checked"] += 1
        result["results"].append({
            "check": "4.2.3",
            "status": "warning",
            "message": f"Window '{w}' is registered in registrar but has no corresponding XML file.",
            "source": {"file": "ui_window_registrar.c", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    # Check XML without registrar entry
    for w in xml_lower - registered_lower:
        result["summary"]["total_checked"] += 1
        result["results"].append({
            "check": "4.2.3",
            "status": "warning",
            "message": f"XML window '{w}' is not registered in ui_window_registrar.c GEN block.",
            "source": {"file": "xml", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

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
