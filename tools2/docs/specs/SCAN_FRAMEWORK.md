# Lavender Tools v2 — Scan Framework

> **Spec reference:** OVERVIEW.md S1.4  
> **Status:** DRAFT

## 1. Scan Tool Protocol

### 1.1. The Problem

Tools v1 had **six scan tools** that shared ~60% identical code but had
**two divergent output schemas**:

- Verification scanners (`scan_entity`, `scan_scene`, `scan_ui`,
  `scan_textures`, `scan_game_actions`) emitted `{tool, timestamp,
  project_root, summary, results: [...]}`.
- Inventory scanners (`scan_assets`, `scan_sprite_assets`) emitted
  bespoke structures with no `results` array.

Additionally:
- `_parse_gen_entries()` was copy-pasted across 4 files.
- `scan_entity` and `scan_ui` had a `"\\n"` split bug.
- All scan tools silently swallowed exceptions.
- No scan tool recorded its output in `tool_history`.

### 1.2. The Solution: ScanBase

All scan tools inherit from a common base that handles boilerplate:

```python
class ScanBase(ABC):
    """Base class for all scan tools.  SCAN_FRAMEWORK.md S1.2"""

    @abstractmethod
    def scan(self, ctx: ToolContext) -> list[ScanCheck]: ...

    def run(self, input: BaseModel, ctx: ToolContext) -> ScanOutput:
        """Execute the scan and produce a ScanOutput.  SCAN_FRAMEWORK.md S1.2

        1. Call self.scan(ctx) to get check results.
        2. Compute summary statistics.
        3. Return a ScanOutput model.
        """
        checks = self.scan(ctx)
        summary = ScanSummary(
            total_checked=len(checks),
            passed=sum(1 for c in checks if c.status == "pass"),
            warnings=sum(1 for c in checks if c.status == "warning"),
            errors=sum(1 for c in checks if c.status == "error"),
        )
        return ScanOutput(
            tool=self.tool_name,
            timestamp=datetime.now(timezone.utc),
            project_root=str(ctx.project_dir),
            summary=summary,
            results=checks,
        )
```

### 1.3. Subclass Responsibilities

Each scan tool subclass implements `scan()` which returns a list of
`ScanCheck` objects.  The base class handles JSON serialization, summary
computation, output file writing, and traceability recording.

## 2. Unified Output Schema

### 2.1. ScanOutput

```python
class ScanOutput(BaseModel):
    """Unified output for all scan tools.  SCAN_FRAMEWORK.md S2.1"""
    tool: str
    timestamp: datetime
    project_root: str
    summary: ScanSummary
    results: list[ScanCheck]
```

### 2.2. ScanSummary

```python
class ScanSummary(BaseModel):
    """SCAN_FRAMEWORK.md S2.2"""
    total_checked: int
    passed: int
    warnings: int
    errors: int
```

### 2.3. ScanCheck

```python
class ScanCheck(BaseModel):
    """SCAN_FRAMEWORK.md S2.3"""
    check_id: str              # e.g. "4.3.1" — references a spec section
    status: Literal["pass", "warning", "error"]
    message: str               # Human/AI-readable description
    source: ScanSource         # What was checked
    expected: str              # What was expected
    actual: str = ""           # What was found (empty if pass)
    clangd_query: str = ""     # The clangd query used, for debuggability
```

### 2.4. ScanSource

```python
class ScanSource(BaseModel):
    """SCAN_FRAMEWORK.md S2.4"""
    file: str                  # File path relative to project root
    element: str               # The specific identifier checked
    line: int | None = None    # Line number if applicable
```

### 2.5. Inventory Scanners

`scan_assets` and `scan_sprite_assets` also emit `ScanOutput`.  Their
`results` list contains checks like:

- "Asset file `foo.png` classified as sprite" (status: pass)
- "Directory `assets/entities/` is empty" (status: warning)
- "Unknown file type at `assets/mystery.bin`" (status: warning)

This unifies the output schema.  An AI consumer can parse ANY scan
tool's output with a single Pydantic model.

## 3. Clangd Integration

### 3.1. Session Management

`core/clangd.py` provides a `ClangdSession` that:

- Starts a clangd subprocess with the project's `compile_commands.json`.
- Communicates via LSP protocol (pygls `LanguageClient`).
- Runs the async event loop in a daemon thread.
- Supports lazy initialization (only started when first scan tool needs it).
- Supports automatic `compile_commands.json` regeneration if missing/empty.

### 3.2. Query Functions

`core/clangd.py` exports pure functions:

```python
def find_definition(session: ClangdSession, file: str, line: int, col: int) -> str | None: ...
def find_references(session: ClangdSession, file: str, line: int, col: int) -> list[str]: ...
def get_symbols(session: ClangdSession, file: str) -> list[Symbol]: ...
def search_workspace_symbols(session: ClangdSession, query: str) -> list[Symbol]: ...
def get_hover_info(session: ClangdSession, file: str, line: int, col: int) -> str | None: ...
```

These are imported by scan tools directly.  They do NOT live in the MCP
server layer.

### 3.3. Error Handling

Clangd queries that fail return `None` or empty lists.  They do NOT
swallow exceptions silently.  If clangd is unavailable, the scan tool
emits a `ScanCheck` with `status="warning"` and `message="clangd not
available"` — but it still runs any checks that don't require clangd.

## 4. Scan Tool Catalog

### 4.1. Verification Scanners

| Tool | Purpose | Checks |
|------|---------|--------|
| `scan_entity` | Entity lifecycle handlers | Handler existence via clangd |
| `scan_scene` | Scene handlers + UI wiring | Handler existence, window cross-refs |
| `scan_ui` | UI XML handler verification | Handler C symbol existence via clangd |
| `scan_textures` | Orphan/missing textures | Registrar vs usage cross-ref |
| `scan_game_actions` | Game action handlers | Process handler existence + registration mode |

### 4.2. Inventory Scanners

| Tool | Purpose | Output |
|------|---------|--------|
| `scan_assets` | Classify all project assets | File inventory with type classification |
| `scan_sprite_assets` | Analyze sprite sheet layouts | Group boundaries, frame resolution, animation patterns |

### 4.3. GEN-Block Parsing

All scan tools that need to parse GEN-marker blocks use
`core.codegen.find_gen_block()` (CODEGEN.md S2.2).  No per-scan-tool
regex implementations.
