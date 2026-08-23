# Lavender Tools v2 — MCP Server

> **Spec reference:** OVERVIEW.md S1.5, S3.1, S3.2  
> **Status:** DRAFT

## 1. Single Server Principle

Tools v1 had **three separate FastMCP server instances**:
- `lav_ai_app.py` (the original, 2631 lines)
- `mcp_server.py` (the new pluggable-backend server, 313 lines)
- `lav_ai_fs_readonly.py` (read-only engine filesystem, 293 lines)

Tools v2 has **one server**: `mcp_server.py`.  This server handles all
tool execution.  The read-only filesystem tools are registered as regular
tools in the same registry.

## 2. Dynamic Registration

The server does NOT hand-code tool wrappers.  It iterates the
`ToolRegistry.TOOLS` dict and generates MCP tool registrations
dynamically:

```python
for name, tool_def in registry.TOOLS.items():
    @mcp.tool(name=name, description=tool_def.description)
    async def handler(**kwargs):
        input_obj = tool_def.input_model(**kwargs)
        ctx = _build_context(tool_def)
        output = tool_def.implementation(input_obj, ctx)
        return output.model_dump_json()
```

Each tool's MCP parameter schema is derived from
`tool_def.input_model.model_json_schema()`.

Each tool's MCP return value is the JSON serialization of
`tool_def.output_model`.

## 3. Transport Support

### 3.1. Stdio Transport (IDE)

For interactive IDE clients (Claude Code, OpenCode), the server runs on
the host in stdio mode:

```bash
python -m lavender_tools2.mcp_server --transport stdio
```

This is safe because IDE use is interactive — the MCP SDK deadlock only
affects sustained sequential programmatic calling (OVERVIEW.md S3.1).

### 3.2. Streamable HTTP Transport (Pipeline)

For the LangGraph pipeline runner, the server runs inside a container and
listens on HTTP:

```bash
python -m lavender_tools2.mcp_server --transport http --port 8080
```

The pipeline connects via HTTP from the host.  This avoids the stdio
deadlock entirely.

### 3.3. Transport Selection

The server accepts a `--transport` flag:
- `stdio` (default) — for IDE clients
- `http` — for pipeline / programmatic use

## 4. Execution Backends

### 4.1. DirectBackend

Calls tool implementation functions in-process.  Used when the server is
running on the host (IDE mode).

```python
class DirectBackend:
    def __init__(self, project_dir: Path, engine_dir: Path): ...
    def execute(self, tool_def: ToolDef, input: BaseModel) -> BaseModel: ...
```

### 4.2. SandboxBackend

The server itself runs inside the container.  There is no "redirect" layer.
The container is started by the pipeline runner (or manually), and the
server process is the entrypoint.

Container mounts:
- `/lavender` — engine directory, read-only
- `/project` — game project directory, read-write

The server detects containerized execution by checking if `/lavender` and
`/project` exist.

### 4.3. No Subprocess Wrappers

Tools v1 had tools that were thin subprocess wrappers around CLI scripts.
The MCP server called `subprocess.run(["python", "gen_entity.py", ...])`.

Tools v2 tools are **in-process function calls**.  The implementation
function runs directly in the server process.  No subprocess overhead.
No argument serialization.  No stdout capture.

The only exceptions are `build` tools which invoke `make` (an external
process by necessity) and `clangd` which runs as a managed subprocess.

## 5. CWD Guard

### 5.1. Engine Directory Rejection

The server refuses to operate when `project_dir` resolves to the engine
directory itself.  This prevents accidental modification of engine source
files.

```python
def _validate_project_dir(project_dir: Path, engine_dir: Path) -> None:
    """MCP_SERVER.md S5.1"""
    if project_dir.resolve() == engine_dir.resolve():
        raise ToolError(
            "CWD is the Lavender engine directory. "
            "Tools must run from a game project directory.",
            recoverable=False,
        )
```

### 5.2. Lavender Project Validation

The server validates that `project_dir` contains `.lavender/lavender.json`.
Tools that legitimately operate without a project context (e.g.,
`gen_lav_project` which *creates* the project) are marked as
`requires_project=False` in their `ToolDef`.
