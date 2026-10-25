set_ui_button_as__toggled_or__not_toggled — core/include/ui/ui_button.h, lines 60-68

Conditionally sets or clears the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit on a UI_Element's ui_button_flags field, based on a boolean parameter.

Pre-conditions:
1. p_ui_button must be a non-null pointer to a valid, writable UI_Element object. (The pointer is dereferenced indirectly via the callee functions set_ui_button_as__toggled and set_ui_button_as__untoggled.)
2. is_toggled_or__not_toggled is a bool and may be either true or false with no additional constraints.

Post-conditions:
1. If is_toggled_or__not_toggled was true, the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit in p_ui_button->ui_button_flags is set (bit value 1).
2. If is_toggled_or__not_toggled was false, the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit in p_ui_button->ui_button_flags is cleared (bit value 0).
3. All other bits in ui_button_flags are unaffected.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the semantic intent of the function. When is_toggled_or__not_toggled is true, it delegates to set_ui_button_as__toggled, which performs p_ui_button->ui_button_flags |= UI_BUTTON_FLAGS__BIT_IS_TOGGLED. When false, it delegates to set_ui_button_as__untoggled, which performs p_ui_button->ui_button_flags &= ~UI_BUTTON_FLAGS__BIT_IS_TOGGLED. Both callees operate on the correct field (ui_button_flags, of type UI_Button_Flags__u8, i.e., uint8_t) and the correct flag bit (UI_BUTTON_FLAGS__BIT_IS_TOGGLED). No semantic drift is present.

Implementation Correctness:
Type compatibility — the is_toggled_or__not_toggled parameter is of type bool, which is the correct type for a boolean branch condition. The p_ui_button parameter is UI_Element *, matching the callee signatures exactly. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (the pointer is passed through to callees that handle it), no type punning, no out-of-bounds access. The function body is a simple if/else with no arithmetic.
Validation — no validation is performed within this function. This is appropriate for a low-level inline setter dispatcher. The caller is responsible for ensuring p_ui_button is a valid, non-null pointer.

Side Effects:
Mutates p_ui_button->ui_button_flags by setting or clearing the UI_BUTTON_FLAGS__BIT_IS_TOGGLED bit, depending on the value of is_toggled_or__not_toggled. No other state is modified.
