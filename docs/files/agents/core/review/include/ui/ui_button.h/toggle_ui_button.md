toggle_ui_button — core/include/ui/ui_button.h

Toggles the UI_BUTTON_FLAGS__BIT_IS_TOGGLED flag on a UI_Element's ui_button_flags and returns the resulting toggle state.

Pre-conditions:
1. p_ui_button must be a non-null pointer to a writable UI_Element whose union variant is active as a UI_Button (i.e., the_kind_of_ui_element__this_is designates a button), so that the ui_button_flags field is the meaningful union member.
2. The ui_button_flags field must be initialized to a valid UI_Button_Flags__u8 value (typically UI_BUTTON_FLAGS__NONE or a combination of UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE and UI_BUTTON_FLAGS__BIT_IS_TOGGLED).

Post-conditions:
1. The UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit in p_ui_button->ui_button_flags is flipped: set if it was previously clear, cleared if it was previously set.
2. All other bits in ui_button_flags (including UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE) are left unchanged.
3. The return value is the new toggle state: true if the button is now toggled, false if it is now untoggled.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of toggling a button's toggled state. It reads the current toggle state via is_ui_button__toggled, negates it to compute the target state, applies that state via set_ui_button_as__toggled_or__not_toggled, and returns the new state. The logic is sound: if the button was toggled it becomes untoggled (returns false), and if it was untoggled it becomes toggled (returns true).

Implementation Correctness:
Type compatibility — is_ui_button__toggled returns bool, the negation (!) yields bool, which is stored in a bool local and passed to set_ui_button_as__toggled_or__not_toggled (which accepts bool) and returned as bool. All types match exactly with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (the function trusts the caller to pass a valid pointer, consistent with all other inline helpers in this header), no type punning, no out-of-bounds access. The union access to ui_button_flags is valid as long as the UI_Button variant is the active member (caller responsibility).
No validation is needed — this is a low-level inline bit-toggle helper. The caller is responsible for ensuring p_ui_button is valid and that the UI_Button union variant is active.

Side Effects:
Mutates p_ui_button->ui_button_flags by flipping the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit. No other state is modified.
