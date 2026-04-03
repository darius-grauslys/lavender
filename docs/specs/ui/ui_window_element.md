# UI Window Element Specification

## File
`core/include/ui/ui_window_element.h`

## Purpose
Specializes a `UI_Element` as a window element — a UI element that owns and
manages a child `Graphics_Window`. When the element is created, it opens a
new graphics window of the specified kind.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Element`, `Graphics_Window`, `Graphics_Window_Kind` |
| `defines_weak.h` | Forward declarations |
| `types/implemented/graphics_window_kind.h` | `Graphics_Window_Kind` enum |

## Window-Specific Data (union member in `UI_Element`)
