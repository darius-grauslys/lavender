# Lavender Tools v2 — Specification Overview

> **Status:** DRAFT  
> **Date:** 2026-05-22  
> **Supersedes:** `tools/lavender_tools/` (tools v1)  
> **Lavender Spec Strategy:** Numeric sections, mandatory traceability, immutable anchors.

## 0. Purpose

This document is the immutable anchor for the Lavender Tools v2 specification
system.  It defines the scope, goals, constraints, non-goals, and
organizational conventions for a ground-up reimplementation of the Lavender
game engine's AI-native MCP tooling.

Tools v2 replaces `tools/lavender_tools/` (22,800 lines across ~55 files)
which was found to have systemic coherency failures in a May 2026 audit:
architectural duplication (two parallel MCP servers), broken traceability
(`tool_history` no-ops by default), zero atomic writes, zero file locking,
no formal schemas, copy-paste as architecture, and a half-finished migration.

Tools v2 is a **hard cut** — no backward compatibility with v1.

## 1. Goals

1.1. **Single Source of Truth** — Every tool is defined exactly once.
     The MCP surface, CLI surface, parameter schemas, return schemas,
     documentation, and tests are all derived from that single definition.

1.2. **Mandatory Traceability** — Every file mutation is recorded in a
     transaction log before the tool returns.  No opt-in.  No silent no-ops.

1.3. **Undo/Redo** — Every mutation is reversible.  The system maintains
     enough state to roll back any tool invocation atomically.

1.4. **Pydantic Enforcement** — All tool inputs and outputs are validated
     by Pydantic v2 models.  No ad-hoc dict construction.  No bespoke JSON
     schemas.

1.5. **Sandbox-First** — The architecture must support execution inside a
     container (podman/docker) with the engine mounted read-only at
     `/lavender` and the game project mounted read-write at `/project`,
     with `--network none`.

1.6. **AI-Native Maintainability** — An AI agent must be able to understand,
     extend, and maintain the tooling from the code and specs alone, without
     oral tradition or tribal knowledge.

1.7. **CI Enforcement** — Structural invariants are enforced by automated
     checks, not human discipline.

## 2. Non-Goals

2.1. Backward compatibility with tools v1 at the Python API level.

2.2. Supporting Windows as a host for the tooling (Linux-only; container
     targets are Linux).

2.3. Replacing the LangGraph pipeline runner (`lav_pipeline/`).  The pipeline
     runner is a *consumer* of tools v2 via MCP.

2.4. Replacing the map editor (`tools/editors/`).

## 3. Constraints

3.1. **MCP SDK stdio deadlock** — The MCP Python SDK (`mcp` package)
     deadlocks after ~3 sequential `call_tool` invocations on a persistent
     stdio session due to zero-buffer `anyio.create_memory_object_stream(0)`.
     The pipeline runner must use HTTP transport (Streamable HTTP) or
     subprocess-per-call to avoid this.  See Open Brain: "CRITICAL ISSUE —
     MCP SDK stdio_client deadlocks" (2026-05-01).

3.2. **Container networking** — The pipeline runs on the HOST because it
     needs network access for LLM API calls.  Tools run in the CONTAINER
     with `--network none`.  The API key never enters the container.
     See Open Brain: "Lavender Agentic Game Engine System — Architecture
     Overview" (2026-05-02).

3.3. **Container runtime** — The host is Void Linux with Podman 5.7.1.
     The `docker` CLI fails with "unable to upgrade to tcp, received 500"
     because the Docker server is actually Podman.  Runtime auto-detection
     (podman-first) is required.

3.4. **Engine code generation correctness** — The GEN-marker logic and C
     code generation patterns in tools v1 are correct and battle-tested.
     The *logic* is ported; the *architecture* is replaced.

3.5. **Python >= 3.10** — Required for `X | Y` union syntax.

## 4. Spec Organization

All specs live in `tools2/docs/specs/`.  The following files are defined:

| File | Contents | Section Range |
|------|----------|---------------|
| `OVERVIEW.md` | This file.  Immutable anchor. | 0–6 |
| `CHANGES.md` | Change log.  Immutable anchor. | — |
| `ARCHITECTURE.md` | Layered architecture, call flow, sandbox model | 1–5 |
| `TOOL_REGISTRY.md` | Tool definition protocol, Pydantic models, single-source-of-truth | 1–5 |
| `TRACEABILITY.md` | Transaction log, undo/redo, atomic writes, file locking | 1–5 |
| `CODEGEN.md` | GEN-marker protocol, C code generation patterns, shared parsing | 1–4 |
| `SCAN_FRAMEWORK.md` | Scan tool protocol, output schema, clangd integration | 1–4 |
| `MCP_SERVER.md` | MCP server design, transport, sandbox backend | 1–5 |
| `CI.md` | Automated enforcement, linting, structural checks | 1–4 |
| `MIGRATION.md` | Port plan from tools v1 to tools v2 | 1–4 |

## 5. Traceability Conventions

5.1. Every function and test case MUST reference at least one numbered spec
     section (e.g., `ARCHITECTURE.md S3.2`).

5.2. Helper functions that do not directly reference a spec section must
     reference at least one function that does.

5.3. The `CHANGES.md` file records every spec modification with timestamp,
     file, section, change type (`ADDED`, `REMOVED`, `CHANGED`), and
     description.

## 6. Terminology

| Term | Definition |
|------|-----------|
| **Tool** | A discrete, named operation exposed via MCP that performs code generation, file mutation, scanning, building, or querying. |
| **Tool Definition** | The single Python object (Pydantic model + implementation function) that defines a tool's name, parameters, return type, and behavior. |
| **Transaction** | An atomic unit of file mutations performed by a single tool invocation.  Either all mutations commit or none do. |
| **GEN-marker** | A pair of C comments (`// GEN-{NAME}-BEGIN` / `// GEN-{NAME}-END`) that delimit machine-managed regions in source files. |
| **Host** | The machine running the pipeline runner and LLM API calls. |
| **Container** | The podman/docker instance running tool execution with `--network none`. |
| **Engine directory** | `$LAVENDER_DIR` — the Lavender engine source tree. Mounted read-only in container. |
| **Project directory** | The game project CWD. Mounted read-write in container. |
