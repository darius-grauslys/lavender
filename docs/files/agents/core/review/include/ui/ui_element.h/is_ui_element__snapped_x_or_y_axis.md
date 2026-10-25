is_ui_element__snapped_x_or_y_axis — core/include/ui/ui_element.h

Checks the UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS bit of a UI_Element's flags to determine its axis-snapping state.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid UI_Element. No null check is performed (consistent with all other is_ui_element__* flag-checking functions in the same file, e.g., is_ui_element__enabled, is_ui_element__focused).

Post-conditions:
1. Returns true if the UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS bit is set (element is snapped to the X axis).
2. Returns false if the UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS bit is cleared (element is snapped to the Y axis).
3. The pointed-to UI_Element is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function is the getter counterpart to the pair of setters set_ui_element_as__snapped_x_axis (sets the bit) and set_ui_element_as__snapped_y_axis (clears the bit). The single bit UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS acts as a one-bit selector between two snapped states:
  - Bit set (1) → snapped to X axis
  - Bit cleared (0) → snapped to Y axis

The getter correctly returns the bit's value, which is symmetric with set_ui_element__snapped_state(bool is_snapped_x_or_y__axis): when the parameter is true it calls set_ui_element_as__snapped_x_axis (sets bit), and when false it calls set_ui_element_as__snapped_y_axis (clears bit). The getter returns true for X and false for Y, matching this convention exactly.

Usage in the codebase confirms this semantic: in ui_slider.c and ui_slider.h, the return value is used as a ternary condition to select between X-axis logic (e.g., cursor x-coordinate, width) and Y-axis logic (e.g., cursor y-coordinate, height). For example, in m_ui_slider__dragged_handler__default, is_ui_element__snapped_x_or_y_axis(p_this_draggable) is true → use x-coordinate and width; false → use y-coordinate and height. This is consistent with the setter functions.

The function name "is_ui_element__snapped_x_or_y_axis" uses "x_or_y" to name the single bit field that encodes the axis selection (not a logical OR of two independent booleans). The implementation faithfully reads this bit.

Implementation Correctness:
Type compatibility — p_ui_element->ui_flags is UI_Flags__u16 (uint16_t). UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS is BIT(5) = ((1U) << 5), which is unsigned int. The bitwise AND promotes uint16_t to unsigned int (implicit, widening conversion — no data loss). The result is explicitly cast to bool, which correctly yields true for any nonzero value and false for zero. No implicit conversions or truncation occur that would affect correctness.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access.
No validation needed — consistent with all sibling flag-checking inline functions in this header. The caller is responsible for passing a valid pointer.

Side Effects:
No side effects. The function is a pure read operation on the UI_Element's flags field.
