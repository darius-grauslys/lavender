"""MkDocs hook: compile docs/files/graph/*.csv into graph/graph-data.js.

nodes.csv and edges.csv are generated from core/'s #include graph by
docs/scripts/graph_from_sources.py; layers.csv is hand-written.

The architecture graph viewer (docs/files/graph/viewer.html) must work when the
built site is opened over file://, where browsers refuse fetch()/XHR of local
files. A <script src> is still allowed, so the CSVs are turned into a JS file
that assigns window.LAVENDER_GRAPH.

The CSVs are the single source of truth; this hook only parses, validates and
converts them. Problems are reported as build warnings (mkdocs build --strict
turns them into errors).

CSV conventions (all three files):
  - first row is the header
  - a row whose first cell starts with '#' is a comment
  - blank rows are ignored
  - multi-valued cells are separated by ';'
"""

import csv
import json
import logging
import os

log = logging.getLogger("mkdocs.hooks.graph_data")

GRAPH_DIR = "graph"
OUT_FILE = "graph-data.js"
GRAPH_NAME = "core"  # refs are GRAPH_NAME::uuid; see graph_from_sources.py

LAYER_COLUMNS = ["id", "rank", "label", "color", "description"]
NODE_COLUMNS = ["id", "uuid", "label", "layer", "kind", "exempt", "files", "docs", "description", "tags"]
EDGE_COLUMNS = ["source", "target", "uuid", "kind", "weight", "status", "sites", "note", "ai_commentary", "tags"]


def _read_csv(path, columns):
    if not os.path.isfile(path):
        log.warning("graph: missing %s", path)
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = None
        for line_no, raw in enumerate(reader, start=1):
            if not raw or all(not c.strip() for c in raw):
                continue
            if raw[0].lstrip().startswith("#"):
                continue
            cells = [c.strip() for c in raw]
            if header is None:
                header = cells
                missing = [c for c in columns if c not in header]
                if missing:
                    log.warning("graph: %s header lacks columns %s", path, missing)
                continue
            row = {c: (cells[header.index(c)] if c in header and header.index(c) < len(cells) else "")
                   for c in columns}
            row["_line"] = line_no
            rows.append(row)
    return rows


def _tags(cell):
    """';'-separated tags -> list, trimmed and de-duplicated, order kept."""
    out = []
    for t in cell.split(";"):
        t = t.strip()
        if t and t not in out:
            out.append(t)
    return out


def _doc_href(docs_dir, md_path, where):
    """docs/files-relative .md path -> link relative to site/graph/."""
    md_path = md_path.strip().lstrip("/")
    if not os.path.exists(os.path.join(docs_dir, md_path)):
        log.warning("graph: %s references missing doc '%s'", where, md_path)
    if md_path.endswith(".md"):
        md_path = md_path[:-3] + ".html"
    return "../" + md_path


def _build(docs_dir):
    gdir = os.path.join(docs_dir, GRAPH_DIR)
    layers = _read_csv(os.path.join(gdir, "layers.csv"), LAYER_COLUMNS)
    nodes = _read_csv(os.path.join(gdir, "nodes.csv"), NODE_COLUMNS)
    edges = _read_csv(os.path.join(gdir, "edges.csv"), EDGE_COLUMNS)

    layer_ids = set()
    out_layers = []
    for l in layers:
        where = "layers.csv:%d" % l["_line"]
        try:
            rank = float(l["rank"])
        except ValueError:
            log.warning("graph: %s rank '%s' is not a number", where, l["rank"])
            continue
        if l["id"] in layer_ids:
            log.warning("graph: %s duplicate layer id '%s'", where, l["id"])
        layer_ids.add(l["id"])
        out_layers.append({"id": l["id"], "rank": rank, "label": l["label"] or l["id"],
                           "color": l["color"], "description": l["description"]})

    node_ids = set()
    out_nodes = []
    for n in nodes:
        where = "nodes.csv:%d" % n["_line"]
        if not n["id"]:
            log.warning("graph: %s node without id", where)
            continue
        if n["id"] in node_ids:
            log.warning("graph: %s duplicate node id '%s'", where, n["id"])
        node_ids.add(n["id"])
        if n["layer"] and n["layer"] not in layer_ids:
            log.warning("graph: %s node '%s' has unknown layer '%s'", where, n["id"], n["layer"])
        docs = [d for d in n["docs"].split(";") if d.strip()]
        out_nodes.append({
            "id": n["id"], "uuid": n["uuid"], "label": n["label"] or n["id"], "layer": n["layer"],
            "kind": n["kind"], "description": n["description"], "tags": _tags(n["tags"]),
            "exempt": n["exempt"].lower() in ("yes", "y", "true", "1"),
            "files": [p.strip() for p in n["files"].split(";") if p.strip()],
            "docs": [{"path": d.strip(), "href": _doc_href(docs_dir, d, where)} for d in docs],
        })

    out_edges = []
    for e in edges:
        where = "edges.csv:%d" % e["_line"]
        bad = [k for k in ("source", "target") if e[k] not in node_ids]
        if bad:
            log.warning("graph: %s edge %s -> %s references unknown node(s) %s",
                        where, e["source"], e["target"], [e[k] for k in bad])
            continue
        try:
            weight = float(e["weight"]) if e["weight"] else 1
        except ValueError:
            log.warning("graph: %s weight '%s' is not a number", where, e["weight"])
            weight = 1
        sites = [p.strip() for p in e["sites"].split(";") if p.strip()]
        out_edges.append({"source": e["source"], "target": e["target"], "uuid": e["uuid"],
                          "kind": e["kind"] or "depends", "weight": weight,
                          "status": e["status"], "note": e["note"],
                          "ai_commentary": e["ai_commentary"], "sites": sites,
                          "tags": _tags(e["tags"]),
                          # does any #include behind this edge sit in a header?
                          "from_header": any(p.split(":")[0].endswith(".h") for p in sites)})

    seen = {}
    for kind, items in (("node", out_nodes), ("edge", out_edges)):
        for x in items:
            name = x["id"] if kind == "node" else "%s -> %s" % (x["source"], x["target"])
            if not x["uuid"]:
                log.warning("graph: %s '%s' has no uuid (re-run graph_from_sources.py)", kind, name)
            elif x["uuid"] in seen:
                log.warning("graph: %s '%s' reuses the uuid of %s", kind, name, seen[x["uuid"]])
            else:
                seen[x["uuid"]] = name

    return {"graph": GRAPH_NAME, "layers": out_layers, "nodes": out_nodes, "edges": out_edges}


def on_post_build(config, **kwargs):
    graph = _build(config["docs_dir"])
    out_dir = os.path.join(config["site_dir"], GRAPH_DIR)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, OUT_FILE), "w", encoding="utf-8") as f:
        f.write("// Generated by docs/hooks/graph_data.py from graph/*.csv. Do not edit.\n")
        f.write("window.LAVENDER_GRAPH = ")
        json.dump(graph, f, indent=1)
        f.write(";\n")
    log.info("graph: %d layers, %d nodes, %d edges",
             len(graph["layers"]), len(graph["nodes"]), len(graph["edges"]))


if __name__ == "__main__":
    # Regenerate only the graph data, without a full mkdocs build (seconds, not
    # a minute). Run from the repo root after editing the CSVs:
    #   python3 docs/hooks/graph_data.py
    # Needs an existing docs/site/ from a previous build for the viewer itself.
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s -  %(message)s")
    here = os.path.dirname(os.path.abspath(__file__))
    on_post_build({"docs_dir": os.path.join(here, "..", "files"),
                   "site_dir": os.path.join(here, "..", "site")})
