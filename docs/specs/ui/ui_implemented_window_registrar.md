# UI Window Registrar (Implemented) Specification

## File
`core/include/ui/implemented/ui_window_registrar.h`

## Purpose
Declares the game-specific function that registers all UI window types into
the graphics context's `UI_Context`. This function is implemented by the game
(not by the engine core) and serves as the hook where all
`Graphics_Window_Kind` entries are associated with their load/close callbacks
and resource requirements.

## Dependencies
| Header       | Purpose                          |
|--------------|----------------------------------|
| `defines.h`  | `Gfx_Context` type              |

## Functions

### `register_ui_windows`
