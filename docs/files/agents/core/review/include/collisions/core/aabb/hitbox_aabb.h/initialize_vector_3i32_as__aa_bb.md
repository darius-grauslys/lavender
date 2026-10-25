initialize_vector_3i32_as__aa_bb — core/source/collisions/core/aabb/hitbox_aabb.c

Computes a designated corner vertex of an AABB hitbox as a plain Vector__3i32, incorporating the hitbox's x/y velocity offset, by delegating to the without-velocity helper and then adding velocity.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a valid, initialized Hitbox_AABB object.
2. hitbox_point must be a non-null, writable pointer to a Vector__3i32 (caller's responsibility; not validated, consistent with codebase convention).
3. corner_direction should be one of DIRECTION__NORTH_EAST, DIRECTION__NORTH_WEST, DIRECTION__SOUTH_EAST, or DIRECTION__SOUTH_WEST. Any other value causes the delegated _without__velocity helper to log a debug error and return early, leaving hitbox_point uninitialized.

Post-conditions:
1. hitbox_point is mutated. Its x and y components are set to the hitbox corner position (converted from i32F4 to i32 via arithmetic right shift by 4) plus the corresponding velocity component (also converted from i32F4 to i32). The z component is set to the hitbox position's raw fixed-point z value (see Implementation Correctness — there is a bug).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to compute a corner point of the AABB in integer space, including the hitbox's velocity for x and y. The x and y components are correctly computed. However, the z component contains a bug in the delegated function initialize_vector_3i32_as__aa_bb_without__velocity (line 225): it assigns the raw fixed-point value directly:
    hitbox_point->z__i32 = p_hitbox_aabb->position__3i32F4.z__i32F4;
instead of converting from i32F4 to i32. By contrast, the x and y components (lines 216-223) correctly use get_x_i32_from__hitbox_aabb / get_y_i32_from__hitbox_aabb, which perform i32F4_to__i32 (arithmetic right shift by FRACTIONAL_PERCISION_4__BIT_SIZE = 4). The z value is therefore stored in fixed-point form (16x larger than the intended integer), a semantic drift bug. The analogous F4 version (line 158) is correct because both sides are i32F4.

Implementation Correctness:
- Type compatibility: i32F4 and Signed_Index__i32 are both int32_t, so the direct assignment on z (line 225) does not produce a compiler warning — the bug is silent. The velocity additions (lines 243-246) correctly use get_x_i32_from__vector_3i32F4 / get_y_i32_from__vector_3i32F4, which convert the i32F4 velocity to i32 before adding.
- Undefined behavior: None — no pointer arithmetic, null dereference (in release), type punning, or out-of-bounds access.
- Validation: p_hitbox_aabb is checked in debug builds (consistent with codebase convention). hitbox_point is not validated — consistent with the codebase convention where Vector* parameters are the caller's responsibility.
- Additional issue: The debug error message on line 234 is a copy-paste artifact: it reads "initialize_vector_3i32F4_as__aa_bb" (with "F4") but the actual function is initialize_vector_3i32_as__aa_bb. This is cosmetic and debug-only but misleading.

Side Effects:
Mutates hitbox_point (writes x, y, and z components). Does not modify p_hitbox_aabb. Also triggers the side effects of initialize_vector_3i32_as__aa_bb_without__velocity, which only writes to hitbox_point (plus debug logging on invalid input).
