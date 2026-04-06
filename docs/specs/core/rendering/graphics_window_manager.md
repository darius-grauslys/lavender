# 1. Graphics Window Manager Specification

## 1.1 File
`core/include/rendering/graphics_window_manager.h`

## 1.2 Purpose
Manages a fixed-size pool of `Graphics_Window` instances. Provides
allocation, deallocation, lookup, parent-child relationships, sorting by
priority, and batch composition/rendering of all windows.

## 1.3 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Graphics_Window_Manager`, `Graphics_Window`, `Gfx_Context` |
| `defines_weak.h` | Forward declarations |
| `serialization/hashing.h` | UUID hashing for lookup and allocation |
| `serialization/identifiers.h` | UUID utilities, `is_identifier_u32__invalid` |

## 1.4 Types

### 1.4.1 `Graphics_Window_Manager` (defined in `defines.h`)
