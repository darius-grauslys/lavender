# Lavender Tools v2 — Architecture

> **Spec reference:** OVERVIEW.md S4  
> **Status:** DRAFT

## 1. Layered Architecture

The system has exactly three layers.  Dependencies flow strictly downward.
No layer may import from a layer above it.

```
Layer 3: MCP Transport          (mcp_server.py)
          │
Layer 2: Tool Registry          (registry.py, tool definitions)
          │
Layer 1: Core Infrastructure    (codegen/, scan/, traceability/, clangd/)
```

### 1.1. Layer 1 — Core Infrastructure

Pure Python libraries with zero MCP awareness.  No FastMCP imports.
No transport concepts.  No `project_dir` parameter threading — Layer 1
operates on explicit `Path` objects.

Modules:

- `core/codegen.py` — GEN-marker parsing, block insertion/replacement/
  deletion.  The single implementation.  (CODEGEN.md S2)
- `core/atomic.py` — Atomic file writes (`write_atomic`), file locking
  (`lock_file`).  (TRACEABILITY.md S3)
- `core/traceability.py` — Transaction log.  Records file creates, modifies,
  deletes.  Mandatory.  (TRACEABILITY.md S1)
- `core/project.py` — Project root detection, `.lavender/lavender.json`
  reading, engine dir resolution.  The single implementation.
- `core/clangd.py` — ClangdSession lifecycle, LSP queries.  Moved out of
  any server-specific package.  (SCAN_FRAMEWORK.md S3)
- `core/scan_base.py` — Base class/protocol for scan tools.
  (SCAN_FRAMEWORK.md S1)

### 1.2. Layer 2 — Tool Registry

The **single source of truth** for all tool definitions.  Each tool is a
`ToolDef` object that binds together:

- A name (the MCP tool name)
- A Pydantic `Input` model
- A Pydantic `Output` model
- An implementation function `(Input, ToolContext) -> Output`
- Metadata (category, file-touch manifest, ordering constraints)

See TOOL_REGISTRY.md for the full `ToolDef` protocol.

Tools are grouped by category in submodules:

- `tools/gen_entity.py`, `tools/gen_scene.py`, etc.
- `tools/mod_scene.py`, `tools/mod_entity.py`, etc.
- `tools/scan_entity.py`, `tools/scan_scene.py`, etc.
- `tools/build.py`, `tools/query.py`, `tools/clangd.py`

Each file exports a list of `ToolDef` objects.  The registry auto-discovers
them.

### 1.3. Layer 3 — MCP Transport

A single FastMCP server (`mcp_server.py`) that:

1. Imports the tool registry.
2. For each `ToolDef`, registers an `@mcp.tool()` wrapper that:
   a. Deserializes MCP JSON params into the Pydantic `Input` model.
   b. Constructs a `ToolContext` (project_dir, engine_dir, transaction).
   c. Calls the implementation function.
   d. Serializes the Pydantic `Output` model to JSON.
   e. Commits or rolls back the transaction.
3. Supports two backends:
   a. **DirectBackend** — in-process execution (for IDE MCP clients).
   b. **SandboxBackend** — containerized execution (for pipeline).

No tool logic lives in Layer 3.  Layer 3 is pure transport + dispatch.

## 2. Sandbox Model

### 2.1. Split-Trust Architecture

```
HOST (has network)                 CONTAINER (--network none)
┌────────────────────┐            ┌────────────────────────┐
│ Pipeline Runner    │   HTTP     │ MCP Server (tools v2)  │
│ (LangGraph)        │───────────▶│ FastMCP Streamable HTTP│
│                    │            │                        │
│ LLM API calls      │            │ /lavender (read-only)  │
│ (OpenRouter, etc.) │            │ /project  (read-write) │
│                    │            │ --network none         │
│ API keys stay here │            │ No secrets             │
└────────────────────┘            └────────────────────────┘
```

### 2.2. Transport Decision

The pipeline connects to the MCP server via **Streamable HTTP**, not stdio.

**Rationale (OVERVIEW.md S3.1):** The MCP Python SDK's `stdio_client`
deadlocks after ~3 sequential `call_tool` invocations due to zero-buffer
`anyio.create_memory_object_stream(0)`.  HTTP transport avoids this entirely.

For IDE clients (Claude Code, OpenCode), the server also supports **stdio**
transport.  The deadlock only affects sustained sequential programmatic
calling patterns; interactive IDE use is fine.

### 2.3. Container Lifecycle

Two modes (MCP_SERVER.md S4):

- **Persistent container** — started once, MCP server runs inside,
  pipeline connects via HTTP.  Lower latency.  Default for pipeline.
- **Direct mode** — no container, server runs on host.  For local
  development and IDE clients.

### 2.4. Container Runtime Detection

Auto-detect in order: `podman` then `docker`.  (OVERVIEW.md S3.3)
Podman is required on Void Linux where the Docker CLI fails.

## 3. Call Flow

### 3.1. Pipeline → Container (Sandbox Mode)

```
Pipeline (HOST)
  │
  ├─ HTTP POST to container:8080/mcp
  │
  ▼
mcp_server.py (CONTAINER)
  │
  ├─ Deserialize MCP JSON → Pydantic Input
  ├─ Create ToolContext (transaction, project_dir=/project)
  ├─ Call tool implementation function
  │    ├─ core/codegen.py (GEN-marker ops)
  │    ├─ core/traceability.py (record mutations)
  │    └─ core/atomic.py (temp file + os.replace)
  ├─ Commit transaction (flush traceability log)
  ├─ Serialize Pydantic Output → JSON
  │
  └─ HTTP response
```

### 3.2. IDE → Direct (No Container)

```
IDE MCP Client
  │
  ├─ stdio transport
  │
  ▼
mcp_server.py (HOST, same process)
  │
  ├─ Same dispatch as 3.1 but project_dir=CWD
  └─ ...
```

## 4. Project Root Resolution

There is exactly ONE function that resolves the project root:
`core.project.resolve_project_root(hint: Path | None) -> Path`.

Rules:
1. If `hint` is provided, use it.
2. Else use `Path.cwd()`.
3. Validate that `.lavender/lavender.json` exists at the resolved path.
4. Raise `ProjectNotFoundError` if not.

There is exactly ONE parameter name: `project_dir`.  Not `project_root`,
not `game_dir`, not `project-dir`.

## 5. Engine Directory Resolution

There is exactly ONE function: `core.project.resolve_engine_dir() -> Path`.

Rules:
1. Check `$LAVENDER_DIR` environment variable.
2. If inside a container, use `/lavender`.
3. Else walk up from the tool package to find the engine root.
4. Raise `EngineNotFoundError` if not found.
