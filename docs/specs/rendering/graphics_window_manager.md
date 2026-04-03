# Graphics Window Manager Specification

## File
`core/include/rendering/graphics_window_manager.h`

## Purpose
Manages a fixed-size pool of `Graphics_Window` instances. Provides
allocation, deallocation, lookup, parent-child relationships, sorting by
priority, and batch composition/rendering of all windows.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Graphics_Window_Manager`, `Graphics_Window`, `Gfx_Context` |
| `defines_weak.h` | Forward declarations |
| `serialization/hashing.h` | UUID hashing for lookup and allocation |
| `serialization/identifiers.h` | UUID utilities, `is_identifier_u32__invalid` |

## Types

### `Graphics_Window_Manager` (defined in `defines.h`)
