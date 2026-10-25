set_ui_element_as__NOT_being_dragged — core/include/ui/ui_element.h

Clears the "being dragged" flag on a UI element, marking it as no longer being dragged.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, writable UI_Element object (the function dereferences the pointer without null checking).

Post-conditions:
1. The UI_FLAGS__BIT_IS_BEING_DRAGGED bit in p_ui_element->ui_flags is cleared (set to 0).
2. All other bits in p_ui_element->ui_flags remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly clears the "being dragged" flag using bitwise AND-assignment with the complement of UI_FLAGS__BIT_IS_BEING_DRAGGED. This matches the semantic intent of marking a UI element as no longer being dragged. The implementation is consistent with the sibling setter set_ui_element_as__being_dragged, which sets the same bit via OR-assignment. No fields are omitted or reordered; this function modifies only a single bit flag.

Implementation Correctness:
Type compatibility — ui_flags is of type UI_Flags__u16 (a u16), and UI_FLAGS__BIT_IS_BEING_DRAGGED is a u16 bit constant. The expression ~UI_FLAGS__BIT_IS_BEING_DRAGGED produces an int in C, but the bitwise AND-assignment (&=) truncates the result back to u16 when stored into the u16 field, which is well-defined behavior. No implicit conversions or truncation issues arise from this pattern.
No undefined behavior — no pointer arithmetic, no null dereference (assuming caller passes a valid pointer), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline flag setter. The caller is responsible for ensuring p_ui_element is valid. This is consistent with the pattern used by all sibling flag setters in this file (e.g., set_ui_element_as__NOT_focused, set_ui_element_as__disabled).

Side Effects:
Mutates p_ui_element->ui_flags by clearing the UI_FLAGS__BIT_IS_BEING_DRAGGED bit. All other bits are preserved.
