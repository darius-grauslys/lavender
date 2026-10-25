is_ui_element__non_interactive — core/include/ui/ui_element.h

Returns true if the UI element's non-interactive flag bit is set; false otherwise.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, writable UI_Element object. No null check is performed; this is consistent with all sibling is_ui_element__* query functions in the same header, which also assume a valid pointer.
2. p_ui_element->ui_flags is a UI_Flags__u16 (uint16_t) holding the element's bitflags.

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_NON_INTERACTIVE bit (BIT(2)) is set in p_ui_element->ui_flags, false otherwise.
2. The UI_Element struct is not modified; the function is a pure read query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements its semantic intent: querying whether the UI element has been marked as non-interactive. The flag UI_FLAGS__BIT_IS_NON_INTERACTIVE (BIT(2)) is set by set_ui_element_as__non_interactive(...) and cleared by set_ui_element_as__interactive(...). The inline documentation in the header confirms the semantic distinction: "Non-interactive will prevent user interaction but still allow for composing." The bitwise AND with the flag constant and cast to bool correctly tests this single bit. The implementation is consistent with all sibling query functions (is_ui_element__enabled, is_ui_element__focused, is_ui_element__being_held, etc.).

Implementation Correctness:
Type compatibility — p_ui_element->ui_flags is UI_Flags__u16 (uint16_t). UI_FLAGS__BIT_IS_NON_INTERACTIVE is BIT(2) which expands to ((1U) << 2), an unsigned int. The bitwise AND promotes the uint16_t operand to unsigned int (which can represent all uint16_t values), so no truncation occurs. The (bool) cast then converts any non-zero result to true and zero to false. No implicit conversions or truncation issues.
Undefined behavior — none. No pointer arithmetic, no null dereference (caller must provide valid pointer), no type punning, no out-of-bounds access.
Validation — no validation is needed for this low-level flag query. This is a static inline accessor; the caller is responsible for ensuring p_ui_element is valid, consistent with the codebase pattern.

Side Effects:
No side effects — the function reads p_ui_element->ui_flags and returns a bool. No state is mutated.
