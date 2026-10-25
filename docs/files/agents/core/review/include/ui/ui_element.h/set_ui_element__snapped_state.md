set_ui_element__snapped_state — core/include/ui/ui_element.h

Conditionally sets or clears the UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS bit on a UI_Element to snap it to the X axis (true) or Y axis (false).

Pre-conditions:
1. p_ui_slider must be a non-null pointer to a writable UI_Element object.
2. is_snapped_x_or_y__axis is a bool: true means snap to the X axis (set bit), false means snap to the Y axis (clear bit).

Post-conditions:
1. If is_snapped_x_or_y__axis is true, UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS is set in p_ui_slider->ui_flags.
2. If is_snapped_x_or_y__axis is false, UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS is cleared in p_ui_slider->ui_flags.
3. No return value (void).

Correctness Verdict: Correct

Semantic Alignment:
The function delegates to set_ui_element_as__snapped_x_axis (which sets the bit) when the parameter is true, and to set_ui_element_as__snapped_y_axis (which clears the bit) when false. This is consistent with the single-bit encoding of UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS (BIT(5)), where set = X axis and clear = Y axis. The query function is_ui_element__snapped_x_or_y_axis returns true when the bit is set (X axis), confirming the convention. All callers in ui_slider.c (e.g., m_ui_slider__dragged_handler__default, m_ui_slider__transformed_handler__default, get_percentage_i32F20_from__ui_slider) use the same true=X, false=Y convention, so the implementation fulfills its semantic intent.

Implementation Correctness:
Type compatibility — p_ui_slider is UI_Element *, matching the parameter type of both callee functions (set_ui_element_as__snapped_x_axis and set_ui_element_as__snapped_y_axis). is_snapped_x_or_y__axis is bool, used directly as a condition in the if statement — no implicit conversion or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility per codebase convention), no type punning, no out-of-bounds access.
Validation — no null check is performed, consistent with all other set_ui_element_as__* inline functions in this file. The caller is responsible for ensuring p_ui_slider is valid.

Side Effects:
Mutates p_ui_slider->ui_flags by setting or clearing the UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS bit (BIT(5)).
