is_ui_element__being_dragged — core/include/ui/ui_element.h

Checks whether the UI element is currently being dragged by testing the `UI_FLAGS__BIT_IS_BEING_DRAGGED` bit in its `ui_flags` field.

Pre-conditions:
1. `p_ui_element` must be a non-null pointer to a valid `UI_Element` object.

Post-conditions:
1. Returns `true` if the `UI_FLAGS__BIT_IS_BEING_DRAGGED` bit (bit 4) is set in `p_ui_element->ui_flags`; returns `false` otherwise.
2. No mutation of the `UI_Element` occurs — the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly checks whether the "being dragged" flag is set by performing a bitwise AND between `p_ui_element->ui_flags` (of type `UI_Flags__u16`, i.e., `uint16_t`) and `UI_FLAGS__BIT_IS_BEING_DRAGGED` (defined as `BIT(4)`, i.e., `((1U) << 4)`). The result is explicitly cast to `bool`, which correctly converts any non-zero value to `true` and zero to `false`. This matches the semantic intent of a flag-checking predicate.

Implementation Correctness:
Type compatibility — `ui_flags` is `uint16_t` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` is `unsigned int` (from the `BIT` macro). The bitwise AND undergoes standard integer promotion (`uint16_t` → `int`, then `int & unsigned int` → `unsigned int`), and the result is explicitly cast to `bool`. No truncation or data loss occurs. This is the same pattern used by all sibling flag-checking functions in the file (e.g., `is_ui_element__enabled`, `is_ui_element__focused`, `is_ui_element__being_held`, `is_ui_element__snapped_x_or_y_axis`).
No undefined behavior — no pointer arithmetic, no null dereference (assuming non-null pointer per pre-condition), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline accessor. The caller is responsible for ensuring `p_ui_element` is valid.

Side Effects:
No side effects — the function reads from the pointed-to struct but does not modify it or any other state.
