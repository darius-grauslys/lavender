step_p_ray_until__next_tile — core/source/raycast/ray.c

Advances the ray forward until it crosses a tile boundary, using a do-while loop that steps the ray and checks whether the two relevant plane components have exited their current tile.

Pre-conditions:
1. p_ray must be a non-null pointer to a valid, initialized Ray__3i32F20 object.
2. p_ray->angle_of__ray must be a valid index into the __DEGREE_TO_2i32F10__LOOKUP_TABLE (i.e., a valid Degree__u9 value), so that step_p_ray produces a non-zero offset.
3. p_ray->ray_plane_mode must be a valid Ray_Plane_Mode enum value (Ray_Plane_Mode__XY, Ray_Plane_Mode__XZ, or Ray_Plane_Mode__YZ). If invalid, it defaults to Ray_Plane_Mode__XY behavior.

Post-conditions:
1. p_ray->ray_current_vector__3i32F20 is mutated such that at least one of the two plane-relevant components has crossed a tile boundary relative to its position before the function was called.
2. The ray is advanced by at least one step (the loop is do-while, guaranteeing a minimum of one step_p_ray call).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements "step until next tile." It delegates to __step_p_ray_until with a precision of FRACTIONAL_PERCISION_20__BIT_SIZE + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (20 + 3 = 23 bits). This precision value correctly isolates the tile index by right-shifting past both the 20-bit fractional portion and the 3-bit tile sub-coordinate (since tiles are 2^3 = 8 units). The captured tile indices (a, b) represent the ray's current tile before stepping. The do-while loop steps the ray and continues while both components remain in the same tile, exiting as soon as either component crosses into a new tile. This is the standard DDA (Digital Differential Analyzer) raycasting behavior and matches the semantic intent of "step until next tile."

Implementation Correctness:
Type compatibility — percision is u32, and ARITHMETRIC_R_SHIFT accepts the shift amount as a generic expression; the shift amount of 23 is well within the valid range (0–31) for 32-bit integers. The Signed_Quantity__i32 type is int32_t, matching the i32F20 fields.
Undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access. The ARITHMETRIC_R_SHIFT macro correctly handles negative values by negating before and after the shift. The switch statement covers all valid Ray_Plane_Mode values with a default fallback, so p_a and p_b are always assigned before use.
Validation — no validation is performed, which is appropriate for this low-level raycasting function. Null-checking and angle/plane-mode validation are the caller's responsibility, consistent with the engine's coding style for similar functions.

Side Effects:
The function mutates p_ray->ray_current_vector__3i32F20 by advancing it through repeated calls to step_p_ray. No other state is modified. The ray's starting vector is not changed.
