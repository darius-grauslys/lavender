initialize_ui_element_as__slider — core/source/ui/ui_slider.c

Initializes a UI_Element as a slider by delegating to initialize_ui_element, then configuring slider-specific handlers, axis snapping, and spanning length.

Pre-conditions:
1. p_ui_slider must be a non-null pointer to a writable UI_Element object.
2. spanning_length__3i32 is any Vector__3i32; represents the full travel range of the slider along its snapped axis.
3. m_ui_dragged_handler is a valid function pointer of type m_UI_Dragged (may be NULL; no validation is performed, consistent with the codebase pattern for low-level init functions).
4. is_snapped_x_or_y__axis is a boolean: true snaps the slider to the X axis, false snaps to the Y axis.
5. The UI_Element's p_parent, p_child, p_next, and ui_flags fields may hold prior linkage and flag state; these are read and re-passed to initialize_ui_element to preserve structural relationships. This is the established pattern across all initialize_ui_element_as__* functions (e.g., initialize_ui_element_as__button).

Post-conditions:
1. p_ui_slider is mutated such that the_kind_of_ui_element__this_is is set to UI_Element_Kind__Slider.
2. The m_ui_dragged_handler is set to the provided m_ui_dragged_handler.
3. The m_ui_transformed_handler is set to m_ui_slider__transformed_handler__default (overriding the default set by initialize_ui_element).
4. The m_ui_dispose_handler is set to m_ui_slider__dispose_handler__gfx_window__default (overriding the default set by initialize_ui_element).
5. The m_ui_compose_handler remains m_ui_element__compose_handler__default (set by initialize_ui_element, not overridden).
6. The m_ui_clicked_handler, m_ui_dropped_handler, m_ui_receive_drop_handler, m_ui_held_handler, and m_ui_typed_handler are all NULL (zeroed by the memset in initialize_ui_element).
7. The ui_flags field preserves its prior value (re-set by initialize_ui_element), with the snapped axis bit set or cleared per is_snapped_x_or_y__axis.
8. The slider__spanning_length__3i32 field is set to the provided spanning_length__3i32.
9. The slider__distance__u32 field is zeroed (by the memset in initialize_ui_element), representing the slider's initial position at distance 0.
10. The serialization header (_serialization_header) is preserved (not zeroed by initialize_ui_element).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of initializing a UI_Element as a slider. The function follows the established Lavender pattern of "initialization as cleanup/reset to initial conditions" (not RAII). It delegates to initialize_ui_element, which performs a memset to zero the struct (except the serialization header) and then restores linkage pointers (p_parent, p_child, p_next), the element kind, and ui_flags. This is consistent with the codebase convention seen in initialize_ui_element_as__button and other similar init functions.

The slider-specific union members (slider__spanning_length__3i32 and slider__distance__u32) are properly handled: spanning_length is explicitly set, and distance is implicitly zeroed by the memset. No struct member is omitted or reordered — the function relies on initialize_ui_element to handle the base struct initialization, then layers on slider-specific configuration.

Implementation Correctness:
Type compatibility — every parameter type matches its target exactly:
- Vector__3i32 spanning_length__3i32 → slider__spanning_length__3i32 (Vector__3i32) ✓
- m_UI_Dragged m_ui_dragged_handler → set_ui_element__dragged_handler parameter (m_UI_Dragged) ✓
- bool is_snapped_x_or_y__axis → set_ui_element_as__snapped_x_axis / set_ui_element_as__snapped_y_axis (both take UI_Element*) ✓
- UI_Element *p_ui_slider → all setter functions (UI_Element*) ✓

No undefined behavior — no null dereference (caller responsibility per codebase convention), no broken pointer arithmetic, no type punning, no out-of-bounds access. The function reads p_parent, p_child, p_next, and ui_flags from the struct before initialize_ui_element's memset, but this is intentional and matches the pattern used by all sibling init functions.

Validation — no validation is performed on p_ui_slider (null check), which is consistent with the codebase convention for low-level initialization functions. initialize_ui_element itself also performs no null check. The caller is responsible for ensuring p_ui_slider is valid.

Side Effects:
Mutates the UI_Element struct at p_ui_slider:
- Resets the struct via initialize_ui_element (memset to 0 except serialization header, then restores p_parent/p_child/p_next/kind/ui_flags).
- Overrides the transformed handler and dispose handler with slider-specific defaults.
- Sets the dragged handler to the provided value.
- Sets or clears the snapped axis flag in ui_flags.
- Sets slider__spanning_length__3i32 to the provided value.
- Zeroes slider__distance__u32 (via the memset).
