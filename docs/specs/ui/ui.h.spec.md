# Specification: core/include/ui/ui.h

## Overview

Root header for the UI subsystem. Currently serves only as an entry point
that pulls in `defines.h`. It does not declare any types, functions, or
macros of its own.

## Dependencies

- `defines.h` (for all core type definitions)

## Types

None.

## Functions

None.

## Agentic Workflow

### Usage Pattern

Include this header when you need general access to the UI subsystem's
foundational types (via `defines.h`). This file may be extended in the
future to aggregate additional UI sub-headers.

## Header Guard

`UI_H`
