# Lavender Tools Specification

## 1.0 Architecture

The Lavender tooling system is a Python package (`lavender_tools`) that
provides code generation, asset modification, codebase analysis, and build
automation for the Lavender C game engine. All tools are exposed to AI agents
via an MCP (Model Context Protocol) server.

### 1.1 MCP Entry Point

`tools/lavender_tools/lav_ai/lav_ai_app.py` is a `FastMCP("lavender-tools")`
server. Each MCP tool call from an agent triggers `subprocess.run()` of a
Python script **or** an in-process function call. This subprocess boundary is
the **only** process boundary in the system.

### 1.2 Single-Process Constraint

**Critical rule**: All sub-tool invocations within a single MCP tool call
MUST be Python imports, never subprocesses.

Rationale: `tool_history.py` (Section 2.0) uses `inspect.stack()` to trace
which tool called which. Subprocess boundaries sever the call stack, breaking
callee-chain introspection and losing automated filesystem operation tracing.

```
Agent
  |
  v  (MCP JSON-RPC)
lav_ai_app.py
  |
  v  (subprocess.run -- ONLY process boundary)
gen_scene.py
  |
  v  (Python import -- NOT subprocess)
  gen_entity.py   (if gen_scene needs entity registration)
  clang_tools.py  (if gen_scene needs symbol verification)
  tool_history.py (records file operations with full callee-chain)
```

Tools that compose other tools (scan_\* tools, future mod_scene.py) MUST
import their dependencies as Python modules.

### 1.3 Module Layout

```
tools/
  lavender_tools/           # Python package (pip-installable)
    __init__.py
    gen_*.py                # Code generators (Layer 0 - deterministic)
    mod_png.py              # Asset modifier
    clang_tools.py          # Layer 1 - pure LSP query functions
    scan_*.py               # Layer 2 - domain analysis (import clang_tools)
    tool_history.py         # File operation history tracking
    build*.py               # Build system wrappers
    lav_ai/                 # MCP server subpackage
      lav_ai_app.py         # FastMCP entry point
      clang_server.py       # clangd subprocess lifecycle (pygls)
      lav_ai_fs_readonly.py # Read-only engine filesystem server
      tests/                # pytest suite
    lav_query_*.py          # MCP tool/agent introspection
  pyproject.toml            # Package metadata
  requirements.txt          # pip dependencies
  legacy/                   # Obsolete scripts (NOT used by agents)
```

### 1.4 Configuration

All project configuration lives under `.lavender/`:

| File | Purpose |
|------|---------|
| `.lavender/lavender.json` | Authoritative project config: platforms, tool-manifest flags |
| `.lavender/clangd.json` | clangd subprocess config: path, timeouts, startup mode |
| `.lavender/tool-manifest/` | Per-tool file operation history (tool_history output) |
| `.lavender/scans/` | Scan tool analysis output (JSON) |

### 1.5 Tool Categories

| Prefix | Category | Process Model | Example |
|--------|----------|---------------|---------|
| `gen_*` | Generator | Subprocess from MCP | `gen_entity.py` |
| `mod_*` | Modifier | Subprocess from MCP | `mod_png.py` |
| `scan_*` | Analyzer | In-process (import) | `scan_ui.py` |
| `build*` | Build | Subprocess from MCP | `build.py` |
| `clangd_*` | LSP query | In-process (import) | `clang_tools.py` |
| `query_*` | Introspection | Subprocess from MCP | `lav_query_tools.py` |

---

## 2.0 Tool History (tool_history.py)

Tracks which tools touched which files, with full callee-chain attribution.
Currently named `tool_manifest.py` (rename to `tool_history.py` pending).

### 2.1 API

```python
record_create(file_path: str) -> str | None   # Returns UUID
record_modify(file_path: str) -> str | None   # Returns UUID
record_read(file_path: str) -> str | None      # Returns UUID (disabled by default)
```

### 2.2 Manifest Schema

Per-tool JSON files in `.lavender/tool-manifest/<tool_name>.json`:

```json
[{
  "timestamp": "2026-04-30",
  "block": [
    {
      "uuid": "...",
      "type": "file",
      "timestamp": "2026-04-30T12:00:00Z",
      "callee-chain": ["tools/lavender_tools/gen_entity.py"],
      "record": {"file": "/abs/path/to/entity_kind.h"}
    },
    {
      "uuid": "...",
      "type": "sub-tool",
      "timestamp": "2026-04-30T12:00:01Z",
      "callee-chain": ["tools/lavender_tools/gen_scene.py"],
      "record": {"sub-tool": "gen_entity", "sub-tool-uuid": "..."}
    }
  ]
}]
```

### 2.3 Callee-Chain Introspection

Uses `inspect.stack()` to walk the call stack. Filters frames where the
executing file is under `$LAVENDER_DIR/tools/`. Reverses so the originator
tool is first. **This only works within a single process** (Section 1.2).

### 2.4 Configuration

In `.lavender/lavender.json`:

```json
{
  "tool-manifest": {
    "create": true,
    "modify": true,
    "read": false
  }
}
```

When `read` is `true`, scan_\* tools calling `record_read()` will log every
file they analyze, creating a full trace of analysis inputs.

### 2.5 Future: Read-Back API

Planned additions (not yet implemented):
- `query_history(tool_name)` -- list all records for a tool
- `query_files_touched_by(tool_name)` -- list file paths
- `query_tools_that_touched(file_path)` -- list tool names

---

## 3.0 MCP Tool Convention

### 3.1 Docstring Pattern

Every `@mcp.tool()` function follows this structure:

1. One-line summary
2. `**PREFER this tool** over [manual alternative]` directive
3. Risk explanation (why manual editing is dangerous)
4. Memory tooling hint: "For Lavender-specific context on [domain],
   consult available memory tooling."
5. `Args:` section with parameter descriptions
6. `Returns:` section with output format

### 3.2 Error Convention

- Subprocess tools: `"ERROR (exit <code>):\n<output>"` on non-zero exit
- In-process tools: `"ERROR: <message>"` on exception
- Missing config: `"ERROR: clangd not configured. Create .lavender/clangd.json"`

---

## 4.0 Scan Tools (Layer 2)

Scan tools are **deterministic analysis scripts** that compose Layer 1 clangd
queries with domain knowledge. They verify that code generation outputs are
correctly wired and that referenced symbols actually exist.

### 4.1 Common Pattern

Every scan tool follows this structure:

1. **Parse enum header** -- extract registered entries (`*_Kind__*`)
2. **Parse registrar** -- extract wired entries from `*_registrar.c`
3. **Verify via clangd** -- use `clang_tools.py` to confirm handlers exist
4. **Cross-reference** -- check related systems for consistency
5. **Output JSON** -- write structured results to `.lavender/scans/<tool>.json`

All scan tools:
- Import `clang_tools` functions directly (Section 1.2)
- Call `clang_server.get_session()` to obtain the shared clangd session
- Optionally call `tool_history.record_read()` if read tracking is enabled
- Are exposed as MCP tools via in-process function calls (not subprocess)

### 4.2 scan_ui.py

**Purpose**: Verify UI XML handler references resolve to real C symbols.

**Use cases**:
- `4.2.1` Handler verification: For every `c_signatures` function in UI XML,
  use `clangd_definition` to verify it exists. Report missing handlers with
  the XML file and element that references them.
- `4.2.2` Handler location tracing: For verified handlers, report
  `file:line:column` of their definition.
- `4.2.3` UI window registration check: Cross-ref `ui_window_registrar.c`
  GEN-BEGIN/END entries against XML files. Detect registered-but-unused
  windows and XML-without-registrar entries.
- `4.2.4` Offset collision detection: Check `offset_of__ui_index` values
  across XMLs that may be loaded simultaneously. Flag collisions.
- `4.2.5` c_signature completeness: For each XML element type used, verify
  a matching `ui_func_signature` entry exists in the XML config section.

**Inputs**: `assets/ui/xml/**/*.xml`, `ui_window_registrar.c`,
`core/include/defines.h` (m_UI_\* typedefs)

**Output**: `.lavender/scans/scan_ui.json`

### 4.3 scan_entity.py

**Purpose**: Verify entity lifecycle handlers exist and are correctly wired.

**Use cases**:
- `4.3.1` Lifecycle handler verification: For each `Entity_Kind__*`, verify
  expected handlers exist via clangd: `m_entity_handler__update_<name>`,
  `m_entity_handler__dispose_<name>`, etc. (gen_entity naming convention).
- `4.3.2` Sprite mapping: Cross-ref `entity_kind.h` against `sprite_kind.h`.
  Convention: `Entity_Kind__X` maps to `Sprite_Kind__X`.
- `4.3.3` Registrar completeness: Verify `register_entity_<name>` call
  exists in `entity_registrar.c` for every enum entry.
- `4.3.4` Handler signature tracing: Use `clangd_hover` to verify handler
  functions match expected typedef signatures.

**Inputs**: `entity_kind.h`, `entity_registrar.c`, `sprite_kind.h`,
`entity__*.c`

**Output**: `.lavender/scans/scan_entity.json`

### 4.4 scan_scene.py

**Purpose**: Verify scene handlers exist and trace scene-to-UI relationships.

**Use cases**:
- `4.4.1` Handler tracing: For each `Scene_Kind__*`, use
  `clangd_workspace_symbol` to find `m_load_scene_as__<name>`,
  `m_enter_scene_as__<name>`, `m_unload_scene_as__<name>`. Verify all three.
- `4.4.2` Registrar completeness: Verify `register_scene__<name>` calls match
  `scene_kind.h` entries.
- `4.4.3` UI window cross-ref: Parse scene source files for
  `open_ui_window`/`close_ui_window` calls. Verify referenced
  `UI_Window_Kind__*` values exist.
- `4.4.4` Scene transition tracing: Find all `Scene_Kind__*` references in
  scene source files. Map which scenes can transition to which.

**Inputs**: `scene_kind.h`, `scene_registrar.c`, `scene__*.c`,
`ui_window_kind.h`

**Output**: `.lavender/scans/scan_scene.json`

### 4.5 scan_textures.py

**Purpose**: Detect orphaned and missing texture registrations.

**Use cases**:
- `4.5.1` Orphan detection: For each registered alias in
  `aliased_texture_registrar.c`, use `clangd_references` on the
  `name_of__texture__*` symbol. Flag registered-but-never-used textures.
- `4.5.2` Missing texture detection: Search for `get_texture_by__alias()`
  calls. Verify each referenced alias is registered.
- `4.5.3` Asset file verification: For each registered texture, verify the
  PNG at the registered path exists on disk.

**Inputs**: `aliased_texture_registrar.c/.h`, `assets/**/*.png`

**Output**: `.lavender/scans/scan_textures.json`

### 4.6 scan_game_actions.py

**Purpose**: Verify game action handlers and registration modes.

**Use cases**:
- `4.6.1` Handler verification: For each game action type, verify the
  `m_process__game_action` handler exists via clangd.
- `4.6.2` Registration mode audit: Verify each game action is registered in
  the correct mode (offline/client/server) based on naming convention.
- `4.6.3` Entity reference tracing: Game actions referencing `Entity_Kind__*`
  values -- verify those entities are registered.

**Inputs**: `game_action_registrar.c`, `game_action_kind.h`,
`game_action__*.c`

**Output**: `.lavender/scans/scan_game_actions.json`

### 4.7 Output Schema

All scan tools output JSON with a common envelope:

```json
{
  "tool": "scan_ui",
  "timestamp": "2026-04-30T12:00:00Z",
  "project_root": "/abs/path",
  "summary": {
    "total_checked": 15,
    "passed": 12,
    "warnings": 2,
    "errors": 1
  },
  "results": [
    {
      "check": "4.2.1",
      "status": "error",
      "message": "Handler 'm_UI_Clicked__settings_save' not found",
      "source": {"file": "assets/ui/xml/sdl/game/settings.xml", "element": "button"},
      "expected": "m_UI_Clicked__settings_save",
      "clangd_query": "workspace_symbol"
    }
  ]
}
```

The `check` field references the spec section number, allowing agents and
humans to look up the exact verification rule that produced each result.

### 4.8 Tool History Integration

When `.lavender/lavender.json` has `"read": true` in the `tool-manifest`
section, scan tools call `tool_history.record_read()` for every file they
analyze. This creates a traceable record of analysis inputs. The scan output
file itself is tracked via `tool_history.record_create()` (first run) or
`tool_history.record_modify()` (subsequent runs).
