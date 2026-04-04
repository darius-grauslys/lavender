# Specification: core/include/types/implemented/graphics_window_kind.h

## Overview

Template header that defines the `Graphics_Window_Kind` enum — the set of
graphics window types available in the game. Each kind corresponds to a
registered UI window with load/close callbacks. This file is copied to the
game project directory by `tools/lav_new_project` and is meant to be
extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_GRAPHICS_WINDOW_KIND` is not defined
after the `#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Graphics_Window_Kind (enum)

    typedef enum Graphics_Window_Kind {
        Graphics_Window_Kind__None = 0,
        Graphics_Window_Kind__Unknown
    } Graphics_Window_Kind;

| Value | Description |
|-------|-------------|
| `Graphics_Window_Kind__None` | No window / sentinel. |
| `Graphics_Window_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/graphics_window_kind.h>
    #ifndef DEFINE_GRAPHICS_WINDOW_KIND
    typedef enum Graphics_Window_Kind { ... } Graphics_Window_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef enum Graphics_Window_Kind {
        Graphics_Window_Kind__None = 0,
        Graphics_Window_Kind__Main_Menu,
        Graphics_Window_Kind__Inventory,
        Graphics_Window_Kind__HUD,
        Graphics_Window_Kind__Unknown
    } Graphics_Window_Kind;

### Constraints

- `Graphics_Window_Kind__None` must remain first (value 0).
- `Graphics_Window_Kind__Unknown` must remain last.
- `Graphics_Window_Kind__Unknown` is used for array sizing in
  `UI_Context.ui_window_record[Graphics_Window_Kind__Unknown]`.
- Each kind must be registered via `register_ui_window_into__ui_context`
  (see `ui/implemented/ui_window_registrar.h`).
- The `#define DEFINE_GRAPHICS_WINDOW_KIND` line must not be removed.

## Header Guard

`IMPL_GRAPHICS_WINDOW_KIND_H`
