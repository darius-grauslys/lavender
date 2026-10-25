get_ui_parent_or__child_with__dragged_handler — core/source/ui/ui_manager.c, lines 75-88

Searches a UI_Element (and its single child, if present) for one that has a dragged handler attached, returning the first match or NULL.

Pre-conditions:
1. p_ui_parent may be NULL; the function handles this gracefully by returning 0.
2. If p_ui_parent is non-NULL, it must point to a valid, fully-constructed UI_Element object.

Post-conditions:
1. Returns a pointer to the UI_Element that has a dragged handler — either p_ui_parent itself (if it has one) or p_ui_parent->p_child (if the child has one).
2. Returns 0 if p_ui_parent is NULL, if neither the parent nor its child has a dragged handler, or if the parent has no child.
3. No state is mutated; the input UI_Element tree is unmodified.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to find a UI_Element (parent or its immediate child) that has a dragged handler, so that the caller can invoke that handler. The implementation correctly:
  - Guards against NULL input (p_ui_parent == 0 → return 0).
  - Checks the parent first for a dragged handler (does_ui_element_have__dragged_handler(p_ui_parent)).
  - If the parent lacks a dragged handler, checks whether the parent even has a child (does_ui_element_have__child(p_ui_parent)) before attempting to access the child.
  - If the child exists, checks the child for a dragged handler (does_ui_element_have__dragged_handler(get_child_of__ui_element(p_ui_parent))).
  - Returns p_ui_parent->p_child only after confirming both that the child exists and that it has a dragged handler.
This matches the semantic intent exactly. The function is structurally identical to its sibling functions (get_ui_parent_or__child_with__clicked_handler, get_ui_parent_or__child_with__held_handler, get_ui_parent_or__child_with__receive_drop_handler), differing only in the handler type checked — confirming this is an intentional, consistent pattern.

Implementation Correctness:
Type compatibility — The parameter type (UI_Element *) matches the types expected by all helper functions (does_ui_element_have__dragged_handler, does_ui_element_have__child, get_child_of__ui_element). The return type (UI_Element *) is consistent with all return expressions (p_ui_parent, p_ui_parent->p_child, or 0/NULL). No implicit conversions or truncation occur.
Undefined behavior — No undefined behavior is present:
  - No null dereference: p_ui_parent is null-checked before any member access. The direct member access p_ui_parent->p_child on the return statement is only reached after does_ui_element_have__child(p_ui_parent) returned true, which internally verifies both p_ui_parent is non-NULL and p_ui_parent->p_child is non-NULL.
  - No out-of-bounds access: only struct member access is used, no array indexing.
  - No type punning: no casts or union misuse.
  - get_child_of__ui_element(p_ui_parent) is only called after does_ui_element_have__child(p_ui_parent) returned true, so p_ui_parent->p_child is guaranteed non-NULL at that point.
Validation — The function performs appropriate validation for its role: a NULL check on the input parameter and a child-existence check before accessing the child. This is sufficient; deeper validation (e.g., checking the child's parent pointer back-references the parent) is the caller's responsibility.

Side Effects:
No side effects. This is a pure query function — it reads from the UI_Element tree but does not modify any state, handlers, flags, or pointers.
