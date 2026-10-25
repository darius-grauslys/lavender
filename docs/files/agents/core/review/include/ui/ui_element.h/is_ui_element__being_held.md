is_ui_element__being_held — core/include/ui/ui_element.h

Checks whether the UI_FLAGS__BIT_IS_BEING_HELD flag bit is set on a UI_Element.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, accessible UI_Element struct. No null-check is performed; this is the caller's responsibility (consistent with all sibling query functions in this header).

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_BEING_HELD bit (BIT(3) of ui_flags) is set; returns false otherwise.
2. The pointed-to UI_Element is not mutated; this is a read-only query.

Correctness Verdict: Correct

Semantic Alignment:
The implementation directly tests the UI_FLAGS__BIT_IS_BEING_HELD flag bit via a bitwise AND and casts the result to bool. This matches the semantic intent of determining whether the UI element is currently being held. The function follows the exact same pattern used by every other flag-query function in this header (e.g., is_ui_element__enabled, is_ui_element__focused, is_ui_element__being_dragged), all of which use the form `(bool)(p_ui_element->ui_flags & UI_FLAGS__BIT_*)`.

Implementation Correctness:
- Type compatibility: p_ui_element->ui_flags is of type UI_Flags__u16 (typedef'd to uint16_t). UI_FLAGS__BIT_IS_BEING_HELD is defined as BIT(3), which expands to ((1U) << 3), an unsigned int expression. The bitwise AND promotes the uint16_t operand to unsigned int, and the result is explicitly cast to bool. This is safe and well-defined; no truncation or data loss occurs.
- Undefined behavior: No pointer arithmetic, no null dereference (assumes valid pointer per caller responsibility), no type punning, no out-of-bounds access. The bitwise AND and bool cast are standard C operations with well-defined semantics.
- Validation: No validation is performed inside the function, which is appropriate for a low-level inline query function. This is consistent with the design of all sibling functions in this header (e.g., is_ui_element__enabled, is_ui_element__focused, is_ui_element__non_interactive, is_ui_element__being_dragged), none of which perform null checks. The caller is responsible for ensuring the pointer is valid.

Side Effects:
No side effects. The function reads the ui_flags field of the pointed-to UI_Element and returns a boolean value. No state is modified.
