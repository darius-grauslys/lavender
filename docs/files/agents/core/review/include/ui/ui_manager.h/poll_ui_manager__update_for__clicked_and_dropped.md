# `poll_ui_manager__update_for__clicked_and_dropped`

**File of origin:** `core/source/ui/ui_manager.c`

## Semantic

Handles click-release and drop events for UI elements managed by the `UI_Manager`. When a click is released, if the focused element is currently being dragged, a drop is processed; otherwise, the clicked handler of the focused element (or its parent/child) is invoked.

## Pre-conditions

1. `p_ui_manager` must be non-null. It is dereferenced by `detect_focus__strictly_under_cursor_in__ui_manager` and `handle_drop_in__ui_manager`.
2. `p_game` must be non-null. It is passed to `detect_focus__strictly_under_cursor_in__ui_manager`, `handle_drop_in__ui_manager`, and the invoked handlers.
3. `p_graphics_window` must be non-null. It is passed to `handle_drop_in__ui_manager` and the invoked handlers.
4. The caller (`poll_ui_manager__update`) must have already established that `is_input__click_released(p_input)` is true, ensuring this function is only invoked on a click-release event.
5. `p_ui_manager` must have been properly initialized (allocation of `pM_ui_element_pool`, `pM_ptr_array_of__ui_elements`, etc. completed).

## Post-conditions

1. If no UI element is detected under the cursor, the function returns immediately with no side effects.
2. If the focused element is being dragged, `handle_drop_in__ui_manager` is invoked, which:
   - Clears the `IS_BEING_HELD` and `IS_BEING_DRAGGED` flags on the element via `set_ui_element_as__dropped`.
   - If the element has a dropped handler, finds a receiving element under the focused element and invokes its `m_ui_receive_drop_handler`, then invokes the focused element's `m_ui_dropped_handler`.
   - If the element has no dropped handler, drops the UI element focus for the manager.
3. If the focused element is not being dragged, `get_ui_parent_or__child_with__clicked_handler` is called to find an element (the focused element itself or its child) that has a non-null `m_ui_clicked_handler`. If found, that element's `m_ui_clicked_handler` is invoked with the focused element, game, and graphics window. If no such element is found, the function returns with no side effects.
4. The function does not return a value.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. When a click is released:

- If the element was being dragged (drag in progress), it is treated as a drop operation, delegating to `handle_drop_in__ui_manager`. This correctly models the drag-then-release → drop interaction.
- If the element was not being dragged, it is treated as a simple click, and the clicked handler is invoked on the appropriate element (the focused element or its child).

The control flow correctly distinguishes between drop and click scenarios, and the delegation to helper functions is appropriate.

## Implementation Correctness

- **Type compatibility:** The `m_ui_clicked_handler` field is of type `m_UI_Clicked`, which is `void (*)(UI_Element*, Game*, Graphics_Window*)`. The invocation passes `(p_ui_element__focused, p_game, p_graphics_window)` — all types match exactly with no implicit conversions.
- **Null safety:** `p_ui_element__focused` is checked for null after `detect_focus__strictly_under_cursor_in__ui_manager` and after `get_ui_parent_or__child_with__clicked_handler`. The `get_ui_parent_or__child_with__clicked_handler` function internally calls `does_ui_element_have__clicked_handler`, which checks both that the element pointer is non-null and that the handler pointer is non-null before returning the element. Therefore, the `m_ui_clicked_handler` invocation is guaranteed to be on a non-null handler.
- **No undefined behavior:** No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. All pointer dereferences are guarded by null checks.
- **Validation:** The function relies on its caller to ensure `p_ui_manager`, `p_game`, and `p_graphics_window` are valid. Internal null checks are performed on `p_ui_element__focused`. This is appropriate for the function's role as an internal poll/update handler.

## Side Effects

- When a drop is processed: `handle_drop_in__ui_manager` mutates the focused UI element's flags (clears `IS_BEING_HELD` and `IS_BEING_DRAGGED`), may drop the manager's focus, and invokes `m_ui_receive_drop_handler` and `m_ui_dropped_handler` on the appropriate elements.
- When a click is processed: invokes `m_ui_clicked_handler` on the resolved UI element, which may have arbitrary side effects depending on the handler implementation.
- Both paths may indirectly modify `p_ui_manager->p_ui_element__focused` and related state through the called functions.
