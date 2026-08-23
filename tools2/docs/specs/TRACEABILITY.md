# Lavender Tools v2 — Traceability

> **Spec reference:** OVERVIEW.md S1.2, S1.3  
> **Status:** DRAFT

## 1. Transaction Log

### 1.1. Mandatory, Not Opt-In

In tools v1, `tool_history.py` was opt-in: each script decided whether to
call `record_create()` / `record_modify()`.  Most didn't.  The module also
had a path resolution bug (`parents[1]` instead of `parents[2]`) that caused
it to silently no-op without `$LAVENDER_DIR`.

In tools v2, traceability is **mandatory at the dispatch layer**.  The MCP
server creates a `Transaction` object before calling the tool implementation.
The implementation uses `transaction.record_*()` methods.  The MCP server
commits the transaction after the tool returns, or rolls back on exception.

A tool that mutates files but produces an empty transaction log is a **CI
failure**.

### 1.2. Transaction Object

```python
class Transaction:
    """TRACEABILITY.md S1.2"""
    id: uuid.UUID                          # Unique per invocation
    tool_name: str
    timestamp: datetime
    records: list[FileRecord]
    committed: bool = False

    def record_create(self, path: Path, content_hash: str) -> None: ...
    def record_modify(self, path: Path, original_hash: str,
                      new_hash: str, diff: str) -> None: ...
    def record_delete(self, path: Path, original_hash: str) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

### 1.3. FileRecord

```python
class FileRecord(BaseModel):
    """TRACEABILITY.md S1.3"""
    path: str                              # Relative to project root
    operation: Literal["create", "modify", "delete"]
    original_hash: str | None              # SHA-256 of content before mutation
    new_hash: str | None                   # SHA-256 of content after mutation
    diff: str | None                       # Unified diff (for modify ops)
    backup_path: str | None                # Path to pre-mutation backup
    timestamp: datetime
```

### 1.4. Storage

Transaction logs are written to `.lavender/tool-history/` as append-only
JSONL files (one line per `FileRecord`), partitioned by UTC day:

```
.lavender/tool-history/2026-05-22.jsonl
```

Each line is a JSON object with: `transaction_id`, `tool_name`, `timestamp`,
`record` (the `FileRecord`).

JSONL (append-only) eliminates the read-modify-write race condition that
existed in tools v1's JSON manifest files.

### 1.5. Pipeline Context

When running inside a pipeline, the transaction inherits context from
environment variables:

- `LAV_PIPELINE_RUN_ID`
- `LAV_PIPELINE_ID`
- `LAV_NODE_ID`
- `LAV_EXECUTION_MODE`

These are recorded in every JSONL line so that post-run analysis can
correlate tool invocations to pipeline nodes.

## 2. Undo/Redo

### 2.1. Backup Strategy

Before every file mutation, `core/atomic.py` creates a backup:

- **Modify**: Copy original to `.lavender/backups/{transaction_id}/{relative_path}`.
- **Create**: Record the path in the transaction (undo = delete).
- **Delete**: Copy original to `.lavender/backups/{transaction_id}/{relative_path}`.

### 2.2. Undo Operation

An `undo_transaction(transaction_id: UUID)` function:

1. Reads the transaction's `FileRecord` entries from the JSONL log.
2. For each record, in reverse order:
   - **create** → delete the file.
   - **modify** → restore from backup.
   - **delete** → restore from backup.
3. Appends a compensating transaction to the log.

### 2.3. Redo Operation

Redo is re-executing the tool with the same inputs.  Because all tools
are deterministic (given the same file state), redo is equivalent to
calling the tool again.  The transaction log provides the input
parameters.

### 2.4. Limitations

- Undo is only valid if no other tool has modified the same files since
  the transaction.  The undo function verifies file hashes before
  restoring and aborts if they don't match.
- Backup storage is bounded: `.lavender/backups/` is pruned to the last
  N transactions (configurable, default 50).

## 3. Atomic Writes

### 3.1. write_atomic

```python
def write_atomic(path: Path, content: str | bytes) -> None:
    """Write content to path atomically.  TRACEABILITY.md S3.1

    Strategy: write to a temporary file in the same directory, then
    os.replace() into place.  This guarantees that the file is either
    fully written or not modified at all.
    """
```

Every file mutation in tools v2 MUST use `write_atomic`.  Direct
`open(path, 'w')` is banned.

### 3.2. File Locking

```python
@contextmanager
def lock_file(path: Path, timeout: float = 10.0) -> Iterator[None]:
    """Acquire an advisory lock on path.  TRACEABILITY.md S3.2

    Uses fcntl.flock on a .lock sidecar file.  Prevents concurrent
    read-modify-write races between parallel tool invocations.
    """
```

Locking is used for:
- GEN-marker block modifications (multiple tools may target the same
  registrar file).
- Transaction log writes (though JSONL append is mostly safe,
  concurrent appends can interleave).

## 4. Tool History Query API

### 4.1. Query Functions

```python
def query_history(
    tool_name: str | None = None,
    since: datetime | None = None,
    path_pattern: str | None = None,
) -> list[FileRecord]:
    """Query the transaction log.  TRACEABILITY.md S4.1"""

def query_files_touched_by(tool_name: str) -> list[str]:
    """Return all file paths ever touched by a tool.  TRACEABILITY.md S4.1"""

def query_tools_that_touched(path: str) -> list[str]:
    """Return all tools that have touched a file.  TRACEABILITY.md S4.1"""
```

### 4.2. MCP Exposure

These query functions are exposed as MCP tools (`query_tool_history`,
`query_files_touched_by`, `query_tools_that_touched`) so that AI agents
and the pipeline runner can inspect the audit trail programmatically.

## 5. CI Enforcement

### 5.1. Mutation Coverage Check

A CI script verifies that every `ToolDef` where `mutating=True`:
- Has at least one `record_create` or `record_modify` call in its
  implementation.
- Never calls `open(path, 'w')` directly (must use `write_atomic`).

### 5.2. Transaction Integrity Check

A CI script verifies that after running the full test suite, every
transaction in the test `.lavender/tool-history/` log has:
- At least one `FileRecord` (no empty transactions for mutating tools).
- Valid `original_hash` / `new_hash` pairs.
- `backup_path` pointing to an existing file (for modify/delete records).
