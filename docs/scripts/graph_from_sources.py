#!/usr/bin/env python3
"""Regenerate docs/files/graph/{nodes,edges}.csv from core/'s #include graph.

Run from anywhere (takes ~seconds):
    python3 docs/scripts/graph_from_sources.py

Nodes: one per source module under core/. A module is a .c/.h pair that shares
a path below core/source/ and core/include/ (core/source/world/world.c +
core/include/world/world.h -> node "world/world"); a lone .c or lone .h is a
node too. Headers resolved outside core/ (e.g. the backend's
sdl/include/platform_defines.h) become "external" nodes.

Edges: "A depends on B" for every #include in A's files that resolves to one of
B's files. Every #include line in the source is listed in the edge's `sites`
column. The preprocessor (clang -E -dI, flags from compile_commands.json) is
used to learn which of those lines are actually reached in the build:
  kind=include           at least one site is active in some translation unit
  kind=include-inactive  no site is active (inside a disabled #if, or only in
                         files that compile_commands.json never compiles)

Exempt nodes: EXEMPT_ROOTS below, everything they include (transitively), and
every external node. The graph viewer leaves them out of hierarchy checks.

Hand-maintained columns survive regeneration:
  nodes: layer, docs, description, tags
  edges: status, note, ai_commentary, tags
An edge that no longer exists in the source but carries a note,
ai_commentary or tags is kept with status=stale so the text isn't lost; otherwise it
is dropped. Each run prints what was added, removed and made stale.

Every node and edge gets a uuid: a UUIDv5 of its identity (node id, or
source->target), so it is stable across runs and comes back unchanged if an
edge is removed and later re-added. Refer to an entry as GRAPH::uuid, e.g.
core::<uuid>; docs/files/graph/lookup.py resolves such refs.
"""

import concurrent.futures
import csv
import json
import os
import re
import shlex
import subprocess
import sys
import uuid

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CORE = os.path.join(REPO, "core")
GRAPH_DIR = os.path.join(REPO, "docs", "files", "graph")
COMPILE_COMMANDS = os.path.join(REPO, "compile_commands.json")

# Header-only roots that sit outside the strict hierarchy. Their transitive
# includes are exempt too.
EXEMPT_ROOTS = ["defines", "defines_weak", "platform"]

# New nodes get the module doc of their top-level directory, when one exists.
MODULE_DOCS = "agents/core/modules"
DOC_FOR_TOP_DIR = {
    "audio": "audio", "client": "client", "collisions": "collisions", "config": "config",
    "debug": "debug", "entity": "entity", "game": "engine", "main": "engine",
    "game_util": "engine", "game_action": "game_action", "input": "input", "log": "log",
    "vectors": "math", "degree": "math", "random": "math", "numerics": "math", "timer": "math",
    "multiplayer": "multiplayer", "process": "process", "raycast": "raycast",
    "rendering": "rendering", "scene": "scene", "serialization": "serialization",
    "sort": "sort", "lav_string": "strings", "core_string": "strings", "ui": "ui",
    "util": "util", "world": "world",
}

# Name of this graph in refs (GRAPH::uuid). The namespace must never change,
# or every ref already handed out stops resolving.
GRAPH_NAME = "core"
UUID_NAMESPACE = uuid.UUID("6f1c2a52-3c1e-4b0e-9a57-5d2f1e7c4a10")


def node_uuid(nid, graph=GRAPH_NAME):
    return str(uuid.uuid5(UUID_NAMESPACE, "%s:node:%s" % (graph, nid)))


def edge_uuid(source, target, graph=GRAPH_NAME):
    return str(uuid.uuid5(UUID_NAMESPACE, "%s:edge:%s->%s" % (graph, source, target)))


NODE_COLUMNS = ["id", "uuid", "label", "layer", "kind", "exempt", "files", "docs", "description", "tags"]
EDGE_COLUMNS = ["source", "target", "uuid", "kind", "weight", "status", "sites", "note", "ai_commentary", "tags"]

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]')
MARKER_RE = re.compile(r'^# \d+ "([^"]+)"(.*)$')


def rel(path):
    return os.path.relpath(path, REPO)


def node_id(path):
    """Absolute file path -> node id, or None for files outside the repo."""
    r = rel(path)
    if r.startswith(".."):
        return None
    stem = os.path.splitext(r)[0]
    for prefix in ("core/include/", "core/source/"):
        if r.startswith(prefix):
            return stem[len(prefix):]
    return stem  # external, or a core/ file outside include/ and source/


# ---------------------------------------------------------------- compile db

def load_compile_db():
    with open(COMPILE_COMMANDS) as f:
        entries = json.load(f)
    tus, include_dirs = [], []
    for e in entries:
        path = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if not path.startswith(CORE + os.sep):
            continue
        args = e.get("arguments") or shlex.split(e["command"])
        tus.append((e["directory"], args, path))
        for i, a in enumerate(args):
            d = a[2:] if a.startswith("-I") and len(a) > 2 else (args[i + 1] if a == "-I" else None)
            if d:
                d = os.path.normpath(os.path.join(e["directory"], d))
                if d not in include_dirs:
                    include_dirs.append(d)
    return tus, include_dirs


def preprocess(tu):
    """Return {(includer_abs, spelled): resolved_abs_or_None} for active #includes."""
    directory, args, path = tu
    cmd = [args[0], "-E", "-dI", "-w"]
    skip = False
    for a in args[1:]:
        if skip:
            skip = False
            continue
        if a in ("-c", "-o", "-MF", "-MT", "-MQ"):
            skip = a != "-c"
            continue
        if a in ("-MD", "-MMD", "-MP") or a == path or os.path.normpath(os.path.join(directory, a)) == path:
            continue
        cmd.append(a)
    cmd.append(path)
    proc = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        print("warning: preprocessing failed for %s:\n%s" % (rel(path), proc.stderr[-800:]), file=sys.stderr)
    active, current, pending = {}, path, None
    for line in proc.stdout.splitlines():
        if line.startswith("#include"):
            m = INCLUDE_RE.match(line)
            if m:
                pending = (os.path.normpath(current), m.group(2))
                active.setdefault(pending, None)
            continue
        m = MARKER_RE.match(line)
        if not m:
            continue
        current = os.path.normpath(os.path.join(directory, m.group(1)))
        flags = m.group(2).split()
        if "1" in flags and pending:
            active[pending] = current  # clang's own resolution of the directive
            pending = None
    return active


# ---------------------------------------------------------------- source scan

def scan_sources():
    files = []
    for root in (os.path.join(CORE, "include"), os.path.join(CORE, "source"), CORE):
        for dp, dns, fns in os.walk(root):
            if root == CORE:
                dns[:] = [d for d in dns if d not in ("include", "source")]
            for fn in fns:
                if fn.endswith((".c", ".h")):
                    files.append(os.path.normpath(os.path.join(dp, fn)))
    return sorted(set(files))


def include_lines(path):
    out = []
    with open(path, errors="replace") as f:
        for n, line in enumerate(f, start=1):
            m = INCLUDE_RE.match(line)
            if m:
                out.append((n, m.group(1), m.group(2)))
    return out


def resolve(includer, quote, spelled, include_dirs):
    dirs = ([os.path.dirname(includer)] if quote == '"' else []) + include_dirs
    for d in dirs:
        p = os.path.normpath(os.path.join(d, spelled))
        if os.path.isfile(p):
            return p
    return None  # system header (stdint.h, ...) or genuinely missing


# ---------------------------------------------------------------- csv merge

def read_csv(path):
    if not os.path.isfile(path):
        return [], []
    with open(path, newline="", encoding="utf-8") as f:
        lines = f.read().splitlines(True)
    comments = [l for l in lines if l.startswith("#")]
    rows = list(csv.DictReader(l for l in lines if not l.startswith("#") and l.strip()))
    return comments, rows


def write_csv(path, header_comment, columns, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(header_comment)
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})


NODES_HEADER = """\
# GENERATED by docs/scripts/graph_from_sources.py: one row per core source module.
# Edit only: layer (id from layers.csv, empty = unassigned), docs (';'-separated
# paths relative to docs/files), description, tags (';'-separated free-form
# labels, searchable in the viewer). Other columns are overwritten on every
# regeneration. uuid: stable id, referred to as core::<uuid>. kind: c+h | c |
# h | external. exempt: yes = outside the strict-hierarchy rules (see
# EXEMPT_ROOTS in the script).
"""
EDGES_HEADER = """\
# GENERATED by docs/scripts/graph_from_sources.py: source depends on target.
# Edit only: status (unreviewed | reviewed | stale), note, ai_commentary, tags
# (';'-separated free-form labels, searchable in the viewer). Other columns
# are overwritten on every regeneration. uuid: stable id, referred to as
# core::<uuid>. sites: every #include line behind the edge (file:line).
# kind: include | include-inactive (no site is reached by the preprocessor in
# any translation unit).
"""


def main():
    tus, include_dirs = load_compile_db()
    print("compile_commands.json: %d core translation units, %d include dirs" % (len(tus), len(include_dirs)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        active = {}
        for result in pool.map(preprocess, tus):
            for k, v in result.items():
                if v or k not in active:
                    active[k] = v

    sources = scan_sources()
    nodes = {}  # id -> {"files": set, "external": bool}
    for p in sources:
        nodes.setdefault(node_id(p), {"files": set(), "external": False})["files"].add(rel(p))

    edges = {}  # (src, dst) -> {"sites": [...], "active": bool}
    file_includes = {}  # abs path -> set of abs paths it #includes
    mismatches = 0
    for p in sources:
        src = node_id(p)
        for line_no, quote, spelled in include_lines(p):
            target = resolve(p, quote, spelled, include_dirs)
            key = (p, spelled)
            if key in active and active[key] and target and active[key] != target:
                mismatches += 1
                target = active[key]  # trust the compiler
            if not target:
                continue
            file_includes.setdefault(p, set()).add(target)
            dst = node_id(target)
            if dst is None or dst == src:
                continue
            if dst not in nodes:
                nodes[dst] = {"files": set(), "external": True}
            nodes[dst]["files"].add(rel(target))
            e = edges.setdefault((src, dst), {"sites": [], "active": False})
            e["sites"].append("%s:%d" % (rel(p), line_no))
            e["active"] = e["active"] or key in active
    if mismatches:
        print("note: %d #include lines resolved differently by clang; clang's answer was used" % mismatches)

    # exempt = roots + every file they #include, transitively, followed file by
    # file (a header pulled in this way does not drag its .c along) + externals
    exempt_files = {os.path.join(CORE, "include", r + ".h") for r in EXEMPT_ROOTS}
    stack = list(exempt_files)
    while stack:
        for t in file_includes.get(stack.pop(), ()):
            if t not in exempt_files:
                exempt_files.add(t)
                stack.append(t)
    exempt = {node_id(f) for f in exempt_files if os.path.isfile(f)}
    exempt |= {n for n, v in nodes.items() if v["external"]}

    # merge with hand-maintained columns
    node_csv = os.path.join(GRAPH_DIR, "nodes.csv")
    edge_csv = os.path.join(GRAPH_DIR, "edges.csv")
    _, old_nodes = read_csv(node_csv)
    _, old_edges = read_csv(edge_csv)
    old_n = {r["id"]: r for r in old_nodes}
    old_e = {(r["source"], r["target"]): r for r in old_edges}

    node_rows = []
    for nid in sorted(nodes):
        v, prev = nodes[nid], old_n.get(nid, {})
        exts = {os.path.splitext(f)[1] for f in v["files"]}
        kind = "external" if v["external"] else "+".join(k for k in ("c", "h") if "." + k in exts)
        docs = prev.get("docs")
        if docs is None:
            top = nid.split("/")[0]
            doc = DOC_FOR_TOP_DIR.get(top)
            docs = "%s/%s.md" % (MODULE_DOCS, doc) if doc else ""
        node_rows.append({
            "id": nid, "label": nid.rsplit("/", 1)[-1], "layer": prev.get("layer", ""),
            "kind": kind, "exempt": "yes" if nid in exempt else "",
            "files": ";".join(sorted(v["files"])), "docs": docs,
            "description": prev.get("description", ""), "tags": prev.get("tags", ""),
        })

    edge_rows, added, stale, dropped = [], 0, 0, 0
    for (s, d) in sorted(edges):
        e, prev = edges[(s, d)], old_e.get((s, d))
        if prev is None:
            added += 1
        status = (prev or {}).get("status") or "unreviewed"
        if status == "stale":
            status = "unreviewed"  # it came back
        edge_rows.append({
            "source": s, "target": d, "kind": "include" if e["active"] else "include-inactive",
            "weight": len(e["sites"]), "status": status, "sites": ";".join(e["sites"]),
            "note": (prev or {}).get("note", ""), "ai_commentary": (prev or {}).get("ai_commentary", ""),
            "tags": (prev or {}).get("tags", ""),
        })
    node_ids = set(nodes)
    for key, prev in old_e.items():
        if key in edges:
            continue
        if (prev.get("note") or prev.get("ai_commentary") or prev.get("tags")) and key[0] in node_ids and key[1] in node_ids:
            stale += 1
            edge_rows.append(dict(prev, status="stale"))
        else:
            dropped += 1
    edge_rows.sort(key=lambda r: (r["source"], r["target"]))
    for r in node_rows:
        r["uuid"] = node_uuid(r["id"])
    for r in edge_rows:
        r["uuid"] = edge_uuid(r["source"], r["target"])

    write_csv(node_csv, NODES_HEADER, NODE_COLUMNS, node_rows)
    write_csv(edge_csv, EDGES_HEADER, EDGE_COLUMNS, edge_rows)
    inactive = sum(1 for r in edge_rows if r["kind"] == "include-inactive")
    print("nodes: %d (%d exempt, %d external)" % (len(node_rows), len(exempt),
                                                 sum(1 for v in nodes.values() if v["external"])))
    print("edges: %d (%d inactive); added %d, made stale %d, dropped %d"
          % (len(edge_rows), inactive, added, stale, dropped))


if __name__ == "__main__":
    main()
