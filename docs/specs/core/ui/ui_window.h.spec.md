# 18 Specification: core/include/ui/ui_window.h

## 18.1 Overview

Provides the default close handler for UI windows. A UI window is a
`Graphics_Window` that has an associated `UI_Manager` for managing its
UI elements.

## 18.2 Dependencies

- `defines.h` (for `Gfx_Context`, `Graphics_Window`, `Game`, `UI_Manager`)
- `defines_weak.h` (forward declarations)
- `types/implemented/ui_element_kind.h` (for `UI_Element_Kind` enum)
- `ui/ui_element.h` (for `UI_Element` operations)

## 18.3 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `f_ui_window__close__default` | `(Gfx_Context*, Graphics_Window*, Game*, UI_Manager*) -> bool` | `bool` | Default window close handler. Releases all UI elements from the manager and performs cleanup. Matches `f_UI_Window__Close` signature. |

## 18.4 Agentic Workflow

### 18.4.1 Usage Pattern

Used as the default `f_UI_Window__Close` callback in `UI_Window_Record`.
Called by `close_ui_window` (from `ui_context.h`). Releases resources
managed by the `UI_Manager`.

### 18.4.2 Preconditions

- All parameters must be non-null.

## 18.5 Header Guard

`UI_WINDOW_H`
