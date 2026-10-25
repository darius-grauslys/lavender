#!/usr/bin/env python3
"""Add or remove an edge of the core #include graph.

edges.csv is generated from the source, so an edge is changed where it comes
from: this script edits the #include lines in core/, then re-runs
docs/scripts/graph_from_sources.py so the CSVs follow.

Usage (from the repo root):
  python3 docs/files/graph/edge.py remove core::<uuid> [--site FILE:LINE ...]
  python3 docs/files/graph/edge.py add core/source/world/chunk.c world/tile
  python3 docs/files/graph/edge.py add core/source/world/chunk.c core::<node-uuid>

remove  deletes every #include behind the edge (or only the --site ones).
        Each line is checked to still be an #include that resolves to the
        target, so a stale graph cannot delete the wrong line. An edge with a
        note, ai_commentary or tags is kept in edges.csv with status=stale.
add     inserts #include "<target header>" after the last #include of the
        given source file (the edge's source is that file's node).

Options:
  --dry-run   print what would change, touch nothing
  --no-regen  edit the source but do not regenerate the CSVs

Neither command builds the code. Build the affected targets afterwards: a
removed include may have been needed after all.
"""

import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of docs/files (and the built site)
from lookup import REPO, find, read_rows

GENERATOR = os.path.join(REPO, "docs", "scripts", "graph_from_sources.py")
_spec = importlib.util.spec_from_file_location("graph_from_sources", GENERATOR)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def die(msg):
    sys.exit("error: " + msg)


def one(query, kind):
    hits = [h for h in find(query) if h[0] == "core" and h[1] == kind]
    if len(hits) != 1:
        die("'%s' matches %d core %ss" % (query, len(hits), kind))
    return hits[0][2]


def node_files(nid):
    for row in read_rows("nodes.csv"):
        if row["id"] == nid:
            return {os.path.join(REPO, f) for f in row["files"].split(";") if f}
    die("unknown node '%s'" % nid)


def regenerate():
    subprocess.run([sys.executable, GENERATOR], check=True)


def current_edge(source, target):
    for row in read_rows("edges.csv"):
        if row["source"] == source and row["target"] == target:
            return row
    return None


def remove(query, only_sites, dry_run, regen):
    edge = one(query, "edge")
    sites = [s for s in edge["sites"].split(";") if s]
    if only_sites:
        unknown = [s for s in only_sites if s not in sites]
        if unknown:
            die("not sites of this edge: %s (sites: %s)" % (", ".join(unknown), ", ".join(sites)))
        sites = only_sites
    if not sites:
        die("edge has no #include sites (stale?); edit edges.csv by hand")
    _, include_dirs = gen.load_compile_db()
    targets = node_files(edge["target"])

    by_file = {}
    for site in sites:
        path, _, line = site.rpartition(":")
        abs_path, n = os.path.join(REPO, path), int(line)
        with open(abs_path, errors="replace") as f:
            lines = f.readlines()
        m = gen.INCLUDE_RE.match(lines[n - 1]) if n <= len(lines) else None
        resolved = m and gen.resolve(abs_path, m.group(1), m.group(2), include_dirs)
        if not m or resolved not in targets:
            die("%s is no longer an #include of %s; regenerate the graph first:\n  python3 %s"
                % (site, edge["target"], os.path.relpath(GENERATOR)))
        by_file.setdefault(abs_path, []).append(n)
        print("remove %s  %s" % (site, lines[n - 1].strip()))
    if dry_run:
        return

    for abs_path, numbers in by_file.items():
        with open(abs_path, errors="replace") as f:
            lines = f.readlines()
        for n in sorted(numbers, reverse=True):
            del lines[n - 1]
        with open(abs_path, "w") as f:
            f.writelines(lines)
    if not regen:
        return
    regenerate()
    after = current_edge(edge["source"], edge["target"])
    if after is None:
        print("edge %s -> %s removed" % (edge["source"], edge["target"]))
    elif after["status"] == "stale":
        print("edge kept in edges.csv as status=stale (it has a note, ai_commentary or tags)")
    else:
        print("edge still present through: %s" % after["sites"])


def insertion_point(lines):
    last_include = max((i for i, l in enumerate(lines) if gen.INCLUDE_RE.match(l)), default=None)
    if last_include is not None:
        return last_include + 1
    for i, l in enumerate(lines):  # after an include guard's #define
        if l.lstrip().startswith("#define") and i and lines[i - 1].lstrip().startswith("#ifndef"):
            return i + 1
    return 0


def add(source_file, query, dry_run, regen):
    abs_src = os.path.abspath(source_file)
    if not abs_src.startswith(gen.CORE + os.sep) or not os.path.isfile(abs_src):
        die("%s is not a file under core/" % source_file)
    target = one(query, "node")["id"]
    include_root = os.path.join(gen.CORE, "include") + os.sep
    headers = sorted(f for f in node_files(target) if f.endswith(".h") and f.startswith(include_root))
    if not headers:
        die("node '%s' has no header under core/include to include" % target)
    header = headers[0]
    spelled = os.path.relpath(header, include_root)
    _, include_dirs = gen.load_compile_db()

    with open(abs_src, errors="replace") as f:
        lines = f.readlines()
    for n, quote, name in gen.include_lines(abs_src):
        if gen.resolve(abs_src, quote, name, include_dirs) == header:
            die("%s:%d already includes %s" % (gen.rel(abs_src), n, spelled))
    if gen.resolve(abs_src, '"', spelled, include_dirs) != header:
        die('#include "%s" would not resolve to %s from %s' % (spelled, gen.rel(header), gen.rel(abs_src)))

    at = insertion_point(lines)
    text = '#include "%s"\n' % spelled
    source = gen.node_id(abs_src)
    print("add %s:%d  %s" % (gen.rel(abs_src), at + 1, text.strip()))
    print("edge %s -> %s  core::%s" % (source, target, gen.edge_uuid(source, target)))
    if dry_run:
        return
    lines.insert(at, text)
    with open(abs_src, "w") as f:
        f.writelines(lines)
    if regen:
        regenerate()


def main(argv):
    flags = {a for a in argv if a in ("--dry-run", "--no-regen")}
    args = [a for a in argv if a not in flags]
    only_sites = []
    while "--site" in args:
        i = args.index("--site")
        if i + 1 >= len(args):
            die("--site needs FILE:LINE")
        only_sites.append(args.pop(i + 1))
        args.pop(i)
    dry_run, regen = "--dry-run" in flags, "--no-regen" not in flags
    if len(args) == 2 and args[0] == "remove":
        remove(args[1], only_sites, dry_run, regen)
    elif len(args) == 3 and args[0] == "add" and not only_sites:
        add(args[1], args[2], dry_run, regen)
    else:
        print(__doc__.strip())
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
