set_ui_element_as__non_interactive — core/include/ui/ui_element.h

Sets the `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit in the `ui_flags` field of a `UI_Element`, marking it as non-interactive (composing-only, no user input).

Pre-conditions:
1. `p_ui_element` must be a non-null pointer to a writable `UI_Element` object.
2. The `ui_flags` field must be a valid `UI_Flags__u16` (uint16_t) value.

Post-conditions:
1. The `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit is set in `p_ui_element->ui_flags`, preserving all other flag bits.
2. After return, `is_ui_element__non_interactive(p_ui_element)` will return true.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent: it marks a UI element as non-interactive by setting the appropriate flag bit. The documentation comment confirms this intent — "Non-interactive will prevent user interaction but still allow for composing." The bitwise OR assignment (`|=`) correctly sets only the target bit without disturbing other flags. This is consistent with the pattern used by all sibling setter functions in this file (e.g., `set_ui_element_as__focused`, `set_ui_element_as__enabled`). This is a simple setter, not an initialization/reset function; it does not perform resource setup (Lavender-style initialization ≠ RAII).

Implementation Correctness:
Type compatibility — `p_ui_element->ui_flags` is of type `UI_Flags__u16` (uint16_t), and `UI_FLAGS__BIT_IS_NON_INTERACTIVE` is defined as `BIT(2)`, which is a uint16_t-compatible constant. The bitwise OR operation is type-safe with no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (null-checking is the caller's responsibility, consistent with all other inline setters in this file), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline flag setter. The caller is responsible for ensuring `p_ui_element` is valid, matching the convention of every other `set_ui_element_as__*` function in this header.

Side Effects:
Mutates `p_ui_element->ui_flags` by setting the `UI_FLAGS__BIT_IS_NON_INTERACTIVE` bit. No other state is modified.
