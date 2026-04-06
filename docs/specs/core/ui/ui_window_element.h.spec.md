# 20 Specification: core/include/ui/ui_window_element.h

## 20.1 Overview

Specializes a `UI_Element` as a window element — a UI element that owns and
manages a child `Graphics_Window`. When the element is created, it opens a
new graphics window of the specified kind.

## 20.2 Dependencies

- `defines.h` (for `UI_Element`, `Graphics_Window`, `Game`, `Identifier__u32`, `Vector__3i32`)
- `defines_weak.h` (forward declarations)
- `types/implemented/graphics_window_kind.h` (for `Graphics_Window_Kind` enum)

## 20.3 Types

### 20.3.1 Window-Specific Data (union member in UI_Element)

    struct {
        Graphics_Window *p_ui_window__graphics_window;
    };

The lifetime of the child graphics window does not exceed the UI window
element's lifetime.

## 20.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__window_element_and__open_window` | `(UI_Element*, Game*, Graphics_Window_Kind, Identifier__u32 parent_uuid, Vector__3i32 origin) -> void` | Initializes as window element and opens a child graphics window. Sets kind to `UI_Element_Kind__Window`. Uses `open_ui_window_with__this_uuid_and__parent_uuid` from `ui_context.h`. |

## 20.5 Agentic Workflow

### 20.5.1 Preconditions

- `p_ui_window_element` must be non-null and allocated from a `UI_Manager`.

### 20.5.2 Relationships

- The child window's lifetime is tied to this element's lifetime.

## 20.6 Header Guard

`UI_WINDOW_ELEMENT_H`
