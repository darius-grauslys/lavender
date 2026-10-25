get_ui_parent_or__child_with__receive_drop_handler — core/source/ui/ui_manager.c

Searches the parent and its single child for a configured receive-drop handler and returns the first match, or NULL if neither has one.

Pre-conditions:
1. p_ui_parent may be NULL; if it is, the function returns 0 immediately.
2. If p_ui_parent is non-NULL, it must point to a valid UI_Element struct.

Post-conditions:
1. Returns p_ui_parent if it has a non-NULL m_ui_receive_drop_handler.
2. Returns p_ui_parent->p_child if the parent has a child and that child has a non-NULL m_ui_receive_drop_handler.
3. Returns 0 if p_ui_parent is NULL, if the parent has no child, or if neither the parent nor the child has a receive-drop handler.
4. No mutation of the UI_Element or any other state occurs.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully implements its intent: it checks the parent first, then the child, returning the first element that has a receive-drop handler. This matches the pattern of its sibling functions (get_ui_parent_or__child_with__clicked_handler, get_ui_parent_or__child_with__dragged_handler, get_ui_parent_or__child_with__held_handler). All checks and returns are correct and consistent with the semantic goal of finding a parent-or-child element capable of receiving a drop.

Implementation Correctness:
Type compatibility — p_ui_parent is UI_Element *, returned pointer is UI_Element *. The helper functions does_ui_element_have__receive_drop_handler, does_ui_element_have__child, and get_child_of__ui_element all accept and return the correct types. No implicit conversions or truncation.
Undefined behavior — no null dereference, no out-of-bounds access, no type punning, no broken pointer arithmetic. The null check on p_ui_parent (line 108) precedes all field accesses. The child existence check (line 112) precedes the child handler check (line 114) and the child return (line 116), so p_ui_parent->p_child is guaranteed non-NULL when dereferenced. The helper functions themselves also guard against NULL internally.
Validation — the null checks within this function and its helpers are appropriate for a low-level query function. No additional validation is needed.

Side Effects:
No side effects. The function is a pure query — it only reads from the UI_Element struct and its child, and returns a pointer without modifying any state.
