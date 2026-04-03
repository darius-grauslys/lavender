# UI Draggable Specification

## File
`core/include/ui/ui_draggable.h`

## Purpose
Specializes a `UI_Element` as a draggable element that can be picked up and
moved by the cursor. Draggable elements have handlers for both the drag
motion and the drop event.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `UI_Element`, `m_UI_Dragged`, `m_UI_Dropped`, `Game`, `Graphics_Window` |
| `ui/ui_element.h` | `UI_Element` operations and inline helpers |

## Types Used

### `UI_Element` (defined in `defines.h`)
The draggable specialization uses the anonymous empty struct union member:
