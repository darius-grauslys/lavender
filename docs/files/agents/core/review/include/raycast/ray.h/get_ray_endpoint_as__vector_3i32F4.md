get_ray_endpoint_as__vector_3i32F4 — core/include/raycast/ray.h

Returns the ray's current endpoint position as a Vector__3i32F4 by converting the ray's internal 20-bit fractional fixed-point position to 4-bit fractional fixed-point.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid Ray__3i32F20 struct.
2. p_ray->ray_current_vector__3i32F20 may be out-of-bounds; no constraint on the vector's validity (out-of-bounds is a valid sentinel state).

Post-conditions:
1. Returns a Vector__3i32F4 representing the ray's current endpoint, converted from i32F20 to i32F4 precision via arithmetic right shift by 16 bits (FRACTIONAL_PERCISION_16__BIT_SIZE).
2. The returned value is a new value; no mutation occurs on the input ray.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves the ray's current position vector (ray_current_vector__3i32F20) and converts it to Vector__3i32F4 using the established conversion function vector_3i32F20_to__vector_3i32F4. The conversion from i32F20 (20 fractional bits) to i32F4 (4 fractional bits) is performed by i32F20_to__i32F4, which arithmetic-right-shifts by 16 bits — the correct difference in fractional precision. The function name accurately describes its purpose: it returns the ray endpoint as a Vector__3i32F4.

Implementation Correctness:
Type compatibility — the function returns Vector__3i32F4, and vector_3i32F20_to__vector_3i32F4 also returns Vector__3i32F4. No implicit conversions or truncation beyond the intentional precision reduction from i32F20 to i32F4.
Undefined behavior — no pointer arithmetic, no null dereference (caller's responsibility, consistent with all other functions in this header), no type punning, no out-of-bounds access.
No validation is performed — this is consistent with the rest of the ray.h header, where all static inline functions take Ray__3i32F20 *p_ray without null checks. The caller is responsible for ensuring p_ray is valid.

Side Effects:
No side effects — this is a pure function. It reads from p_ray->ray_current_vector__3i32F20 and returns a converted value without mutating any state.
