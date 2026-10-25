get_y_offset_i32F4_of__ray — core/include/raycast/ray.h

Computes the y-axis offset (current minus starting) of a ray, converting the result from i32F20 (20-bit fractional) precision to i32F4 (4-bit fractional) precision.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, initialized Ray__3i32F20 struct.
2. p_ray->ray_current_vector__3i32F20 and p_ray->ray_starting_vector__3i32F20 must contain valid i32F20 y-components.
3. No out-of-bounds sentinel check is performed by this function; the caller is responsible for ensuring the ray is not in an out-of-bounds state if such checks are needed.

Post-conditions:
1. Returns an i32F4 value representing (current_y - starting_y) converted from i32F20 to i32F4 precision via arithmetic right-shift by 16 bits.
2. The input ray struct is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the y-offset of the ray by subtracting the starting y-component from the current y-component. The subtraction is performed at full i32F20 precision (the native precision of the Vector__3i32F20 fields), and the result is then converted to i32F4 using i32F20_to__i32F4. This matches the semantic intent of the function name: "get_y_offset_i32F4_of__ray". The sibling functions get_x_offset_i32F4_of__ray and get_z_offset_i32F4_of__ray follow the exact same pattern for their respective axes, confirming consistency.

Implementation Correctness:
Type compatibility — p_ray is Ray__3i32F20 *, and both ray_current_vector__3i32F20 and ray_starting_vector__3i32F20 are Vector__3i32F20 fields, each containing a y__i32F20 member of type i32F20 (int32_t). The subtraction yields an i32F20, which is the expected input type for i32F20_to__i32F4. The return type of i32F20_to__i32F4 is Signed_Index__i32 (int32_t), which is identical to i32F4. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (caller responsibility, consistent with all sibling functions in ray.h), no type punning, no out-of-bounds access.
Validation — no validation is needed or expected; this is a low-level accessor. The caller is responsible for providing a valid pointer, consistent with the codebase convention where all inline getter functions in ray.h (e.g., get_x_offset_i32F4_of__ray, get_z_offset_i32F4_of__ray, get_squared_length_i32F4_of__ray) omit null checks.

Side Effects:
No side effects — the function is pure. It reads from the ray struct but does not modify it, and it does not call any functions with side effects.
