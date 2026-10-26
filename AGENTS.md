# AGENTS.md

DO NOT UPDATE WITHOUT HUMAN DIRECTIVE TO DO SO.

## Lavender

Lavender is a cross-platform multiplayer retro game engine, written in C. It
lets you target whichever retro console you want, and lets players on
*different* consoles play together in the same multiplayer instance. It
achieves this with fixed-size memory pools configured at build time for the
target platform; these build configurations are advertised as *performance
profiles*, and the least performant profile is used for all players so every
client stays in lockstep (with a few client-side exceptions, e.g. rendering
quality/effects).

The engine is developed as a strict hierarchical tree: `core/` is the portable,
console-agnostic engine, and each console is a backend (`nds/`, `sdl/`,
`no_gui/`, …) implementing the `platform.h` abstraction.

## Working with the source

**Do not modify any `.c` or `.h` file unless specifically instructed to.** The
human operator changes the code by hand; the AI's role is to help them
identify the changes needed. Investigate, then report what to change and
where (file, line, the edit itself, and why), and leave the editing to them.
This includes indirect edits, such as scripts that rewrite source files.

**Exception: `Agent-[UUID]` branches.** If the current branch
(`git branch --show-current`) is named `Agent-<uuid>`, you were started by
the agent pipeline to solve an issue: the rule above does not apply, and you
should edit source files directly. The resulting merge request is never
merged. The human operator reads it, writes every line himself (possibly with
changes), then closes it. So write for that reader: small commits, one logical
step each, with messages that explain why.

## Building

Builds take `-e PLATFORM=<platform>` (`sdl`, `no_gui`, `nds`, …) and run from
the repo root with `LAVENDER_DIR` set to it (the agent sandbox sets it), e.g.
`make -j4 -e PLATFORM=sdl`. Use `-j` with the machine's
CPU count; the agent sandbox has 4.

`compile_commands.json` (clang tooling, `graph_from_sources.py`) is generated
and gitignored. Don't run a full build to get it:

```bash
make -e PLATFORM=sdl compile_commands_dry   # prints the compile commands, compiles nothing (~1s)
```

In the agent sandbox, `solve.sh` generates it before you start; rerun it after
changing the build. Bash commands there time out after 5 minutes by default.

## Documentation

Engine: **MkDocs + Material** (config in `mkdocs.yml` at the repo root).

- **Canonical docs are the Markdown files in `docs/files/`.** The tree mirrors
  the engine source tree, and sidebar navigation is generated from the file
  structure — there is no nav list to maintain.
- `docs/site/` is built output (gitignored), for human browsing over `file://`.
  `docs/.venv/` is the docs toolchain (gitignored).

### How to update

1. Add/edit/move `.md` files under `docs/files/`. One page per module, at a
   path mirroring the source tree (`docs/files/<module>/index.md` for
   source dir `<module>/`). Use H1 for the page title and relative links
   between pages (MkDocs validates links at build time).
2. Rebuild from the repo root:

   ```bash
   docs/.venv/bin/mkdocs build
   ```

   For quick iteration, `mkdocs build --dirty` rebuilds only changed pages
   (~1s), but leaves other pages' sidebars stale when files are added or
   moved — do a plain build before committing.

Renaming a source directory = moving the corresponding doc directory; the nav
follows automatically.

### Architecture graph

`docs/files/graph/` holds the `#include` graph of `core/`, drawn by
`viewer.html` (embedded in `graph/index.md`). It is the working map of the
strict hierarchy: one node per source module (`.c`/`.h` pair, or a lone `.c`
or `.h`), one edge per "A `#include`s B".

- `nodes.csv` / `edges.csv` are **generated** by
  `python3 docs/scripts/graph_from_sources.py` (reads `core/` via
  `compile_commands.json` + clang). Re-run it after changing includes.
- `layers.csv` is hand-written.
- Exempt from hierarchy rules: `defines.h`, `defines_weak.h`, `platform.h`,
  everything they include, and headers outside `core/` (`exempt=yes`).
- `python3 docs/hooks/graph_data.py` refreshes the viewer data without a full
  build; `mkdocs build` does it too and warns about bad CSV rows.

Only these columns are hand-maintained; regeneration overwrites all others:

| File | Editable columns |
|------|------------------|
| `nodes.csv` | `layer`, `docs`, `description`, `tags` |
| `edges.csv` | `status`, `note`, `ai_commentary`, `tags` |

`tags` (nodes and edges) holds free-form, `;`-separated labels (e.g.
`game-ptr;cut-candidate`) that the viewer's Tag search filters on. Reuse
existing tags where one fits rather than inventing near-duplicates.

#### Refs, lookup and edge edits

Every node and edge has a generated, stable `uuid`; humans copy it from the
viewer as a ref, `core::<uuid>` (`proposed::<uuid>` for the hand-written
`proposed_hierarchy.csv`). When handed a ref, resolve it instead of grepping:

```bash
python3 docs/files/graph/lookup.py core::<uuid>   # also: node id, 'a->b', --json
```

It prints the entry's columns, plus the `#include` line at each site (edges)
or the refs of every edge (nodes).

To remove a stray include, or add one, use `docs/files/graph/edge.py`. It edits
the `#include` lines in `core/` and regenerates the CSVs. Never delete or add
edge rows by hand: the next regeneration would undo it.

```bash
python3 docs/files/graph/edge.py remove core::<uuid> [--site FILE:LINE] --dry-run
python3 docs/files/graph/edge.py add <file.c|.h> <node-id|core::uuid> --dry-run
```

`edge.py` modifies `.c`/`.h` files, so the rule in *Working with the source*
applies: run it for real only when a human specifically instructs you to, or
on an `Agent-<uuid>` branch.
Otherwise flag the stray include in `ai_commentary`, or show the human the
`--dry-run` output so they can make the change themselves. After a real run,
build the affected targets: neither command compiles anything.

#### `ai_commentary` (edges.csv)

Agents document **why an edge exists**: what the source module actually uses
from the target (types, functions, macros) and whether that dependency belongs
in the hierarchy. To fill one in:

1. Read the edge's `sites` column — every `#include` behind it, as `file:line`.
   Open those files, find what is used from the target, and nothing more.
2. Write one or two plain sentences, e.g.
   `world.c calls hold_global_space()/drop_global_space(); only the .c needs it, header could forward-declare Global_Space.`
   Name the concrete symbols. Flag suspected layering problems ("lower module
   reaching up into game.h for Game*") rather than fixing them.
3. Keep the CSV valid: quote the cell if it contains a comma, double any `"`
   inside it, no newlines.
4. Do not change `status` — `reviewed` is a human decision. Do not edit
   generated columns or reorder rows.

An edge that disappears from the source keeps its commentary and tags with
`status=stale`; leave those for a human to delete.

### How to read (context-friendly)

Agents should read the Markdown in `docs/files/` directly — never the HTML.
`ls docs/files/` gives the same map as the sidebar; grep `^#` for a page
outline; grep for a symbol to locate its module page, then read just that file.
