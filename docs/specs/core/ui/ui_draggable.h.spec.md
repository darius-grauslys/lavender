# 13 Specification: core/include/ui/ui_draggable.h

## 13.1 Overview

Specializes a `UI_Element` as a draggable element that can be picked up and
moved by the cursor. Draggable elements have handlers for both the drag
motion and the drop event.

## 13.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `UI_Element`, `m_UI_Dragged`, `m_UI_Dropped`, `Game`, `Graphics_Window`)
- `ui/ui_element.h` (for `UI_Element` operations and inline helpers)

## 13.3 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_element_as__draggable` | `(UI_Element*, m_UI_Dragged) -> void` | Initializes as draggable. Sets kind to `UI_Element_Kind__Draggable`. Sets dragged and dropped handlers. Pass null for default drag handler. |
| `m_ui_draggable__dragged_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default drag handler. Moves element to follow cursor from `p_game->input`. |
| `m_ui_draggable__dropped_handler__default` | `(UI_Element*, Game*, Graphics_Window*) -> void` | Default drop handler. Called when cursor releases the draggable. |

## 13.4 Agentic Workflow

### 13.4.1 Drag Lifecycle

1. **Cursor presses on element:** `UI_Manager` sets `UI_FLAGS__BIT_IS_BEING_HELD`.
2. **Cursor moves while held:** `UI_Manager` sets `UI_FLAGS__BIT_IS_BEING_DRAGGED` and invokes `m_ui_dragged_handler` each frame.
3. **Cursor releases:** `UI_Manager` invokes `m_ui_dropped_handler`. If dropped over a `Drop_Zone`, the drop zone's `m_ui_receive_drop_handler` is also invoked.

### 13.4.2 Implementing a Custom Drag Handler

    void my_drag_handler(
            UI_Element *p_this_draggable,
            Game *p_game,
            Graphics_Window *p_gfx_window) {
        // Optionally call the default to get cursor-following:
        m_ui_draggable__dragged_handler__default(
            p_this_draggable, p_game, p_gfx_window);
        // Add custom logic (e.g. snapping, bounds clamping)
    }

### 13.4.3 Preconditions

- `p_ui_draggable` must be non-null and previously allocated from a `UI_Manager`.
- Must also call `allocate_hitbox_for__ui_element` separately.

### 13.4.4 Notes

- The `// TODO: move to private header` comment on `initialize_ui_element_as__draggable` indicates this function may become non-public in a future refactor.
- The draggable union member is empty; all state is in the base `UI_Element` flags.

## 13.5 Header Guard

`UI_DRAGGABLE_H`
