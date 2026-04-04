# Specification: core/include/types/implemented/ui_element_kind.h

## Overview

Template header that defines the `UI_Element_Kind` enum — the set of UI
element types available in the engine. Unlike most implemented types, the
core engine defines all standard UI element kinds. This file is copied to
the game project directory by `tools/lav_new_project` but typically does
not need modification unless adding entirely new UI element categories.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_UI_ELEMENT_KIND` is not defined after
the `#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### UI_Element_Kind (enum)

    typedef enum UI_Element_Kind {
        UI_Element_Kind__None,
        UI_Element_Kind__Button,
        UI_Element_Kind__Draggable,
        UI_Element_Kind__Slider,
        UI_Element_Kind__Drop_Zone,
        UI_Element_Kind__Text,
        UI_Element_Kind__Text_Box,
        UI_Element_Kind__Logical,
        UI_Element_Kind__Window,
        UI_Element_Kind__Unknown
    } UI_Element_Kind;

| Value | Description |
|-------|-------------|
| `UI_Element_Kind__None` | No element / sentinel. |
| `UI_Element_Kind__Button` | Clickable button with optional toggle. |
| `UI_Element_Kind__Draggable` | Element that can be picked up and moved. |
| `UI_Element_Kind__Slider` | Constrained draggable along one axis. |
| `UI_Element_Kind__Drop_Zone` | Region that receives dropped draggables. |
| `UI_Element_Kind__Text` | Read-only text display. |
| `UI_Element_Kind__Text_Box` | Editable text input. |
| `UI_Element_Kind__Logical` | Logical grouping, no visual. |
| `UI_Element_Kind__Window` | Element that owns a child `Graphics_Window`. |
| `UI_Element_Kind__Unknown` | End-of-enum sentinel. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/ui_element_kind.h>
    #ifndef DEFINE_UI_ELEMENT_KIND
    enum UI_Element_Kind { ... };
    #endif

## Agentic Workflow

### Extension Pattern

This enum is typically not extended. If adding a new UI element category,
add it before `Unknown` and implement the corresponding initialization
and handler functions.

### Constraints

- All listed kinds are used by core engine code (`ui_button.h`,
  `ui_draggable.h`, `ui_slider.h`, `ui_drop_zone.h`, `ui_text.h`,
  `ui_text_box.h`, `ui_window_element.h`).
- `UI_Element_Kind__Unknown` must remain last.
- The `#define DEFINE_UI_ELEMENT_KIND` line must not be removed.

## Header Guard

`IMPL_UI_ELEMENT_KIND_H`
