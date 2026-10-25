m_ui_slider__dragged_handler__gfx_window__default — core/source/ui/ui_slider.c, lines 208-250

Computes the slider's positional offset based on cursor drag, then moves the graphics window owned by the slider from its old position to its new position.

Pre-conditions:
1. p_this_draggable must be a non-null pointer to a UI_Element of kind UI_Element_Kind__Slider.
2. p_game must be a non-null pointer to a valid Game object with an initialized gfx_context.
3. p_graphics_window must be a non-null pointer to a Graphics_Window with an allocated hitbox manager.
4. The slider must have a valid spanning_length__3i32 set (non-zero in the snapped axis direction).
5. The slider must own a Graphics_Window (i.e., get_p_graphics_window_by__uuid_from__graphics_window_manager must return a non-null result using the slider's UUID).

Post-conditions:
1. p_this_draggable->slider__distance__u32 is updated to reflect the cursor position clamped to the hitbox bounds (via m_ui_slider__dragged_handler__default).
2. The Graphics_Window owned by the slider has its position_of__gfx_window updated by subtracting position__old__3i32 and adding position__new__3i32.
3. The graphics window manager is re-sorted after the position change.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the old and new positional offsets of the slider's owned graphics window relative to the slider's drag state. It first captures the offset before the drag handler updates the slider's distance, then recomputes the offset after the drag handler runs (since the distance has changed). The position vectors are correctly constructed with the offset placed in the appropriate axis (x for horizontal sliders, y for vertical sliders). The spanning_length is correctly extracted from the slider's spanning_length__3i32 based on the snapped axis. The call to set_position_3i32_of__graphics_window__relative_to correctly applies the relative position change (subtract old, add new).

Implementation Correctness:
Type compatibility — all parameter types match their target function signatures exactly. The spanning_length is correctly typed as i32, matching the range parameter of get_offset_from__ui_slider_percentage. The offset is correctly typed as i32, matching the return type of get_offset_from__ui_slider_percentage.
Undefined behavior — no broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. However, there is a potential issue: p_graphics_window__owned_by__slider is not checked for null before being passed to set_position_3i32_of__graphics_window__relative_to. While the callee has a debug-only null check, in release mode a null pointer would cause undefined behavior. This is consistent with the codebase pattern where debug checks are used for validation.
Validation — the function does not validate p_this_draggable is of kind UI_Element_Kind__Slider, but this is the caller's responsibility. The get_offset_from__ui_slider_percentage function has its own debug validation for this.

Side Effects:
1. Mutates p_this_draggable->slider__distance__u32 (via m_ui_slider__dragged_handler__default).
2. Mutates the position_of__gfx_window of the graphics window owned by the slider (via set_position_3i32_of__graphics_window__relative_to).
3. Triggers a re-sort of graphics windows in the graphics window manager (via set_position_3i32_of__graphics_window__relative_to).
