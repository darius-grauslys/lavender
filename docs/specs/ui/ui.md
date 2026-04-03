# UI Module — Root Header Specification

## File
`core/include/ui/ui.h`

## Purpose
Root header for the UI subsystem. Currently serves only as an entry point
that pulls in `defines.h`. It does not declare any types, functions, or
macros of its own.

## Dependencies
| Header       | Purpose                          |
|--------------|----------------------------------|
| `defines.h`  | All core type definitions        |

## Public API
None. This header is a placeholder/aggregator.

## Usage Notes
- Include this header when you need general access to the UI subsystem's
  foundational types (via `defines.h`).
- This file may be extended in the future to aggregate additional UI
  sub-headers.
