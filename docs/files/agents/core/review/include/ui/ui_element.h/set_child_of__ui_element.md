set_child_of__ui_element — core/source/ui/ui_element.c

Sets the child pointer of a UI_Element to the given child UI_Element.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. p_ui_element__child may be NULL (to clear the child reference) or a valid pointer to another UI_Element.
3. p_ui_element__child must not be the same pointer as p_ui_element (self-reference is rejected to prevent infinite loops in traversal).

Post-conditions:
1. p_ui_element->p_child is set to p_ui_element__child.
2. If p_ui_element__child was equal to p_ui_element, the function returns early without modification and an error is logged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent: it assigns the child pointer of the given UI_Element. The self-reference guard prevents infinite loops during traversal, which is consistent with the comment in the code. The function mirrors the pattern used in set_parent_of__ui_element. No fields are omitted or reordered — it simply assigns p_ui_element->p_child.

Implementation Correctness:
Type compatibility — p_ui_element__child is of type UI_Element *, which matches the type of p_ui_element->p_child (UI_Element *). No implicit conversions or truncation.
No undefined behavior — the function dereferences p_ui_element to write p_child, which is safe as long as p_ui_element is non-null (a precondition). The self-reference check prevents creating a cycle that would cause infinite loops.
Validation — the self-reference check is appropriate for this function's role. NULL checks on p_ui_element are not performed, which is consistent with the codebase's convention for setter functions (the caller is responsible for providing a valid pointer).

Side Effects:
Mutates p_ui_element->p_child to point to p_ui_element__child. Additionally, if the self-reference guard triggers, debug_error is called to log a message. No other state is modified.
