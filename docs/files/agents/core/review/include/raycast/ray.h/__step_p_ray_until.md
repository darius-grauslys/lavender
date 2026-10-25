__step_p_ray_until — core/source/raycast/ray.c

Steps a ray forward until it crosses a quantized boundary in the plane-relevant components.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, initialized Ray__3i32F20.
2. p_ray->ray_plane_mode must be one of Ray_Plane_Mode__XY, Ray_Plane_Mode__XZ, or Ray_Plane_Mode__YZ (the default case maps to XY).
3. p_ray->angle_of__ray must index a valid entry in __DEGREE_TO_2i32F10__LOOKUP_TABLE (i.e., a valid angle).
4. percision must be less than 32 (to avoid undefined behavior in the ARITHMETRIC_R_SHIFT macro). Callers pass FRACTIONAL_PERCISION_20__BIT_SIZE (20) or 23 (20 + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT), both valid.
5. The ray must have a non-zero offset in the relevant plane so that the loop terminates (caller responsibility).

Post-conditions:
1. p_ray->ray_current_vector__3i32F20 is mutated: it has been advanced by one or more calls to step_p_ray.
2. At loop exit, at least one of the two plane-relevant components (selected by ray_plane_mode) has a quantized value (right-shifted by percision) that differs from its initial quantized value.
3. The ray has not crossed more than one boundary in either relevant component (the loop exits on the first crossing).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of "step the ray until it reaches the next whole integer or tile boundary." The function captures the initial quantized values of the two components relevant to the ray's plane mode (XY → x,y; XZ → x,z; YZ → y,z), then repeatedly calls step_p_ray in a do-while loop. The loop continues while both components' quantized values remain equal to their initial values, and exits as soon as either component crosses a boundary. This matches the intent of step_p_ray_until__next_whole_integer (percision=20, crossing to the next whole integer) and step_p_ray_until__next_tile (percision=23, crossing to the next tile-aligned position).

Implementation Correctness:
Type compatibility — p_ray is Ray__3i32F20*, matching the struct definition. The percision parameter is u32, used as a shift amount in ARITHMETRIC_R_SHIFT; valid since callers pass 20 or 23. Variables a and b are Signed_Quantity__i32 (int32_t), matching i32F20 (also int32_t) component types. Pointers p_a and p_b are Signed_Quantity__i32* pointing to i32F20 fields, which are type-compatible.
Undefined behavior — no null dereference (p_ray is assumed valid by caller for a private static inline function). No out-of-bounds access. The ARITHMETRIC_R_SHIFT macro handles negative values correctly. Shift amounts (20, 23) are < 32, avoiding UB. The do-while loop always executes at least once, which is correct for the "step until" semantics.
Validation — no validation is needed inside this private static inline function; the caller (step_p_ray_until__next_whole_integer / step_p_ray_until__next_tile) is responsible for ensuring p_ray is valid.

Side Effects:
Mutates p_ray->ray_current_vector__3i32F20 by advancing it via repeated calls to step_p_ray. The ray_starting_vector__3i32F20 and other fields are not modified.
