# Lavender Tools v2 — Change Log

> **Immutable anchor document.  Must never be deleted.**

All entries are timestamped and include: file, section, change type, and
description.  Change types: `ADDED`, `REMOVED`, `CHANGED`.

---

## 2026-05-22

| File | Section | Type | Description |
|------|---------|------|-------------|
| `OVERVIEW.md` | 0–6 | ADDED | Initial draft.  Goals, non-goals, constraints, spec organization, traceability conventions, terminology. |
| `CHANGES.md` | — | ADDED | Initial creation of immutable change log anchor. |
| `ARCHITECTURE.md` | 1–5 | ADDED | Initial draft.  Layered architecture, sandbox model, call flow, transport decision, project root resolution. |
| `TOOL_REGISTRY.md` | 1–5 | ADDED | Initial draft.  ToolDef protocol, Pydantic input/output models, single-source-of-truth registry, derived surfaces. |
| `TRACEABILITY.md` | 1–5 | ADDED | Initial draft.  Transaction log, atomic writes, file locking, undo/redo, tool_history v2 design. |
| `CODEGEN.md` | 1–4 | ADDED | Initial draft.  GEN-marker protocol, shared parsing library, C code generation patterns. |
| `SCAN_FRAMEWORK.md` | 1–4 | ADDED | Initial draft.  ScanBase protocol, unified output schema, clangd integration, error handling. |
| `MCP_SERVER.md` | 1–5 | ADDED | Initial draft.  Single server, dual backend, transport strategy, dynamic registration, CWD guard. |
| `CI.md` | 1–4 | ADDED | Initial draft.  Structural enforcement, tool coverage, registry consistency, gen_tool question. |
| `MIGRATION.md` | 1–4 | ADDED | Initial draft.  Port order, tool-by-tool checklist, deprecation timeline, compatibility breaks. |
| `CHECKPOINT.md` | 0–7 | ADDED | Context checkpoint.  Full audit findings, historical context, decision rationale, next steps for continued AI work. |
