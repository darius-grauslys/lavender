# UI Context Specification

## File
`core/include/ui/ui_context.h`

## Purpose
Manages the collection of `UI_Manager` instances and the registry of
`UI_Window_Record` entries. Provides the high-level API for opening and
closing UI windows, which involves allocating graphics windows, UI managers,
and populating them with UI elements via registered load callbacks.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Context`, `UI_Manager`, `Graphics_Window`, all core types |
| `defines_weak.h` | Forward declarations |
| `types/implemented/graphics_window_kind.h` | `Graphics_Window_Kind` enum |

## Types

### `UI_Context` (defined in `defines.h`)
