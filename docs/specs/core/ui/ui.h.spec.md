# 7 Specification: core/include/ui/ui.h

## 7.1 Overview

Root header for the UI subsystem. Currently serves only as an entry point
that pulls in `defines.h`. It does not declare any types, functions, or
macros of its own.

## 7.2 Dependencies

- `defines.h` (for all core type definitions)

## 7.3 Types

None.

## 7.4 Functions

None.

## 7.5 Agentic Workflow

### 7.5.1 Usage Pattern

Include this header when you need general access to the UI subsystem's
foundational types (via `defines.h`). This file may be extended in the
future to aggregate additional UI sub-headers.

## 7.6 Header Guard

`UI_H`
