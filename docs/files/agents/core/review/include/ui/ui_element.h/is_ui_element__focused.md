is_ui_element__focused — core/include/ui/ui_element.h

Returns whether the UI element currently has the focused bit set in its ui_flags.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element object.
2. The ui_flags field of the pointed-to UI_Element must be a valid UI_Flags__u16 value (uint16_t).

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_FOCUSED bit is set in p_ui_element->ui_flags, false otherwise.
2. The UI_Element object is not modified; the function is a pure query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly checks whether the focused bit (UI_FLAGS__BIT_IS_FOCUSED, defined as BIT(1) = 2) is set in the ui_flags bitmask. The bitwise AND operation correctly isolates the focused bit, and the explicit (bool) cast correctly converts any non-zero result to true and zero to false. This aligns with the companion setter functions set_ui_element_as__focused (which sets the bit via |=) and set_ui_element_as__NOT_focused (which clears the bit via &= ~), confirming the flag is used consistently.

Implementation Correctness:
Type compatibility — p_ui_element is typed as UI_Element *, and ui_flags is of type UI_Flags__u16 (uint16_t). UI_FLAGS__BIT_IS_FOCUSED is BIT(1) = ((1U) << 1), which is an unsigned int. The bitwise AND between uint16_t and unsigned int promotes to unsigned int, and the (bool) cast is well-defined. No implicit conversion issues or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access. The function reads a struct field through a valid pointer.
Validation — no validation is needed within this function. It is a low-level inline query; the caller is responsible for ensuring p_ui_element is valid, consistent with the pattern used by all sibling is_ui_element__* functions in this header.

Side Effects:
No side effects. The function is a pure, non-mutating query that reads p_ui_element->ui_flags and returns a boolean result. No state is modified.
