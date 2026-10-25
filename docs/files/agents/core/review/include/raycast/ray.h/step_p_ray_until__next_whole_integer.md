step_p_ray_until__next_whole_integer — core/source/raycast/ray.c

Advances the ray's current position by repeatedly calling step_p_ray until at least one of the two plane-relevant components crosses the next whole-integer boundary (i.e., its integer part, extracted by an arithmetic right shift of FRACTIONAL_PERCISION_20__BIT_SIZE = 20 bits, changes from its initial value).

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, writable Ray__3i32F20 struct.
2. p_ray->angle_of__ray must be a valid index (0–254) into __DEGREE_TO_2i32F10__LOOKUP_TABLE[255], since the lookup table has 255 entries and the field is a 10-bit bitfield.
3. p_ray->ray_plane_mode must be a valid Ray_Plane_Mode value (Ray_Plane_Mode__XY, Ray_Plane_Mode__XZ, or Ray_Plane_Mode__YZ); the default case in the switch falls through to XY.
4. p_ray->ray_current_vector__3i32F20 must be a valid position vector (not out-of-bounds).
5. The ray's direction offset (from the lookup table) must have a non-zero component along at least one of the two tracked axes for the given ray_plane_mode; otherwise the loop may not terminate (caller responsibility).

Post-conditions:
1. p_ray->ray_current_vector__3i32F20 has been advanced by one or more calls to step_p_ray (at least one step is always taken due to the do-while loop).
2. After the function returns, at least one of the two plane-relevant components of ray_current_vector__3i32F20 has a different integer part (i.e., ARITHMETRIC_R_SHIFT(component, 20)) than it did before the function was called.
3. p_ray->ray_starting_vector__3i32F20, p_ray->angle_of__ray, and p_ray->ray_plane_mode are unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent. It delegates to __step_p_ray_until with FRACTIONAL_PERCISION_20__BIT_SIZE (20), which is the correct number of fractional bits for an i32F20 fixed-point value. Right-shifting by 20 bits extracts the integer portion, and the do-while loop steps the ray until that integer portion changes for either tracked component — exactly "step until the next whole integer." No semantic drift is present.

Implementation Correctness:
Type compatibility — p_ray is Ray__3i32F20*, matching the function signature. percision is u32 and is passed to ARITHMETRIC_R_SHIFT as the shift-count argument; 20 is within the valid range [0, 31] for a 32-bit shift, so no undefined behavior arises from the shift. Signed_Quantity__i32 (int32_t) is used for the captured integer parts a and b, which matches the return type of ARITHMETRIC_R_SHIFT when applied to i32F20 (int32_t) values.
No undefined behavior — no null dereference (p_ray is assumed valid per the API contract), no out-of-bounds array access (angle is a 10-bit field indexing a 255-entry table), no type punning. The do-while loop guarantees at least one iteration, preventing a zero-step return.
No validation is needed within this function — it is a low-level ray-stepping utility; ensuring p_ray is valid and the angle is in range is the caller's responsibility.
Note: ARITHMETRIC_R_SHIFT uses -(-(x)) for negative values, which is technically UB if x == INT32_MIN; however, this is a pre-existing limitation of the macro, not specific to this function.

Side Effects:
Mutates p_ray->ray_current_vector__3i32F20 by advancing it (via step_p_ray / add_p_vectors__3i32F20). No other state is modified. No side effects beyond the mutation of the ray's current position.
