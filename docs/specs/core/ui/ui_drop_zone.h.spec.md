# 2 Specification: core/include/ui/ui_drop_zone.h

## 2.1 Overview

Specializes a `UI_Element` as a drop zone — a region that can receive
draggable elements when they are dropped onto it.

## 2.2 Dependencies

- `defines.h` (for `UI_Element`, `m_UI_Receive_Drop`)
- `defines_weak.h` (forward declarations)

## 2.3 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__drop_zone` | `(UI_Element*, m_UI_Receive_Drop) -> void` | Initializes as drop zone. Sets kind to `UI_Element_Kind__Drop_Zone`. Sets receive drop handler. |
| `m_ui_drop_zone__receive_drop_handler__default` | `(UI_Element*, UI_Element* dropped, Game*, Graphics_Window*) -> void` | Default receive drop handler. |

## 2.4 Agentic Workflow

### 2.4.1 Usage Pattern

Drop zones work with `UI_Draggable` elements. When a draggable is dropped
over a drop zone, the `UI_Manager` polling logic invokes the drop zone's
`m_ui_receive_drop_handler` with both the drop zone element and the dropped
element as parameters.

### 2.4.2 Preconditions

- First parameter (`p_ui_button` — legacy parameter name) must be non-null and allocated from a `UI_Manager`.

## 2.5 Header Guard

`UI_DROP_ZONE`
