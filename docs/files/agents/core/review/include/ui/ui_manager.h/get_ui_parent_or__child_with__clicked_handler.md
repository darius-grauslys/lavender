get_ui_parent_or__child_with__clicked_handler — core/source/ui/ui_manager.c

Searches a UI_Element and its immediate child for a non-null clicked handler, returning the first match.

Pre-conditions:
1. p_ui_parent may be NULL — the function handles this gracefully by returning NULL.
2. If p_ui_parent is non-NULL, it must point to a valid UI_Element struct.
3. The UI_Element struct's p_child field, if present, must point to a valid UI_Element or be NULL.

Post-conditions:
1. If p_ui_parent is NULL, returns NULL.
2. If p_ui_parent has a non-null m_ui_clicked_handler, returns p_ui_parent.
3. If p_ui_parent has no clicked handler but has a child with a non-null m_ui_clicked_handler, returns p_ui_parent->p_child.
4. If neither p_ui_parent nor its child has a clicked handler, returns NULL.
5. No state is mutated; the function is pure (read-only).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements its semantic intent: find the first element (parent or immediate child) that possesses a non-null clicked handler. The logic checks the parent first, then falls back to the child, returning the matching element or NULL. This matches the pattern used by the sibling functions get_ui_parent_or__child_with__dragged_handler, get_ui_parent_or__child_with__held_handler, and get_ui_parent_or__child_with__receive_drop_handler, which follow the same structure.

Implementation Correctness:
Type compatibility — p_ui_parent is UI_Element *, matching the parameter type. Return type is UI_Element *, consistent with all return paths. No implicit conversions or truncation.
Undefined behavior — no null dereference occurs. The function checks p_ui_parent for null (line 62) before any dereference. On line 66, does_ui_element_have__child(p_ui_parent) checks p_ui_parent->p_child for null before get_child_of__ui_element(p_ui_parent) is called on line 68-69. The returned p_ui_parent->p_child on line 70 is guaranteed non-null because it was verified by does_ui_element_have__child on line 66. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — appropriate for the function's role. The function is a low-level query helper; it performs its own null checks defensively, which is consistent with the codebase style. The caller (poll_ui_manager__update_for__clicked_and_dropped) additionally checks the returned pointer for null before invoking the handler.

Side Effects:
No side effects — the function reads from the UI_Element struct and its child pointer but does not modify any state. It returns a pointer to an existing element without altering any struct fields.
