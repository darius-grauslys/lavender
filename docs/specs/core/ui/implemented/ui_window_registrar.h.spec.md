# 14 Specification: core/include/ui/implemented/ui_window_registrar.h

## 14.1 Overview

Declares the game-specific function that registers all UI window types into
the graphics context's `UI_Context`. This file is a **template** — it is
copied to the game project directory by `lav_new_project` and is meant to
be modified by the engine user.

## 14.2 Template Behavior

This file resides in `core/include/ui/implemented/` and is copied to the
game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the original
in core serves as the default/template. The `implemented/` directory is NOT
in the core include path — it is only in the game project's include path.

## 14.3 Dependencies

- `defines.h` (for `Gfx_Context` type)

## 14.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_ui_windows` | `(Gfx_Context*) -> void` | Registers all game-specific UI window types by calling `register_ui_window_into__ui_context` for each `Graphics_Window_Kind` the game supports. |

## 14.5 Agentic Workflow

### 14.5.1 Implementation Notes

- Must be implemented by the game project.
- Typically called during game initialization.
- Each call to `register_ui_window_into__ui_context` associates a
  `Graphics_Window_Kind` with:
  - `f_UI_Window__Load` callback
  - `f_UI_Window__Close` callback
  - Sprite count requirement
  - UI element count requirement
- The `Graphics_Window_Kind` enum must be extended in the game's
  `types/implemented/graphics_window_kind.h`.

## 14.6 Header Guard

`UI_REGISTRAR__IMPLEMENTED_H`
