iterate_to_parent_of__ui_element — core/include/ui/ui_element.h

Advances a UI_Element iterator pointer to its parent, returning the element at the prior position.

Pre-conditions:
1. p_ui_element_ptr must be a non-null pointer to a UI_Element * (it is dereferenced immediately).
2. *p_ui_element_ptr may be NULL — this is handled gracefully and results in a NULL return.

Post-conditions:
1. If *p_ui_element_ptr was NULL on entry: returns 0 and leaves *p_ui_element_ptr unchanged.
2. If *p_ui_element_ptr was non-NULL on entry: returns the element that was pointed to, and sets *p_ui_element_ptr to that element's p_parent (which may be NULL if the element has no parent).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of iterating to a UI element's parent. It follows the identical pattern as its sibling functions iterate_to_next__ui_element and iterate_to_child_of__ui_element, differing only in which struct field is followed (p_parent vs p_next vs p_child). The volatile qualifier on the pointed-to pointer is appropriate for an iterator that may be used in contexts where the pointer value could change externally.

Implementation Correctness:
Type compatibility — parameter type UI_Element * volatile * matches usage; return type UI_Element * is correct; no implicit conversions or truncation.
Undefined behavior — no UB. The null check on *p_ui_element_ptr prevents null dereference before accessing ->p_parent. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — the null check on *p_ui_element_ptr is appropriate for this function's role as an iterator. Note that p_ui_element_ptr itself is not checked for NULL; this is consistent with the sibling iterator functions (iterate_to_next__ui_element, iterate_to_child_of__ui_element) and the codebase pattern where callers are expected to pass valid pointer-to-pointer arguments.

Side Effects:
Mutates *p_ui_element_ptr to point to the parent element (or NULL if the element has no parent). This is the function's primary observable effect.
