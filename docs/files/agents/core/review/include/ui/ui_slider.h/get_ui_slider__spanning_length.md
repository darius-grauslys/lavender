get_ui_slider__spanning_length — core/include/ui/ui_slider.h

Returns the spanning length (as a Vector__3i32) of a UI slider element by directly accessing the slider__spanning_length__3i32 field from the UI_Element struct's union.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid, initialized UI_Element struct.
2. The UI_Element must be of kind UI_Element_Kind__Slider for the union member access to be well-defined. However, this is NOT validated by the function (see TODO comment in source).

Post-conditions:
1. Returns the value of p_ui_element->slider__spanning_length__3i32 (a Vector__3i32) unmodified.
2. No mutation of the UI_Element or any other state occurs.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to return the spanning length of a slider UI element. The implementation correctly accesses the slider__spanning_length__3i32 field, which is the right field for a slider. However, the function fails to validate that the UI_Element is actually of kind UI_Element_Kind__Slider before accessing this union member. This is inconsistent with other functions in the same file (e.g., get_percentage_i32F20_from__ui_slider, get_offset_from__ui_slider_percentage, set_ui_slider_at__this_distance_u32), all of which perform a debug-mode check via is_ui_element_of__this_kind(). Without this validation, accessing the union member on a non-slider UI_Element constitutes undefined behavior. The TODO comment in the source ("//TODO: validate ui_element enum") acknowledges this gap.

Implementation Correctness:
Type compatibility — the return type (Vector__3i32) matches the field type (Vector__3i32) exactly. No implicit conversions or truncation.
Undefined behavior — accessing the slider__spanning_length__3i32 union member when the UI_Element is not of kind UI_Element_Kind__Slider is undefined behavior. The function does not guard against this, unlike its sibling functions in ui_slider.h.
Validation — validation is absent but would be appropriate here, as the function accesses a type-specific union member. The debug-time validation pattern used elsewhere in the file (checking is_ui_element_of__this_kind()) is the correct approach and should be applied.

Side Effects:
No side effects — this is a pure accessor function that only reads from the UI_Element struct.
