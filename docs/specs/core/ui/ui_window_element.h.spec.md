# Specification: core/include/ui/ui_window_element.h

## Overview

Specializes a `UI_Element` as a window element — a UI element that owns and
manages a child `Graphics_Window`. When the element is created, it opens a
new graphics window of the specified kind.

## Dependencies

- `defines.h` (for `UI_Element`, `Graphics_Window`, `Game`, `Identifier__u32`, `Vector__3i32`)
- `defines_weak.h` (forward declarations)
- `types/implemented/graphics_window_kind.h` (for `Graphics_Window_Kind` enum)

## Types

### Window-Specific Data (union member in UI_Element)

    struct {
        Graphics_Window *p_ui_window__graphics_window;
    };

The lifetime of the child graphics window does not exceed the UI window
element's lifetime.

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__window_element_and__open_window` | `(UI_Element*, Game*, Graphics_Window_Kind, Identifier__u32 parent_uuid, Vector__3i32 origin) -> void` | Initializes as window element and opens a child graphics window. Sets kind to `UI_Element_Kind__Window`. Uses `open_ui_window_with__this_uuid_and__parent_uuid` from `ui_context.h`. |

## Agentic Workflow

### Preconditions

- `p_ui_window_element` must be non-null and allocated from a `UI_Manager`.

### Relationships

- The child window's lifetime is tied to this element's lifetime.

## Header Guard

`UI_WINDOW_ELEMENT_H`
