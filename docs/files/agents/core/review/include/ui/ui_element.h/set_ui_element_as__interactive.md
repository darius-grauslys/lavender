set_ui_element_as__interactive — core/include/ui/ui_element.h

Clears the `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit in the `ui_flags` field of the given `UI_Element`, making the element interactive (i.e., eligible for user interaction).

Pre-conditions:
1. `p_ui_element` must be a non-null pointer to a valid, writable `UI_Element` struct.

Post-conditions:
1. The `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit (BIT(2)) in `p_ui_element->ui_flags` is cleared (set to 0).
2. All other bits in `p_ui_element->ui_flags` are preserved unchanged.
3. After return, `is_ui_element__non_interactive(p_ui_element)` will return `false`.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly clears the `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit, which is the inverse of `set_ui_element_as__non_interactive` (which sets that same bit via `|=`). The comment block above `set_ui_element_as__non_interactive` (lines 472-480) clarifies that "Non-interactive will prevent user interaction but still allow for composing." Clearing this bit restores interactive behavior, which is exactly the semantic intent of the function name. The implementation matches the intent: no other flags are affected, and the operation is the standard bitwise AND with complement (`&= ~FLAG`) idiom used consistently across all other "NOT" / "clear" setters in this file (e.g., `set_ui_element_as__NOT_focused`, `set_ui_element_as__disabled`, `set_ui_element_as__dropped`, `set_ui_element_as__NOT_being_dragged`).

Implementation Correctness:
- Type compatibility: `ui_flags` is of type `UI_Flags__u16` (typedef'd as `uint16_t`). `UI_FLAGS__BIT_IS_NON_INTERACTIVE` is `BIT(2)` which expands to `((1U) << (2))` — an `unsigned int` value of `4`. The `~UI_FLAGS__BIT_IS_NON_INTERACTIVE` expression produces an `unsigned int` mask. The compound assignment `ui_flags &= ~UI_FLAGS__BIT_IS_NON_INTERACTIVE` performs a bitwise AND between a `uint16_t` lvalue and an `unsigned int` rvalue, with the result converted back to `uint16_t`. This is well-defined and no precision is lost, as the mask only affects the lower 16 bits relevant to `ui_flags`. No implicit conversion issues or truncation occur.
- Undefined behavior: No pointer arithmetic, no null dereference (consistent with all sibling setters — null-checking is the caller's responsibility), no type punning, no out-of-bounds access. The function only accesses the `ui_flags` member of the struct.
- Validation: No validation is performed, which is appropriate for this low-level inline setter function. This is consistent with every other flag setter in the file. The caller is responsible for ensuring `p_ui_element` is a valid pointer.

Side Effects:
The function mutates `p_ui_element->ui_flags` by clearing the `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit. No other fields of the struct are modified, and no other objects are affected.
