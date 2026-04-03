# UI Window Specification

## File
`core/include/ui/ui_window.h`

## Purpose
Provides the default close handler for UI windows. A UI window is a
`Graphics_Window` that has an associated `UI_Manager` for managing its
UI elements.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Gfx_Context`, `Graphics_Window`, `Game`, `UI_Manager` |
| `defines_weak.h` | Forward declarations |
| `types/implemented/ui_element_kind.h` | `UI_Element_Kind` enum |
| `ui/ui_element.h` | `UI_Element` operations |

## Functions

### `f_ui_window__close__default`
