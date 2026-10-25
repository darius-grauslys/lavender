does_ui_element_have__parent — core/include/ui/ui_element.h

Returns true if the given UI_Element has a non-null parent pointer.

Pre-conditions:
1. p_ui_element may be NULL; the function safely handles this case.
2. If p_ui_element is non-null, it must point to a validly initialized UI_Element struct.

Post-conditions:
1. Returns true if and only if p_ui_element is non-null AND p_ui_element->p_parent is non-null.
2. Returns false if p_ui_element is NULL or if p_ui_element->p_parent is NULL.
3. No state is mutated; the function is a pure predicate.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the semantic intent of checking whether a UI_Element has a parent. The p_parent field (of type UI_Element *) is set by initialize_ui_element and set_parent_of__ui_element, and a non-null value indicates a parent relationship exists. The two-part check (null-guard on the element pointer, then truthiness check on p_parent) matches the pattern used by sibling functions does_ui_element_have__child and does_ui_element_have__next.

Implementation Correctness:
Type compatibility — p_ui_element is of type UI_Element * and p_parent is a pointer field (UI_Element *), so the truthiness check is well-defined. No implicit conversions or truncation occur.
Undefined behavior — none. The short-circuit evaluation of && ensures p_ui_element->p_parent is only dereferenced when p_ui_element is non-null, preventing null dereference. No pointer arithmetic, type punning, or out-of-bounds access.
Validation — the null check on p_ui_element is appropriate for a public query function that may receive NULL from callers. The caller is not required to pre-validate the pointer.

Side Effects:
No side effects. The function is a pure predicate that reads only the p_parent field of the pointed-to struct.
