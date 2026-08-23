# Lavender Tools v2 — Migration Plan

> **Spec reference:** OVERVIEW.md S0  
> **Status:** DRAFT

## 1. Strategy

### 1.1. Hard Cut

This is NOT an incremental migration.  Tools v2 is a parallel
implementation in `tools2/`.  When tools v2 is feature-complete and
passing all tests, the switch is atomic:

1. `tools/lavender_tools/` → `tools/lavender_tools_v1/` (archived)
2. `tools2/` → `tools/lavender_tools/` (promoted)
3. `opencode.json` MCP server paths updated.
4. Pipeline `mcp_client.py` / `mcp_cli.py` pointed at new server.
5. Container Dockerfile updated.

### 1.2. Coexistence Period

During development, both `tools/` and `tools2/` exist.  The existing
`tools/` remains operational for active game projects.  `tools2/` is
developed and tested independently.

### 1.3. Logic Extraction, Not Rewrite

The C code generation logic in tools v1 is correct.  The migration
extracts this logic into tools v2's architecture:

- **Port**: GEN-marker insertion logic, C template generation,
  tile layer layout derivation, sprite animation registration,
  game action type hierarchy, UI XML → C code generation,
  PNG manipulation, clangd LSP integration.
- **Replace**: Subprocess dispatch, argparse CLI, tool_history,
  MCP server wrappers, scan tool boilerplate, error handling.

## 2. Port Order

Tools are ported in dependency order.  Layer 1 (core infrastructure)
first, then tools that have no inter-tool dependencies, then tools
that depend on others.

### Phase 0: Core Infrastructure
1. `core/codegen.py` — GEN-marker parsing (shared by all gen/mod/scan tools)
2. `core/atomic.py` — Atomic writes, file locking
3. `core/traceability.py` — Transaction log
4. `core/project.py` — Project/engine root resolution
5. `core/clangd.py` — ClangdSession + query functions
6. `core/scan_base.py` — ScanBase class + output models
7. `registry.py` — ToolDef protocol + auto-discovery
8. `mcp_server.py` — Single MCP server with dynamic registration

### Phase 1: Standalone Generators (no inter-tool dependencies)
9. `gen_sprite` (sprite_kind, animation, animation_group)
10. `gen_png`
11. `gen_tile` (tile kind)
12. `gen_tile_layer` (tile layer registration + layout derivation)
13. `gen_tile_logic`
14. `gen_ui_tile_kind`
15. `gen_aliased_texture`
16. `gen_entity`
17. `gen_game_action`
18. `gen_chunk_generator`
19. `gen_window`

### Phase 2: Compound Generators (depend on Phase 1 tools or templates)
20. `gen_scene` (uses scene templates, depends on gen_window being done)
21. `gen_ui_create` (scaffolds UI XML)
22. `gen_ui_code` (XML → C, depends on gen_window)
23. `gen_lav_project` (creates entire project structure)

### Phase 3: Modifiers
24. `mod_scene` (injects boilerplate into scene GEN-markers)
25. `mod_entity` (injects __begin handler boilerplate)
26. `mod_png` (set, swap, copy, resize, condense, read)

### Phase 4: Scanners
27. `scan_entity`
28. `scan_scene`
29. `scan_ui`
30. `scan_textures`
31. `scan_game_actions`
32. `scan_assets`
33. `scan_sprite_assets`

### Phase 5: Build + Query + Clangd MCP Tools
34. `build` (full build)
35. `build_compile_commands`
36. `build_spot_check`
37. `clangd_definition`, `clangd_references`, `clangd_symbols`,
    `clangd_workspace_symbol`, `clangd_hover`
38. `query_tools_list`, `query_tools_search`, `query_tools_describe`
39. `query_agents_list`, `query_agents_show`, `query_agents_search_*`
40. `query_tool_history`, `query_files_touched_by`, `query_tools_that_touched`

### Phase 6: Pipeline Integration Tools
41. `analyze_pipeline_run`
42. `analyze_pipeline_node`
43. `validate_pipeline_schema`
44. Read-only engine filesystem tools (ported from `lav_ai_fs_readonly.py`)

## 3. Per-Tool Migration Checklist

For each tool ported from v1 to v2:

- [ ] Create `tools/gen_foo.py` with `TOOL_DEFS` list
- [ ] Define `GenFooInput(BaseModel)` with all fields validated
- [ ] Define `GenFooOutput(BaseModel)` with structured output
- [ ] Implement `gen_foo(input: GenFooInput, ctx: ToolContext) -> GenFooOutput`
- [ ] Use `core/codegen.py` for ALL GEN-marker operations
- [ ] Use `core/atomic.py` for ALL file writes
- [ ] Use `ctx.transaction.record_*()` for ALL file mutations
- [ ] Create `tests/test_gen_foo.py` with:
  - [ ] At least one test that exercises the real implementation in a temp dir
  - [ ] File-system side effect assertions (file exists, content matches)
  - [ ] GEN-block content assertions where applicable
  - [ ] Idempotency test (running twice produces same result)
- [ ] Verify CI passes: `pytest tools2/tests/ci/ -v`
- [ ] Verify registry: tool appears in `query_tools_list` output
- [ ] Verify file_touch_manifest matches actual behavior

## 4. Compatibility Breaks

### 4.1. MCP Tool Name Changes

Tool names are preserved.  `gen_entity` stays `gen_entity`.  MCP clients
(pipeline, IDE) do not need to update tool references.

### 4.2. Parameter Name Changes

`project_root` → `project_dir` (unified).  This is a breaking change for
scan tools in the pipeline that currently pass `project_root`.

### 4.3. Output Format Changes

All tools now return Pydantic JSON instead of raw strings.  This is a
breaking change for:
- Pipeline `mcp_tool_node.py` output parsing
- Any agent prompt that expects `"ERROR (exit N):\n..."` format

The pipeline will need updates to parse structured JSON responses.

### 4.4. Error Format Changes

Errors are now raised as exceptions, not returned as `"ERROR (exit N):\n..."`
strings.  The MCP server serializes them as MCP error responses.

### 4.5. `lav_ai_app.py` Deletion

The old MCP server is deleted.  `lav_query_tools.py` which imports its
`mcp` object is replaced by registry introspection.
