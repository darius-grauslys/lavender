# UI Manager Specification

## File
`core/include/ui/ui_manager.h`

## Purpose
Manages a pool of `UI_Element` instances for a single `Graphics_Window`.
Handles allocation, deallocation, input polling, composition, rendering,
and priority ordering of UI elements.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Manager`, `UI_Element`, all core types |
| `defines_weak.h` | Forward declarations |
| `ui/ui_element.h` | `UI_Element` operations |

## Types

### `UI_Manager` (defined in `defines.h`)
