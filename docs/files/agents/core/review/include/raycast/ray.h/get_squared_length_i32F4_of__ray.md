get_squared_length_i32F4_of__ray — core/include/raycast/ray.h

Computes the squared length of a ray (the squared distance between the ray's current position and its starting position) in i32F4 fixed-point format.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, writable Ray__3i32F20 struct.
2. p_ray->ray_current_vector__3i32F20 must be a valid Vector__3i32F20 (the ray's current position).
3. p_ray->ray_starting_vector__3i32F20 must be a valid Vector__3i32F20 (the ray's starting/origin position).

Post-conditions:
1. Returns an i32F4 value representing the squared length of the ray (i.e., the squared magnitude of the delta vector current − starting).
2. p_ray is not mutated; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function faithfully implements its intent. It computes the delta vector as subtract_vectors__3i32F20(current, starting), converts that delta to i32F4 precision via vector_3i32F20_to__vector_3i32F4, and then computes the squared length via get_distance_squared_of__vector_3i32F4 (which performs x² + y² + z² with a right-shift by FRACTIONAL_PERCISION_4__BIT_SIZE to correct for the fixed-point multiplication). This matches the sibling function get_squared_length_i32F20_of__ray, which performs the same logical computation at higher precision. No semantic drift is present.

Implementation Correctness:
Type compatibility — all parameter and return types match exactly:
- subtract_vectors__3i32F20 takes Vector__3i32F20 by value; p_ray->ray_current_vector__3i32F20 and p_ray->ray_starting_vector__3i32F20 are Vector__3i32F20 struct members accessed through a pointer, which is correct.
- vector_3i32F20_to__vector_3i32F4 takes Vector__3i32F20 by value and returns Vector__3i32F4; the return is consumed correctly by get_distance_squared_of__vector_3i32F4.
- get_distance_squared_of__vector_3i32F4 takes Vector__3i32F4 by value and returns i32F4, which matches the function's declared return type.
No implicit conversions or truncation occur at any step.

Undefined behavior — no broken pointer arithmetic, no null dereference (p_ray is dereferenced, but null-checking is not performed by any sibling function in this header; it is the caller's responsibility per codebase convention), no type punning, no out-of-bounds access.

Validation — no validation is needed for this function's role; it is a low-level computation helper. The caller is responsible for ensuring p_ray is valid, consistent with all other inline functions in ray.h (e.g., get_ray_endpoint_as__vector_3i32F4, get_vector__3i32F20_wrt__p_ray_and_its_origin).

Side Effects:
No side effects. The function does not modify p_ray or any other observable state. It performs pure arithmetic computation and returns the result.
