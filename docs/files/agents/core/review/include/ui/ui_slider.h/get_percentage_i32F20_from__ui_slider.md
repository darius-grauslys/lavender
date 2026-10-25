get_percentage_i32F20_from__ui_slider — core/include/ui/ui_slider.h

Computes the percentage (as a fixed-point i32F20 value) of a UI slider's current drag distance relative to its spanning dimension (width or height, depending on the snap axis).

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager.
2. p_ui_slider must be a non-null pointer to a valid UI_Element.
3. p_ui_slider must be of kind UI_Element_Kind__Slider (checked in debug builds only).
4. The slider's hitbox (looked up via the UI_Element's UUID in the Hitbox_AABB_Manager) must exist and have non-zero width or height, depending on the snap axis. No guard exists for a zero span dimension.
5. slider__distance__u32 should not exceed INT32_MAX to avoid implementation-defined behavior in the implicit u32-to-i32 conversion.

Post-conditions:
1. Returns an i32F20 (int32_t with 20 fractional bits) representing the ratio slider__distance__u32 / span_dimension. A value of 1.0 (0x100000 in i32F20) indicates the slider is at full span.
2. In debug builds, if p_ui_slider is not a Slider, returns 0 and logs a debug error.

Correctness Verdict: Incorrect

Semantic Alignment:
The computation matches the semantic intent of computing a percentage. The formula i32_to__i32F20(distance) / span correctly produces a fixed-point ratio. If distance equals span, the result is 1.0 in i32F20 format. The use of the snap axis to select width or height is correct.

Implementation Correctness:
Type compatibility — slider__distance__u32 is u32 (uint32_t), but i32_to__i32F20 expects Signed_Index__i32 (int32_t). This is an implicit unsigned-to-signed conversion. While the ARITHMETRIC_L_SHIFT macro inside i32_to__i32F20 reinterprets the value as u32 before shifting (mitigating practical impact), the parameter type mismatch is still a type incompatibility.

Undefined behavior — the divisor is a Quantity__u32 (uint32_t) obtained from get_width_from__p_ui_element or get_height_from__p_ui_element. If the slider's hitbox does not exist or has zero width/height, the divisor is 0, causing division by zero (undefined behavior in C). In debug builds, get_width_u32_of__hitbox_aabb returns 0 for a null hitbox, which directly leads to division by zero. No guard exists for this case.

Mixed signed/unsigned division — the dividend is i32F20 (int32_t) and the divisor is Quantity__u32 (uint32_t). Per C's usual arithmetic conversions, the int32_t dividend is implicitly converted to uint32_t before the division. If the i32F20 value is negative (which can occur when slider__distance__u32 is large enough that shifting left by 20 bits overflows int32_t), the unsigned conversion produces a very large positive value, yielding an incorrect quotient. While the unsigned reinterpretation happens to produce correct results for values that don't overflow int32_t, the mixed signed/unsigned operation is fragile and error-prone.

Validation — the debug check only validates the slider kind. It does not validate p_hitbox_aabb_manager or p_ui_slider for null, nor does it guard against division by zero. Given that this function performs a division (which has a distinct undefined-behavior failure mode), validation of the divisor is appropriate for this function's role.

Side Effects:
No side effects — the function is a pure computation that reads slider state and hitbox dimensions but does not modify any state.
