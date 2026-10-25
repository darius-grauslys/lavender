#!/usr/bin/env python3
"""Look up graph entries by ref, as copied from the graph viewer.

Usage (from the repo root):
  python3 docs/files/graph/lookup.py core::<uuid> [more refs...]
  python3 docs/files/graph/lookup.py world/world               # node id
  python3 docs/files/graph/lookup.py 'world/world->game'       # edge by ends
  python3 docs/files/graph/lookup.py --json core::<uuid>

A ref is GRAPH::uuid. Graphs:
  core      nodes.csv + edges.csv, the generated #include graph of core/
  proposed  proposed_hierarchy.csv, a hand-written module-level proposal
A bare uuid is searched in every graph.

For a core edge the #include line behind every site is printed; for a core
node, its files and the refs of all its edges, so they can be looked up next.
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

GRAPHS = {
    "core": {"nodes": "nodes.csv", "edges": "edges.csv"},
    "proposed": {"nodes": None, "edges": "proposed_hierarchy.csv"},
}


def read_rows(name):
    path = os.path.join(HERE, name)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#") and l.strip()))


def load(graph):
    files = GRAPHS[graph]
    return {k: (read_rows(v) if v else []) for k, v in files.items()}


def edge_name(row):
    return "%s -> %s" % (row["source"], row["target"])


def find(query):
    """Return [(graph, "node" | "edge", row)] matching query."""
    graph, _, key = query.rpartition("::")
    graphs = [graph] if graph else list(GRAPHS)
    for g in graphs:
        if g not in GRAPHS:
            sys.exit("unknown graph '%s' (known: %s)" % (g, ", ".join(GRAPHS)))
    hits = []
    for g in graphs:
        data = load(g)
        for kind in ("nodes", "edges"):
            for row in data[kind]:
                if row.get("uuid") == key:
                    hits.append((g, kind[:-1], row))
        if hits or graph:
            continue
        # not a uuid: try a node id, then "source->target"
        for row in data["nodes"]:
            if row["id"] == key:
                hits.append((g, "node", row))
        if "->" in key:
            s, t = (x.strip() for x in key.split("->", 1))
            for row in data["edges"]:
                if row["source"] == s and row["target"] == t:
                    hits.append((g, "edge", row))
    return hits


def site_text(site):
    path, _, line = site.rpartition(":")
    try:
        with open(os.path.join(REPO, path), errors="replace") as f:
            for n, text in enumerate(f, start=1):
                if n == int(line):
                    return text.strip()
    except (OSError, ValueError):
        pass
    return "(line not found; the graph may be out of date)"


def describe(graph, kind, row):
    out = {"ref": "%s::%s" % (graph, row["uuid"]), "graph": graph, "type": kind,
           "fields": {k: v for k, v in row.items() if v}}
    if graph == "core" and kind == "edge":
        out["include_lines"] = [{"site": s, "text": site_text(s)}
                                for s in row["sites"].split(";") if s]
    if graph == "core" and kind == "node":
        edges = load(graph)["edges"]
        out["depends_on"] = ["%s  %s::%s" % (e["target"], graph, e["uuid"])
                             for e in edges if e["source"] == row["id"]]
        out["used_by"] = ["%s  %s::%s" % (e["source"], graph, e["uuid"])
                          for e in edges if e["target"] == row["id"]]
    return out


def print_text(d):
    row = d["fields"]
    title = row.get("id") or "%s -> %s" % (row.get("source"), row.get("target"))
    print("%s %s  (%s)" % (d["type"], title, d["ref"]))
    for k, v in row.items():
        if k in ("uuid", "id", "source", "target"):
            continue
        if ";" in v and k in ("files", "docs", "sites", "tags"):
            print("  %s:" % k)
            for part in v.split(";"):
                print("    %s" % part)
        else:
            print("  %s: %s" % (k, v))
    if "include_lines" in d:
        print("  include lines:")
        for x in d["include_lines"]:
            print("    %s  %s" % (x["site"], x["text"]))
    for k in ("depends_on", "used_by"):
        if k in d:
            print("  %s (%d):" % (k.replace("_", " "), len(d[k])))
            for x in d[k]:
                print("    %s" % x)


def main(argv):
    as_json = "--json" in argv
    queries = [a for a in argv if a != "--json"]
    if not queries or any(q in ("-h", "--help") for q in queries):
        print(__doc__.strip())
        return 0 if queries else 2
    status, results = 0, []
    for q in queries:
        hits = find(q)
        if not hits:
            print("no entry matches '%s'" % q, file=sys.stderr)
            status = 1
        results.extend(describe(*h) for h in hits)
    if as_json:
        json.dump(results, sys.stdout, indent=1)
        print()
    else:
        for i, d in enumerate(results):
            if i:
                print()
            print_text(d)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
