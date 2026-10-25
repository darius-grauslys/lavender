get_x_offset_i32F4_of__ray — core/include/raycast/ray.h

Computes the x-component offset (delta) between a ray's current position and its starting position, returned in i32F4 fixed-point format (4-bit fractional precision).

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, initialized Ray__3i32F20 struct.
2. p_ray->ray_current_vector__3i32F20.x__i32F20 and p_ray->ray_starting_vector__3i32F20.x__i32F20 must be valid i32F20 values (int32_t with 20-bit fractional precision). No out-of-bounds checking is performed by this function; it is the caller's responsibility.

Post-conditions:
1. Returns an i32F4 value representing the x-offset: (current.x - starting.x) converted from i32F20 to i32F4.
2. The Ray__3i32F20 struct pointed to by p_ray is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the x-offset between the ray's current and starting positions. The subtraction is performed in i32F20 format (preserving full 20-bit fractional precision), and the result is then converted to i32F4 via i32F20_to__i32F4, which right-shifts by FRACTIONAL_PERCISION_16__BIT_SIZE (16 bits = 20 - 4). This is the more precise approach compared to converting each component to i32F4 first and then subtracting, as it avoids double truncation. The approach is consistent with sibling functions get_y_offset_i32F4_of__ray and get_z_offset_i32F4_of__ray, as well as with get_vector__3i32F20_wrt__p_ray_and_its_origin (which also subtracts in i32F20 first). The ARITHMETRIC_R_SHIFT macro used by i32F20_to__i32F4 correctly handles negative values (arithmetic right shift on negatives).

Implementation Correctness:
Type compatibility — i32F20 is int32_t and i32F4 is int32_t. The subtraction of two i32F20 (int32_t) values yields int32_t. i32F20_to__i32F4 returns Signed_Index__i32 (int32_t), which is identical to i32F4. No implicit conversions or truncation occur beyond the intended fixed-point format conversion.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility for non-null p_ray), no type punning, no out-of-bounds access. The subtraction of two int32_t values could theoretically overflow if values are at opposite extremes, but this is an accepted risk consistent with subtract_vectors__3i32F20 and other vector operations in the codebase.
No validation is needed — this is a low-level static inline accessor. Null checking is not performed, consistent with all sibling accessor functions in ray.h (e.g., get_y_offset_i32F4_of__ray, get_z_offset_i32F4_of__ray, get_vector__3i32F20_wrt__p_ray_and_its_origin). The caller is responsible for ensuring p_ray is valid.

Side Effects:
No side effects — the function is pure. It only reads from p_ray and returns a computed i32F4 value. The Ray__3i32F20 struct is not mutated.
