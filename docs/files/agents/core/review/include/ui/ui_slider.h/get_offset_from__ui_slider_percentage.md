get_offset_from__ui_slider_percentage — core/include/ui/ui_slider.h

## Semantic
Computes a signed integer offset by scaling the slider's current position percentage (distance along its axis divided by its dimension) by the given `range`, returning the result as a plain `i32`.

## Pre-conditions
1. `p_hitbox_aabb_manager` must be a valid, non-null pointer to an initialized `Hitbox_AABB_Manager`.
2. `p_ui_slider` must be a valid, non-null pointer to a `UI_Element` whose `the_kind_of_ui_element__this_is` is `UI_Element_Kind__Slider`. (Checked in debug builds only via `#ifndef NDEBUG`.)
3. `p_ui_slider->slider__distance__u32` must be a valid distance value within the slider's span.
4. The slider's dimension (width if snapped to X axis, height if snapped to Y axis) must be non-zero to avoid division by zero.
5. `range` is an `i32` and may be any signed integer value (positive, negative, or zero).

## Post-conditions
1. Returns an `i32` representing `floor((slider__distance__u32 * range) / dimension)` where `dimension` is the slider's width or height depending on its snapped axis.
2. If the debug type-check fails (non-slider element passed), returns `0`.
3. No state is mutated; the function is pure/read-only with respect to all parameters.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation correctly fulfills its semantic intent. The computation proceeds as follows:

1. `get_percentage_i32F20_from__ui_slider` returns an `i32F20` (fixed-point with 20 fractional bits) representing `slider__distance__u32 / dimension`. This is computed as `i32_to__i32F20(slider__distance__u32) / dimension`, which is `(slider__distance__u32 << 20) / dimension`.

2. The result is multiplied by `range` (a plain `i32`), yielding `(slider__distance__u32 << 20) * range / dimension`.

3. `i32F20_to__i32` right-shifts by 20 bits, giving `(slider__distance__u32 * range) / dimension` — the percentage of `range` corresponding to the slider's current position.

This is semantically correct: the offset is the slider's position fraction scaled by `range`. The use of fixed-point arithmetic preserves precision during the division step.

## Implementation Correctness
- **Type compatibility**: `slider__distance__u32` is `u32` but is passed to `i32_to__i32F20` which expects `Signed_Index__i32` (i.e., `int32_t`). This is an implicit unsigned-to-signed conversion. If `slider__distance__u32` exceeds `INT32_MAX`, the conversion is implementation-defined. In practice, slider distances are bounded by the element's dimension (which is a `Quantity__u32` but typically small), so this is unlikely to cause issues. However, it is a minor type mismatch.

- **Potential overflow**: The multiplication `get_percentage_i32F20_from__ui_slider(...) * range` is performed in 32-bit integer arithmetic. The `i32F20` value can be up to approximately `INT32_MAX` (if the slider is at full extent), and `range` can also be up to `INT32_MAX`. The product of two large 32-bit values can overflow, producing undefined behavior. Callers should ensure `range` is bounded such that the product does not exceed `INT32_MAX`.

- **Division by zero**: `get_percentage_i32F20_from__ui_slider` divides by the slider's width or height. If this dimension is zero, the behavior is undefined. No guard exists against this. This is a potential latent bug, though a zero-dimension slider is likely an invalid state.

- **Null pointer validation**: Only `p_ui_slider`'s type is validated (debug-only). `p_hitbox_aabb_manager` is not null-checked. If null, `get_p_hitbox_aabb_of__ui_element` would dereference it, leading to undefined behavior. This follows the codebase's pattern of relying on caller correctness for non-debug builds.

## Side Effects
No side effects. The function reads from `p_ui_slider` and `p_hitbox_aabb_manager` but does not modify any state. No callee functions invoked have side effects on the parameters.
