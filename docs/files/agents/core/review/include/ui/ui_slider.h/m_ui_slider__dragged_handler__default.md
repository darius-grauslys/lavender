# m_ui_slider__dragged_handler__default

**File of origin:** `core/source/ui/ui_slider.c`

## Semantic

Handles a drag event on a UI slider by computing the cursor's position relative to the slider's hitbox along the snapped axis (x or y), storing the clamped result as `slider__distance__u32`, and then invoking the transformed handler to reposition the slider's child element.

## Pre-conditions

1. `p_this_draggable` must be non-null and must be a `UI_Element` of kind `UI_Element_Kind__Slider` with a valid `slider__spanning_length__3i32` field.
2. `p_game` must be non-null and must have a valid `Input` subsystem accessible via `get_p_input_from__game`.
3. `p_graphics_window` must be non-null and must have a valid hitbox AABB manager accessible via `get_pV_hitbox_manager_from__graphics_window`.
4. The UI element must have a hitbox AABB component allocated. If the hitbox is missing, the function logs an error and disables the element rather than crashing.
5. `p_input` and `p_hitbox_aabb_manager` are obtained without null checks; the caller must ensure the game and graphics window are in a valid state.

## Post-conditions

1. `slider__distance__u32` is set to the clamped cursor distance along the snapped axis: for x-axis sliders, `clamp(cursor_x - hitbox_x + width/2, 0, width)`; for y-axis sliders, `clamp(hitbox_y - cursor_y + height/2, 0, height)`.
2. If the hitbox AABB is missing, the element is disabled via `set_ui_element_as__disabled` and the function returns early without modifying `slider__distance__u32`.
3. `m_ui_slider__transformed_handler__default` is called to reposition the slider's child element relative to the cursor position.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to compute the cursor's distance along the slider's track for both x-axis (horizontal) and y-axis (vertical) sliders. The x-axis computation is correct: `cursor.x - hitbox.x + (width >> 1)` computes the cursor's position relative to the hitbox's left edge, offset by half the width to center the thumb on the cursor, and clamped to `[0, width]`.

The y-axis computation has a **sign error**: it uses `-cursor.y + hitbox.y + (height >> 1)` (i.e., `hitbox_y - cursor_y + half_height`), which is the negation of the x-axis pattern. The correct formula should be `cursor.y - hitbox.y + (height >> 1)` (i.e., `cursor_y - hitbox_y + half_height`), matching the x-axis pattern of `cursor - hitbox + half_size`.

This sign error causes `slider__distance__u32` to **decrease** as the cursor moves down for vertical sliders, which is semantically incorrect. The `get_percentage_i32F20_from__ui_slider` function (in `ui_slider.h`) computes the slider's value as `slider__distance__u32 / height`, so vertical sliders report **inverted** percentages. The `get_offset_from__ui_slider_percentage` function, used by `m_ui_slider__dragged_handler__gfx_window__default`, is also affected, causing the slider's graphics window to be positioned incorrectly for vertical sliders.

The transformed handler (`m_ui_slider__transformed_handler__default`) compensates for the sign error in the y-axis case by using `height/2 - slider_distance` instead of `slider_distance + height/2` (as used for x-axis). While this may produce approximately correct visual thumb positioning, the underlying `slider__distance__u32` value remains semantically wrong, corrupting the slider's percentage/offset calculations.

## Implementation Correctness

- **Type compatibility (clamp call):** `get_width_u32_of__hitbox_aabb` and `get_height_u32_of__hitbox_aabb` return `Quantity__u32` (typedef for `uint32_t`), but `clamp__i32` expects `i32` parameters. This is an implicit unsigned-to-signed conversion. While safe for typical UI element sizes (which are well within `INT32_MAX`), it is a type mismatch that could theoretically overflow for very large hitboxes.

- **Type compatibility (assignment):** `cursor_position` is `i32` but `slider__distance__u32` is `u32`. The clamp to `[0, width]` guarantees the value is non-negative, so the implicit signed-to-unsigned conversion is safe. However, it is still a type mismatch.

- **Undefined behavior:** No null dereferences are present. `p_hitbox_aabb` is properly null-checked before use. `p_input` and `p_hitbox_aabb_manager` are used without null checks, but this is consistent with the codebase's convention where the caller is responsible for ensuring valid game and graphics window state.

- **Validation:** The function validates `p_hitbox_aabb` (null check with error logging and early return), which is appropriate for the function's role. The lack of null checks for `p_input` and `p_hitbox_aabb_manager` is consistent with the assumption that the caller provides a valid game and graphics window.

- **Unused variable:** `spanning_length__3i32` is computed via `get_ui_slider__spanning_length` on lines 95-97 but is never used in the function body. This is dead code that should be removed.

## Side Effects

1. **Mutates `slider__distance__u32`:** The `slider__distance__u32` field of the `UI_Element` struct is set to the computed `cursor_position` value (clamped to the hitbox dimensions along the snapped axis).
2. **May disable the element:** If the hitbox AABB component is missing, `set_ui_element_as__disabled` is called on `p_this_draggable`, clearing the `UI_FLAGS__BIT_IS_ENABLED` flag.
3. **Logs an error:** If the hitbox AABB is missing, `debug_error` is called with a descriptive message.
4. **Invokes transformed handler:** `m_ui_slider__transformed_handler__default` is called, which may mutate the position of the slider's child UI element via `set_position_3i32_of__ui_element`.
