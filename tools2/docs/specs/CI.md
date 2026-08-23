# Lavender Tools v2 — CI Enforcement

> **Spec reference:** OVERVIEW.md S1.7  
> **Status:** DRAFT

## 1. Philosophy

Tools v1 relied on human discipline for structural invariants.  The result:
4 duplicate function definitions, diverged parameter names, tools that
skipped traceability, tests that only checked argument serialization.

Tools v2 enforces structural invariants with automated checks that run in
CI and can be run locally via `pytest`.  If a check fails, the build fails.

## 2. Structural Checks

### 2.1. Registry Consistency

**Check:** Every file in `tools/` that exports a `TOOL_DEFS` list has all
its `ToolDef` objects present in the global registry.

**Check:** No two `ToolDef` objects have the same `name`.

**Check:** Every `ToolDef.implementation` function name matches
`ToolDef.name`.

**Check:** Every `ToolDef.input_model` field has a `Field(description=...)`.

**Check:** Every `ToolDef.output_model` is JSON-serializable
(`model_json_schema()` succeeds).

### 2.2. Traceability Coverage

**Check:** Every `ToolDef` where `mutating=True` has at least one
`transaction.record_create` or `transaction.record_modify` call in its
implementation (verified by AST inspection or test execution).

**Check:** No Python file in `tools2/` contains a bare `open(..., 'w')`
or `open(..., 'wb')` call outside of `core/atomic.py`.  All writes go
through `write_atomic`.

### 2.3. Test Coverage

**Check:** Every registered `ToolDef` has at least one test function whose
name contains the tool name.

**Check:** Every test for a mutating tool verifies at least one file-system
side effect (file created, file content matches, GEN-block updated).

**Check:** No test file exceeds 500 lines.  God test files are banned.

### 2.4. Import Layer Enforcement

**Check:** No file in `core/` imports from `tools/` or `mcp_server.py`.
(Layer 1 must not depend on Layer 2 or Layer 3.)

**Check:** No file in `tools/` imports from `mcp_server.py`.
(Layer 2 must not depend on Layer 3.)

**Check:** `mcp_server.py` only imports from `core/` and `tools/`.
(Layer 3 depends on Layer 2 and Layer 1.)

### 2.5. No Duplicate Definitions

**Check:** No Python file contains two function definitions with the same
name.  (Catches the tools v1 `clangd_references` duplicate bug.)

### 2.6. Naming Convention Enforcement

**Check:** All `ToolDef` objects in the `gen_*` category have `mutating=True`.

**Check:** All `ToolDef` objects in the `scan_*` category have `mutating=False`.

**Check:** No `ToolDef.input_model` uses the parameter name `project_root`,
`game_dir`, or `project-dir`.  The canonical name is `project_dir`
(ARCHITECTURE.md S4).

## 3. The gen_tool.py Question

### 3.1. Context

The audit recommended a `gen_tool.py` meta-tool that scaffolds new tools
from a manifest.  Is this strictly necessary?

### 3.2. Analysis

**What gen_tool.py would do:**
- Create a new `tools/gen_foo.py` file from a template.
- Create a new `tests/test_gen_foo.py` file from a template.
- Add the Pydantic Input/Output models.
- Register the ToolDef.

**What makes this unnecessary in tools v2:**
- Adding a tool is already a **1-file operation**: create `tools/gen_foo.py`
  with a `TOOL_DEFS` list.  The registry auto-discovers it.
- The CI checks (S2.1–S2.3) will immediately flag missing tests, missing
  descriptions, missing traceability.
- A test template file (`tests/_template_test.py`) can serve as a copy-
  paste starting point.

**What would make it necessary:**
- If the project had many contributors unfamiliar with the conventions.
- If the tool definition required non-trivial boilerplate beyond a Pydantic
  model and a function.

### 3.3. Decision

`gen_tool.py` is **NOT required at this time**.  The ToolDef protocol is
simple enough that creating a tool file from a template (or copying an
existing tool) is equivalent effort.  CI enforcement catches structural
violations immediately.

If the team grows or the ToolDef protocol becomes more complex, revisit
this decision.  The cost of adding `gen_tool.py` later is low.

## 4. Running CI Locally

```bash
# Run all structural checks
pytest tools2/tests/ci/ -v

# Run only the registry consistency checks
pytest tools2/tests/ci/test_registry.py -v

# Run only the traceability coverage checks
pytest tools2/tests/ci/test_traceability.py -v
```

All CI checks are regular pytest tests.  No separate CI framework is needed.
