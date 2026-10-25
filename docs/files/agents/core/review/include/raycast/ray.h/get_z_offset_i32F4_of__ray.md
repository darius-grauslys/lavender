get_z_offset_i32F4_of__ray — core/include/raycast/ray.h

Computes the z-axis offset (delta) of a ray in i32F4 fixed-point precision by subtracting the ray's starting z-coordinate from its current z-coordinate and converting the result from i32F20 (20-bit fractional) to i32F4 (4-bit fractional) precision.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, writable Ray__3i32F20 object.
2. p_ray->ray_current_vector__3i32F20.z__i32F20 and p_ray->ray_starting_vector__3i32F20.z__i32F20 must contain valid i32F20 values (no out-of-bounds sentinel values are checked; that is the caller's responsibility).

Post-conditions:
1. The function returns an i32F4 value representing the z-offset (current_z - starting_z) converted from F20 to F4 fixed-point precision via an arithmetic right shift of 16 bits.
2. The pointed-to Ray__3i32F20 struct is not mutated.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the z-offset between the ray's current and starting positions, consistent with the sibling functions get_x_offset_i32F4_of__ray and get_y_offset_i32F4_of__ray which follow the identical pattern for the x and y axes. The conversion from i32F20 to i32F4 is semantically correct: i32F20 has 20 bits of fractional precision and i32F4 has 4 bits, so a right shift of 16 bits (FRACTIONAL_PERCISION_16__BIT_SIZE) is the correct conversion. The arithmetic right shift (ARITHMETRIC_R_SHIFT) correctly handles negative offsets.

Implementation Correctness:
Type compatibility — p_ray->ray_current_vector__3i32F20.z__i32F20 and p_ray->ray_starting_vector__3i32F20.z__i32F20 are both of type i32F20 (int32_t). Their subtraction yields an i32F20 (int32_t), which is the correct input type for i32F20_to__i32F4. The return type of i32F20_to__i32F4 is Signed_Index__i32 (int32_t), and the function's declared return type is i32F4 (also int32_t). All types are compatible with no implicit conversions or truncation. No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility, consistent with all sibling inline functions in this file), no type punning, no out-of-bounds access. No validation is performed, which is appropriate for this low-level inline utility function; the caller is responsible for ensuring p_ray is valid.

Side Effects:
No side effects — the function is pure: it reads from the pointed-to struct but does not modify it, and produces no other observable effects.
