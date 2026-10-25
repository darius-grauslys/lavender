set_ui_button_as__toggled — core/include/ui/ui_button.h

Sets the toggled bit in the UI element's button flags.

Pre-conditions:
1. p_ui_button must be a non-null pointer to a valid UI_Element object.
2. The UI_Element must have been initialized as a button (i.e., the_kind_of_ui_element__this_is must be a button kind), so that the ui_button_flags field in the union is the active member.

Post-conditions:
1. The UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit in p_ui_button->ui_button_flags is set to 1.
2. All other bits in p_ui_button->ui_button_flags remain unchanged.
3. The function returns void; no return value is produced.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly sets the IS_TOGGLED bit using a bitwise OR with UI_BUTTON_FLAGS__BIT_IS_TOGGLED. This matches the semantic intent of marking the button as toggled. The implementation is consistent with the sibling function set_ui_button_as__untoggled, which clears the same bit using a bitwise AND with the complement.

Implementation Correctness:
Type compatibility — p_ui_button is UI_Element *, and ui_button_flags is UI_Button_Flags__u8 (uint8_t). The bitwise OR operation with UI_BUTTON_FLAGS__BIT_IS_TOGGLED (a BIT macro result, which is an integer) is type-compatible and stored back into the uint8_t field without truncation issues.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access.
No validation is performed inside the function — this is appropriate for a low-level inline setter. The caller is responsible for ensuring p_ui_button is valid and is a button-type UI_Element.

Side Effects:
Mutates p_ui_button->ui_button_flags by setting the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit.
