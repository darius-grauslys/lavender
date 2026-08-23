# Lavender Tools v2 — Tool Registry

> **Spec reference:** OVERVIEW.md S1.1, S1.4  
> **Status:** DRAFT

## 1. The Single-Source-of-Truth Problem

In tools v1, every tool was defined in **four places**: the CLI script
(`gen_entity.py`), the old MCP server (`lav_ai_app.py`), the new MCP server
wrapper (`lav_impl/tools.py`), and the `__init__.py` re-export.  Signatures
had already diverged (`project_dir` vs `project_root`).  Adding a tool
required editing 4 files.

Tools v2 defines each tool **exactly once**.

## 2. ToolDef Protocol

Every tool is a `ToolDef` dataclass:

```python
@dataclass(frozen=True)
class ToolDef:
    """Single source of truth for one MCP tool."""

    name: str                              # MCP tool name, e.g. "gen_entity"
    category: ToolCategory                 # gen | mod | scan | build | query | clangd
    input_model: type[BaseModel]           # Pydantic v2 Input model
    output_model: type[BaseModel]          # Pydantic v2 Output model
    implementation: ToolFunction           # (Input, ToolContext) -> Output
    description: str                       # Human/AI-readable description
    file_touch_manifest: list[FileTouch]   # Declarative list of files this tool may touch
    ordering_constraints: list[str]        # Tool names that must run before this one
    idempotent: bool                       # Safe to re-run with same args?
    mutating: bool                         # Does this tool modify files?
```

### 2.1. ToolFunction Signature

```python
ToolFunction = Callable[[BaseModel, ToolContext], BaseModel]
```

The implementation receives a validated Pydantic input and a context object.
It returns a validated Pydantic output.  It never touches MCP transport
directly.

### 2.2. ToolContext

```python
@dataclass
class ToolContext:
    project_dir: Path              # Resolved project directory
    engine_dir: Path               # Resolved engine directory
    transaction: Transaction       # Active traceability transaction
    clangd: ClangdSession | None   # Lazy; only initialized when needed
    logger: logging.Logger         # Per-tool-invocation logger
```

### 2.3. FileTouch Manifest

```python
@dataclass(frozen=True)
class FileTouch:
    """Declarative description of a file this tool may create or modify."""
    pattern: str          # Glob or template, e.g. "include/types/implemented/entity_kind.h"
    operation: Literal["create", "modify", "create_or_modify"]
    gen_marker: str | None  # If modifying a GEN block, which marker name
```

This manifest serves two purposes:
1. **Documentation** — an AI agent can read the manifest to understand side
   effects without reading the implementation.
2. **CI enforcement** — a structural check can verify that the implementation
   only touches files matching its manifest.

## 3. Input/Output Models

### 3.1. Input Models

Every tool's input is a Pydantic `BaseModel` subclass.  Example:

```python
class GenEntityInput(BaseModel):
    """TOOL_REGISTRY.md S3.1"""
    name: Annotated[str, Field(pattern=r'^[A-Za-z_][A-Za-z0-9_]*$')]
    output: str = ""
    gen_dispose: bool = False
    gen_update: bool = False
    gen_enable: bool = False
    gen_disable: bool = False
    gen_serialize: bool = False
    gen_deserialize: bool = False
    f_update: str = ""
    f_dispose: str = ""
    f_enable: str = ""
    f_disable: str = ""
    f_serialize: str = ""
    f_deserialize: str = ""
    f_update_begin: str = ""
```

Pydantic validates types, patterns, ranges, and required fields *before*
the implementation function is called.  The implementation never does its
own argument parsing.

### 3.2. Output Models

Every tool returns a Pydantic `BaseModel`.  No raw strings.  No raw dicts.

For tools that primarily produce side effects (file creation/modification),
the output model reports what happened:

```python
class GenEntityOutput(BaseModel):
    """TOOL_REGISTRY.md S3.2"""
    files_created: list[str]
    files_modified: list[str]
    warnings: list[str] = []
    message: str
```

For scan tools, the output model is the unified scan schema
(SCAN_FRAMEWORK.md S2).

For build tools, the output model includes exit code, stdout, stderr.

### 3.3. Error Representation

Tool errors are **not** encoded as `"ERROR (exit N):\n..."` strings.  They
are raised as typed exceptions that the MCP transport layer serializes
appropriately:

```python
class ToolError(Exception):
    """Base class for tool errors.  TOOL_REGISTRY.md S3.3"""
    def __init__(self, message: str, recoverable: bool = False):
        self.message = message
        self.recoverable = recoverable

class ValidationError(ToolError): ...
class FileConflictError(ToolError): ...
class ClangdUnavailableError(ToolError): ...
class BuildFailedError(ToolError): ...
```

## 4. Registry Discovery

The registry is a module that auto-discovers all `ToolDef` objects:

```python
# registry.py
TOOLS: dict[str, ToolDef] = {}

def discover_tools() -> dict[str, ToolDef]:
    """Import all tools/*.py modules and collect their TOOL_DEFS lists."""
    ...
```

Each tool module exports a module-level `TOOL_DEFS: list[ToolDef]` variable.

### 4.1. Registration Invariants (CI-enforced)

- No two tools may have the same `name`.
- Every `ToolDef.name` must match the function name of its `implementation`.
- Every `ToolDef.input_model` field must have a `Field(description=...)`.
- Every `ToolDef.output_model` must be JSON-serializable.
- Every `ToolDef` must have a non-empty `description`.

## 5. Derived Surfaces

From the registry, the following are **generated, not hand-maintained**:

### 5.1. MCP Tool Registration

`mcp_server.py` iterates `TOOLS` and registers each as an `@mcp.tool()`.
The tool's docstring is `ToolDef.description`.  The parameter schema is
derived from `ToolDef.input_model.model_json_schema()`.

### 5.2. CLI Entry Points (Optional)

A generic CLI runner can invoke any tool from the command line:

```bash
python -m lavender_tools2 gen_entity --name Zombie --gen-update
```

The CLI argument parser is generated from the Pydantic model's fields.

### 5.3. Documentation

A doc generator can produce markdown tool reference docs from the registry.

### 5.4. Test Scaffolding

CI can verify that every registered `ToolDef` has at least one test case
that exercises the implementation function (not just subprocess argument
construction).
