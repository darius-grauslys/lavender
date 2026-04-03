# UI Slider Specification

## File
`core/include/ui/ui_slider.h`

## Purpose
Specializes a `UI_Element` as a slider — a constrained draggable that moves
along a single axis within a defined span, producing a percentage value.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `UI_Element`, slider union members |
| `defines_weak.h` | Forward declarations |
| `game.h` | `Game` type |
| `rendering/gfx_context.h` | `Gfx_Context` accessors |
| `rendering/sprite.h` | `Sprite` operations |
| `ui/ui_element.h` | `UI_Element` operations, flag queries |
| `vectors.h` | `Vector__3i32` |

## Slider-Specific Data (union members in `UI_Element`)
