# Architecture graph

The `#include` graph of `core/`, one node per source module (a `.c`/`.h` pair,
or a lone `.c` or `.h`). [Open full screen](viewer.html){ target=_blank }

<iframe src="viewer.html" title="Architecture graph"
        style="width: 100%; height: 75vh; border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px;"></iframe>

Click a node to see its files, docs and edges; click an edge (or *details*) to
see the `#include` lines behind it. Deep-link with `viewer.html#<node-id>`,
e.g. [`viewer.html#world/world`](viewer.html#world/world).

Every node and edge has a stable ref, `core::<uuid>`, shown in its side panel
with a **copy** button. Paste it into *Find* to jump back to it, or hand it to
an agent, which resolves it with `lookup.py` (below).

## Reading the graph

- **By depth** stacks nodes by the longest dependency chain beneath them:
  depth 0 depends on nothing (outside the exempt set). In a strict hierarchy
  every edge points downward.
- **Cycles** (orange) are found live over the edges the current filters show.
  All nodes of one cycle group share a depth band, marked ⟳.
- **Header includes only** drops edges whose `#include`s all sit in `.c` files,
  leaving the interface-level graph.
- **Exempt** nodes, `defines.h`, `defines_weak.h`, `platform.h` and everything
  they include, plus headers resolved outside `core/`, are hidden by default
  and never take part in cycle or layer checks.
- **Inactive** edges exist only in disabled `#if` branches or in files the build
  never compiles.

Node shapes: circle `.c`+`.h`, square `.h` only, diamond `.c` only, hexagon external.

## Updating the graph

| File | Maintained by | You edit |
|------|---------------|----------|
| `nodes.csv` | `docs/scripts/graph_from_sources.py` | `layer`, `docs`, `description`, `tags` |
| `edges.csv` | `docs/scripts/graph_from_sources.py` | `status`, `note`, `ai_commentary`, `tags` |
| `layers.csv` | hand-written | everything |
| `proposed_hierarchy.csv` | hand-written (module-level proposal, refs `proposed::<uuid>`) | everything but `uuid` |

```bash
python3 docs/scripts/graph_from_sources.py   # re-read core/ (uses compile_commands.json + clang)
python3 docs/hooks/graph_data.py             # refresh the viewer data only (no full build)
```

The generator keeps hand-edited columns across runs. An edge that disappears
from the source but has a `note` or `ai_commentary` is kept with
`status=stale` instead of being deleted. `mkdocs build` runs
`docs/hooks/graph_data.py`, which validates the CSVs and writes
`site/graph/graph-data.js`; the data is compiled to JavaScript because browsers
block reading local `.csv` files over `file://`.

`uuid` is a UUIDv5 of the entry's identity (node id, or source → target), so it
survives regeneration and an edge that is removed and re-added gets its old ref
back.

## Scripts for agents

```bash
python3 docs/files/graph/lookup.py core::<uuid>           # print an entry (also: node id, 'a->b', --json)
python3 docs/files/graph/edge.py remove core::<uuid>      # delete the #includes behind an edge
python3 docs/files/graph/edge.py add <file.c|.h> <node>   # add #include "<node>.h" to a file
```

`lookup.py` prints every column of the entry; for an edge also the `#include`
line at each site, for a node the refs of all its edges.

`edge.py` changes edges where they come from, the `#include` lines in `core/`,
then re-runs the generator. `remove` checks that each site is still an
`#include` of the target before deleting it, and takes `--site FILE:LINE` to
remove only some of them; an edge with a `note`, `ai_commentary` or `tags`
stays in `edges.csv` as `stale`. Both take `--dry-run`. Neither builds the
code, so build afterwards: a "stray" include may have been needed after all.
