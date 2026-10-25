set_ui_button_as__toggleable_or__non_toggleable — core/include/ui/ui_button.h

Conditionally sets a UI button element as either toggleable or non-toggleable based on the boolean parameter, delegating to set_ui_button_as__toggleable or set_ui_button_as__non_toggleable respectively.

Pre-conditions:
1. p_ui_button must be a non-null pointer to a writable UI_Element.
2. p_ui_button must reference a UI_Element whose kind-of-ui-element is UI_Element_Kind__Button, since ui_button_flags is only valid in the UI_Button variant of the union within UI_Element.
3. is_toggleable_or__non_toggleable is any bool value (no range constraint).

Post-conditions:
1. If is_toggleable_or__non_toggleable is true: the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit is set in p_ui_button->ui_button_flags.
2. If is_toggleable_or__non_toggleable is false: both the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit and the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit are cleared in p_ui_button->ui_button_flags (the latter via set_ui_button_as__non_toggleable calling set_ui_button_as__untoggled).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent. When is_toggleable_or__non_toggleable is true, the function delegates to set_ui_button_as__toggleable, which sets the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit. When false, it delegates to set_ui_button_as__non_toggleable, which clears both the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit and the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit. The function name accurately describes this conditional behavior.

Implementation Correctness:
Type compatibility — UI_Element *p_ui_button matches the parameter type expected by both set_ui_button_as__toggleable and set_ui_button_as__non_toggleable. The bool parameter is used directly in a conditional, which is correct.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function assumes p_ui_button is non-null, which is consistent with the codebase pattern: all sibling inline functions (set_ui_button_as__toggleable, set_ui_button_as__non_toggleable, etc.) also perform no null check.
No validation is needed — this is a low-level inline helper. The caller is responsible for ensuring p_ui_button is valid and points to a UI_Button element.

Side Effects:
Mutates p_ui_button->ui_button_flags:
- When is_toggleable_or__non_toggleable is true: sets the UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE bit.
- When is_toggleable_or__non_toggleable is false: clears both UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE and UI_BUTTON_FLAGS__BIT_IS_TOGGLED bits.
