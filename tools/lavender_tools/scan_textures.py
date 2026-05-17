"""scan_textures.py — Detect orphaned and missing texture registrations.

Spec reference: docs/tools/lavender_tools/SPEC.md Section 4.5
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

def _parse_gen_extern_entries(file_path: str, pattern: str) -> list[str]:
    if not os.path.isfile(file_path):
        return []
    with open(file_path) as f:
        content = f.read()
    m = re.search(r'// GEN-EXTERN-BEGIN\n(.*?)// GEN-EXTERN-END', content, re.DOTALL)
    if not m:
        return []
    return re.findall(pattern, m.group(1))

def run(project_root: str, output_path: str = "") -> dict:
    result = {
        "tool": "scan_textures",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "summary": {"total_checked": 0, "passed": 0, "warnings": 0, "errors": 0},
        "results": []
    }
    
    session = get_session(Path(project_root))
    if session is None:
        result["results"].append({
            "check": "4.5",
            "status": "warning",
            "message": "clangd not configured. Skipping clangd-dependent checks.",
            "source": {"file": "", "element": ""},
            "expected": "",
            "clangd_query": ""
        })
        result["summary"]["warnings"] += 1

    registrar_c_paths = [
        os.path.join(project_root, "source", "rendering", "implemented", "aliased_texture_registrar.c"),
        os.path.join(project_root, "core", "source", "rendering", "implemented", "aliased_texture_registrar.c")
    ]
    registrar_c_path = next((p for p in registrar_c_paths if os.path.isfile(p)), None)
    
    if not registrar_c_path:
        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
        return result

    rel_registrar_c = os.path.relpath(registrar_c_path, project_root)
    
    content = ""
    with open(registrar_c_path) as f:
        content = f.read()
    
    m_extern = re.search(r'// GEN-EXTERN-BEGIN\n(.*?)// GEN-EXTERN-END', content, re.DOTALL)
    extern_block = m_extern.group(1) if m_extern else ""
    
    name_defs = re.findall(r'name_of__texture__([A-Za-z0-9_]+)', extern_block)
    aliases = set(name_defs)
    
    path_mappings = {}
    for alias in aliases:
        pattern = r'path_to__texture__' + alias + r'\[\]\s*=\s*"([^"]+)"'
        m = re.search(pattern, extern_block)
        if m:
            path_mappings[alias] = m.group(1)

    for alias, png_path in path_mappings.items():
        result["summary"]["total_checked"] += 1
        full_png_path = os.path.join(project_root, png_path)
        if not os.path.isfile(full_png_path):
            result["results"].append({
                "check": "4.5.3",
                "status": "error",
                "message": f"Texture '{alias}' registered path does not exist on disk: {png_path}",
                "source": {"file": rel_registrar_c, "element": f"path_to__texture__{alias}"},
                "expected": "File exists",
                "clangd_query": ""
            })
            result["summary"]["errors"] += 1
        else:
            result["summary"]["passed"] += 1

    if session:
        for alias in aliases:
            sym_name = f"name_of__texture__{alias}"
            result["summary"]["total_checked"] += 1
            sym_result = clang_tools.search_workspace_symbols(session, sym_name)
            
            if sym_result == "No symbols found.":
                result["results"].append({
                    "check": "4.5.1",
                    "status": "error",
                    "message": f"Symbol '{sym_name}' not found by clangd workspace search",
                    "source": {"file": rel_registrar_c, "element": sym_name},
                    "expected": "Symbol definition",
                    "clangd_query": "search_workspace_symbols"
                })
                result["summary"]["errors"] += 1
                continue
                
            lines = sym_result.strip().split("\n")
            first_loc = ""
            for line in lines:
                parts = line.rsplit(" ", 1)
                if len(parts) == 2 and ":" in parts[1]:
                    first_loc = parts[1]
                    break
            
            if first_loc:
                try:
                    file_path, line, col = first_loc.rsplit(":", 2)
                    ref_result = clang_tools.find_references(session, file_path, int(line), int(col))
                    
                    refs = ref_result.strip().split("\n")
                    external_refs = 0
                    for ref in refs:
                        if ref == "No references found.":
                            continue
                        if not ref.startswith(registrar_c_path) and "aliased_texture_registrar" not in ref:
                            external_refs += 1
                            
                    if external_refs == 0:
                        result["results"].append({
                            "check": "4.5.1",
                            "status": "warning",
                            "message": f"Texture alias '{alias}' is registered but never used outside the registrar",
                            "source": {"file": rel_registrar_c, "element": sym_name},
                            "expected": "At least 1 external reference",
                            "clangd_query": "find_references"
                        })
                        result["summary"]["warnings"] += 1
                    else:
                        result["summary"]["passed"] += 1
                except Exception as e:
                    pass
    
    import glob
    c_files = glob.glob(os.path.join(project_root, "**", "*.c"), recursive=True)
    c_files += glob.glob(os.path.join(project_root, "**", "*.h"), recursive=True)
    
    found_aliases = set()
    for cf in c_files:
        if "aliased_texture_registrar" in cf or ".lavender" in cf or "build" in cf:
            continue
        try:
            with open(cf, 'r', encoding='utf-8') as f:
                content = f.read()
            for m in re.finditer(r'get_texture_by__alias\s*\([^,]+,\s*(name_of__texture__([A-Za-z0-9_]+))', content):
                alias = m.group(2)
                found_aliases.add((alias, cf))
        except:
            pass

    for alias, cf in found_aliases:
        result["summary"]["total_checked"] += 1
        if alias not in aliases:
            result["results"].append({
                "check": "4.5.2",
                "status": "error",
                "message": f"Texture alias '{alias}' is referenced but not registered",
                "source": {"file": os.path.relpath(cf, project_root), "element": f"name_of__texture__{alias}"},
                "expected": "Registered in aliased_texture_registrar",
                "clangd_query": ""
            })
            result["summary"]["errors"] += 1
        else:
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
