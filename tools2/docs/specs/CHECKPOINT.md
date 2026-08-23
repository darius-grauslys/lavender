# Lavender Tools v2 — Context Checkpoint

> **Date:** 2026-05-22  
> **Purpose:** Contextual save point for continued AI work on the tools v2 remake.
> This document is the **primary context injection point** for any AI agent
> continuing this effort.  Read this FIRST, then the spec files it references.

---

## 0. What Happened and Why

On May 22, 2026, the Lavender engine's MCP tooling (`tools/lavender_tools/`,
~22,800 lines across ~55 files) was subjected to a full adversarial systems-
level audit using four parallel Kimi-v2.6 subagents.  The audit was
commissioned because the tooling had grown into an unmaintainable state
through feature-by-feature accretion without an architecture phase.

**The verdict was unambiguous: the tooling cannot be incrementally fixed.**

A ground-up reimplementation was initiated as `tools2/` with a full
specification system written before any code.  This checkpoint captures
every decision, every constraint, and every piece of historical context
that an AI agent needs to execute the reimplementation correctly.

---

## 1. The Audit — What Was Found

### 1.1. Composite Scores (out of 10)

| Dimension | Score | One-Line Verdict |
|-----------|-------|-----------------|
| Traceability | **3** | `tool_history` is broken by default and opt-in; most tools skip it |
| Maintainability | **2** | Adding one tool requires editing 4 files; ~4,400 lines of duplicate wrappers |
| Consistency | **3** | 4 names for `project_dir`, 3 GEN-marker parsers, 2 scan output schemas |
| AI-Native Readiness | **3** | No formal schemas; `mod_entity` is single-use; no error→fix mapping |
| Mutation Safety | **2** | Zero atomic writes, zero file locking, zero rollback in mod tools |
| Test Coverage | **4** | 94% surface but 86% shallow subprocess mocks; no C output correctness tests |
| Architectural Coherence | **2** | Half-finished migration; circular `lav_impl → lav_ai` dependency |

### 1.2. Five Active Bugs at Time of Audit

1. **`lav_ai_app.py:1779`** — First `clangd_references` definition calls
   `find_definition` (wrong function).  Masked by second definition
   shadowing it at line 1814.

2. **`tool_history.py:~48`** — `Path(__file__).resolve().parents[1]`
   resolves to `tools/`, not project root.  Without `$LAVENDER_DIR` env
   var, entire traceability system silently no-ops.

3. **`scan_entity.py:135`, `scan_ui.py:100`** — `split("\\n")` splits on
   literal two-char sequence, not newline.  Symbol location parsing broken.

4. **`mod_png.py`** — Renames source to `ORIGINAL_*` BEFORE `img.save()`.
   Process crash during save leaves working file missing.
   `os._exit(1)` in SIGALRM handler skips all `finally` blocks.

5. **`requirements.txt`** — Declares `pyglet` (windowing lib) instead of
   `pygls` (LSP framework actually used by clangd integration).

### 1.3. Structural Failures

- **Duplicate implementations**: `lav_ai_app.py` (2,631 lines) and
  `lav_impl/tools.py` (2,293 lines) contain identical 53-tool signature
  sets that have already diverged (`project_root` vs `project_dir`).

- **Copy-paste as architecture**: `_parse_gen_entries()` copied across 4
  scan files.  `_get_lavender_dir()` duplicated in 6 files.  `read_file()`
  / `write_file()` copied between gen_sprite and gen_aliased_texture.

- **Three GEN-marker parser implementations**: `mod_entity` (str.find),
  `mod_scene` (str.find, different variant), scan tools (regex).

- **Two scan output schemas**: Verification scanners emit `{results: [...]}`,
  inventory scanners emit bespoke structures.

- **God files**: `mod_png.py` (1,029 lines), `lav_impl/tools.py`
  (2,293 lines), `lav_ai_app.py` (2,631 lines),
  `test_tool_invocations.py` (2,599 lines).

- **Circular dependency**: `lav_impl/tools.py` (the "new, protocol-agnostic"
  layer) imports `lav_ai.clang_server` (the "old" MCP server layer).

---

## 2. Historical Context — Why Things Are the Way They Are

### 2.1. The MCP SDK stdio Deadlock

**Open Brain reference:** "CRITICAL ISSUE — MCP SDK stdio_client deadlocks"
(2026-05-01).

The MCP Python SDK (`mcp` package, versions 1.2.0 AND 1.27.0) deadlocks
after ~3 sequential `call_tool()` invocations on a persistent stdio session.
Root cause: `anyio.create_memory_object_stream(0)` (zero-buffer) creates a
rendezvous requirement that deadlocks under sustained sequential
call/response patterns.

**This is why `mcp_client.py` was created** — as a subprocess-per-call
workaround.  Each tool call spawned `python <script> <args>` directly,
captured stdout, returned.  ~100ms overhead per call, but zero deadlocks.

**Tools v2 solution:** Use Streamable HTTP transport for the pipeline (not
stdio).  Stdio is kept for IDE clients (interactive use doesn't trigger the
deadlock).

### 2.2. The Sandbox Architecture

**Open Brain reference:** "Lavender Agentic Game Engine System —
Architecture Overview" (2026-05-02).

The sandbox design:
1. Pipeline runner runs on HOST (needs network for LLM API calls via
   OpenRouter).
2. Container runs with `--network none` (security: no exfiltration).
3. Engine mounted at `/lavender` (read-only).
4. Game project mounted at `/project` (read-write).
5. API keys NEVER enter the container.  Secrets stay at
   `~/.config/lavender/secrets.env` on host.

**Why `lav_ai_app.py` didn't work in the container:** The original plan
was to run the MCP server inside the container and have the pipeline
connect via stdio.  This failed because:
- The stdio deadlock (S2.1 above) made persistent sessions unviable.
- The `lav_ai_app.py` server used `Path.cwd()` for project root, which
  was unreliable when CWD was `/project` inside the container.
- The subprocess wrappers spawned by `lav_ai_app.py` needed `$LAVENDER_DIR`
  and `$PYTHONPATH` set correctly inside the container.

The workaround (`mcp_client.py`) bypassed MCP entirely: the pipeline on
the host directly `subprocess.run()`'d tool scripts (or `podman exec`'d
them into the container).  This created the N=2 maintenance fork that
led to `lav_impl/tools.py`.

**Tools v2 solution:** The MCP server runs inside the container, listens
on HTTP.  Pipeline connects from host via HTTP.  Tools execute in-process
(no subprocess wrappers).  Single source of truth.

### 2.3. The Half-Finished Migration

**Open Brain reference:** "Breaking change planned for Lavender tooling
architecture" (2026-05-17) and "Completed Lavender tooling architecture
refactor" (2026-05-17).

The refactor created `lav_impl/` as a "protocol-agnostic" tool library
and `mcp_server.py` as a new server wrapping it.  But:
- `lav_ai_app.py` was never deleted (blocked by `lav_query_tools.py`
  importing its FastMCP `mcp` object).
- `lav_impl/tools.py` turned out to be ANOTHER subprocess wrapper layer,
  not in-process logic.
- The circular dependency (`lav_impl → lav_ai.clang_server`) was introduced.
- Both servers remained operational, signatures diverged.

**Tools v2 solution:** No migration.  Clean-room implementation with the
correct architecture from day one.

### 2.4. The Container Runtime

**Open Brain reference:** "Lavender Pipeline Runner — Critical Design
Decisions and Bugs" (2026-05-02).

Host is Void Linux with Podman 5.7.1.  The Docker CLI fails with
"unable to upgrade to tcp, received 500" because the Docker API server is
actually Podman.  Container runtime auto-detection (podman-first) is
mandatory.

### 2.5. Tool Ordering Dependencies

**Open Brain reference:** "Lavender Pipeline Runner — Critical Design
Decisions and Bugs" (2026-05-02).

Known ordering constraints:
- ALL `gen_tile_layer_name` calls must complete before ANY `gen_tile` call
  (because `gen_tile_layer_name` rewrites `tile.h` completely).
- Scene-first pattern: `gen_window` → `gen_scene` → `mod_scene` → `gen_ui`.
- `build_compile_commands` must run before any `scan_*` tool (clangd needs
  `compile_commands.json`).

These are formalized in `ToolDef.ordering_constraints` (TOOL_REGISTRY.md S2).

---

## 3. The Specification System

Ten spec files at `tools2/docs/specs/`:

### 3.1. OVERVIEW.md — Immutable Anchor
- 7 goals: single source of truth, mandatory traceability, undo/redo,
  Pydantic enforcement, sandbox-first, AI-native maintainability, CI
  enforcement.
- 4 constraints: stdio deadlock, container networking, container runtime,
  correct codegen logic from v1.
- Python >= 3.10.

### 3.2. ARCHITECTURE.md — Three Layers
```
Layer 3: MCP Transport     (mcp_server.py — one server, dynamic registration)
Layer 2: Tool Registry     (registry.py + tools/*.py — ToolDef objects)
Layer 1: Core Infra        (core/ — codegen, atomic, traceability, project, clangd, scan_base)
```
- Strict downward dependency.  No upward imports.  CI-enforced.
- ONE `project_dir` parameter name.  ONE project root resolver.
  ONE engine dir resolver.

### 3.3. TOOL_REGISTRY.md — Single Source of Truth
- `ToolDef` dataclass: name, category, input_model, output_model,
  implementation, description, file_touch_manifest, ordering_constraints,
  idempotent, mutating.
- `ToolFunction = Callable[[BaseModel, ToolContext], BaseModel]`.
- `ToolContext`: project_dir, engine_dir, transaction, clangd, logger.
- MCP registration, CLI, docs, test scaffolding all DERIVED from registry.
- Adding a tool is a **1-file operation** (CI catches violations).

### 3.4. TRACEABILITY.md — Mandatory Transactions
- `Transaction` object created by dispatch layer before tool call.
- `FileRecord` with path, operation, hashes, diff, backup_path.
- JSONL append-only storage (eliminates read-modify-write races).
- Undo via backup restore.  Redo via re-execution.
- Pipeline context (run_id, pipeline_id, node_id) in every record.

### 3.5. CODEGEN.md — One Parser
- `core/codegen.py`: `find_gen_block`, `append_to_gen_block`,
  `replace_gen_block`, `clear_gen_block`, `list_gen_blocks`.
- `GenBlock` dataclass with name, start_line, end_line, content, indent.
- Missing markers are ERRORS, not silent skips.
- Template files in `templates/` with `{{PLACEHOLDER}}` syntax.

### 3.6. SCAN_FRAMEWORK.md — Unified Schema
- `ScanBase` ABC: subclasses implement `scan()`, base handles boilerplate.
- `ScanOutput(BaseModel)`: tool, timestamp, project_root, summary, results.
- `ScanCheck(BaseModel)`: check_id, status, message, source, expected, actual.
- ALL 7 scan tools (verification + inventory) use the same schema.
- Clangd session at `core/clangd.py` (not in MCP server layer).

### 3.7. MCP_SERVER.md — One Server
- Single FastMCP server.  Dynamic registration from registry.
- Stdio transport for IDE, Streamable HTTP for pipeline.
- DirectBackend (in-process, host) and SandboxBackend (container).
- Tools are in-process function calls.  No subprocess wrappers.
- CWD guard: rejects engine directory as project_dir.

### 3.8. CI.md — Automated Enforcement
- Registry consistency (no duplicates, no missing descriptions).
- Traceability coverage (mutating tools must record, no bare `open(w)`).
- Test coverage (every tool tested, max 500 lines per test file).
- Import layer enforcement (no upward imports).
- No duplicate function definitions.
- Naming convention enforcement (no `project_root` / `game_dir`).
- **`gen_tool.py` is NOT needed** — 1-file tool addition + CI is sufficient.

### 3.9. MIGRATION.md — Hard Cut, 6 Phases
- Phase 0: Core infrastructure (codegen, atomic, traceability, project,
  clangd, scan_base, registry, mcp_server).
- Phase 1: Standalone generators (sprite, png, tile, entity, etc.).
- Phase 2: Compound generators (scene, ui, lav_project).
- Phase 3: Modifiers (mod_scene, mod_entity, mod_png).
- Phase 4: Scanners (all 7).
- Phase 5: Build + query + clangd MCP tools.
- Phase 6: Pipeline integration + engine filesystem tools.
- Per-tool checklist: Pydantic models, core/codegen for GEN ops,
  core/atomic for writes, transaction recording, real integration tests.

---

## 4. Key Design Decisions — Rationale Summary

| Decision | Rationale |
|----------|-----------|
| Hard cut, not incremental migration | v1 architecture is unfixable: 3 layers of subprocess wrappers, circular deps, dual servers. Incremental migration would require maintaining both systems simultaneously, which is what caused the current mess. |
| HTTP transport for pipeline | MCP SDK stdio deadlocks after ~3 calls. HTTP has no such limitation. Verified by Open Brain (2026-05-01). |
| In-process tool execution | v1's subprocess wrappers added ~100ms per call, lost type information, and created a separate error format. In-process calls give native Python exceptions, Pydantic validation, and zero serialization overhead. |
| Pydantic v2 for all I/O | Eliminates ad-hoc dict construction, catches type errors at the boundary, generates JSON Schema for MCP automatically, enables structured error reporting. |
| JSONL append-only traceability | v1's JSON manifests used read-modify-write without locking (documented TODO). JSONL append is safe under concurrent access without file locking. |
| `core/codegen.py` as single GEN parser | v1 had 3 divergent parsers. Any change to marker conventions required shotgun surgery across 6+ files. One parser means one place to fix. |
| `ScanBase` with unified schema | v1 had 2 output schemas and copy-pasted boilerplate across 5 files. Unified schema means AI consumers write ONE parser. |
| `gen_tool.py` not needed | Adding a tool is a 1-file operation (create file with `TOOL_DEFS`). CI catches missing tests, missing descriptions, missing traceability. The meta-tool adds complexity without proportional value at current team size. |
| Mandatory traceability at dispatch | v1 made it opt-in per script. Result: most scripts skipped it. Mandatory at the server/dispatch layer means no tool can bypass it. |
| `write_atomic` for all file writes | v1 had zero atomic writes. A crash during `open(path, 'w')` truncates the file to zero bytes. `temp + os.replace` guarantees atomicity. |

---

## 5. What the Next AI Agent Should Do

### 5.1. Immediate Next Steps

1. **Read all 10 spec files** in `tools2/docs/specs/` to internalize the
   architecture.
2. **Implement Phase 0** (MIGRATION.md S2, Phase 0):
   - `core/codegen.py` — port GEN-marker parsing from v1's three
     implementations into one.  Test with real Lavender C files.
   - `core/atomic.py` — `write_atomic()` and `lock_file()`.
   - `core/traceability.py` — `Transaction`, `FileRecord`, JSONL writer.
   - `core/project.py` — project/engine root resolution.
   - `registry.py` — `ToolDef` protocol and auto-discovery.
   - `mcp_server.py` — single FastMCP server with dynamic registration.
3. **Write CI structural checks** (CI.md S2) alongside Phase 0.
4. **Port one simple tool** (e.g., `gen_sprite_kind`) as proof-of-concept
   to validate the full ToolDef → MCP → execution → traceability chain.

### 5.2. Reference Material

- **v1 source code**: `tools/lavender_tools/` — the C codegen logic is
  correct; extract it, do not rewrite it.
- **Open Brain**: Search for "Lavender Pipeline", "MCP SDK deadlock",
  "Lavender tooling architecture", "gen_* tools common patterns".
- **Engine specs**: `docs/specs/core/` — 160+ spec files documenting the
  C engine that the tools generate code for.
- **Pipeline specs**: Search Open Brain for "PIPELINE SPEC STRUCTURE"
  (2026-05-01) for the full pipeline JSON schema.

### 5.3. What NOT to Do

- Do NOT create `lav_ai_app.py` equivalent wrappers.  Tools are in-process.
- Do NOT use `subprocess.run` for tool execution (except `make` for builds).
- Do NOT use `project_root`, `game_dir`, or `project-dir` as parameter
  names.  It is `project_dir`.
- Do NOT create per-tool argparse CLI parsers.  The CLI is derived from
  Pydantic models by the generic CLI runner.
- Do NOT put clangd session management in the MCP server layer.  It lives
  in `core/clangd.py`.
- Do NOT write test files > 500 lines.  Split by tool category.
- Do NOT skip traceability recording.  If a tool mutates files, the
  transaction must have records.

---

## 6. Open Brain References

Key Open Brain entries for continued context retrieval:

| Query | What You'll Find |
|-------|-----------------|
| `"MCP SDK stdio_client deadlocks"` | The deadlock root cause, versions affected, workaround |
| `"Lavender Agentic Game Engine System"` | Sandbox architecture, split-trust model |
| `"Lavender Pipeline Runner"` | Pipeline structure, execution model, subpipeline design |
| `"Breaking change planned for Lavender tooling"` | The half-finished migration that led to tools v2 |
| `"Completed Lavender tooling architecture refactor"` | What was done in the May 2026 refactor (and what failed) |
| `"Lavender Pipeline Runner — Critical Design Decisions"` | Tool ordering constraints, state reducers, container runtime |
| `"Lavender spec writing style"` | Spec conventions: numeric sections, traceability, immutable anchors |
| `"gen_* tools common patterns"` | v1 tool conventions: argparse, GEN markers, name validation |
| `"Lavender Tools v2 — Specification System Created"` | This checkpoint's companion summary |
| `"Lavender tools/legacy/ folder policy"` | Which old scripts are obsolete and why |

---

## 7. File Inventory at Checkpoint Time

```
tools2/
  docs/
    specs/
      OVERVIEW.md          — Immutable anchor.  Goals, constraints, terminology.
      CHANGES.md           — Immutable anchor.  Change log.
      ARCHITECTURE.md      — 3-layer architecture, sandbox model, call flow.
      TOOL_REGISTRY.md     — ToolDef protocol, Pydantic I/O, single source of truth.
      TRACEABILITY.md      — Transaction log, atomic writes, undo/redo.
      CODEGEN.md           — GEN-marker protocol, shared parser, C templates.
      SCAN_FRAMEWORK.md    — ScanBase, unified output schema, clangd integration.
      MCP_SERVER.md        — Single server, dual transport, dual backend.
      CI.md                — Structural enforcement, gen_tool.py analysis.
      MIGRATION.md         — Hard cut, 6-phase port order, per-tool checklist.
      CHECKPOINT.md        — This file.

tools/ (v1, to be archived after v2 is complete)
  lavender_tools/          — 22,800 lines.  Source of C codegen logic to port.
  legacy/                  — Obsolete scripts.  Do not use.
  editors/                 — Map/UI editors.  Not in scope for v2.
  gen_ui_elements/         — UI element definitions.  Evaluate for porting.
  pyproject.toml           — v1 packaging.  v2 will have its own.
  requirements.txt         — v1 deps.  Contains known `pyglet` typo.
```

No code has been written for tools v2 yet.  This checkpoint marks the
completion of the specification phase and the beginning of the
implementation phase.
