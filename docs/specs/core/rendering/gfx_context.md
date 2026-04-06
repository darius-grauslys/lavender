# 1. Graphics Context Specification

## 1.1 File
`core/include/rendering/gfx_context.h`

## 1.2 Purpose
Provides initialization and inline accessor functions for `Gfx_Context` —
the top-level graphics state container that aggregates all rendering
subsystems.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Gfx_Context` and all sub-component types |
| `defines_weak.h` | Forward declarations |

## 1.4 Types

### 1.4.1 `Gfx_Context` (defined in `defines.h`)
