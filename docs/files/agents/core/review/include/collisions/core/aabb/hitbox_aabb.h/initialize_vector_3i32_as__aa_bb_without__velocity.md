initialize_vector_3i32_as__aa_bb_without__velocity — core/source/collisions/core/aabb/hitbox_aabb.c

Computes one corner of an AABB hitbox as a Vector__3i32 (integer space) from the hitbox position, half-width, half-height, and a corner direction. The "without__velocity" variant computes the geometric corner only; the caller (initialize_vector_3i32_as__aa_bb) is responsible for subsequently adding velocity.

Pre-conditions:
1. hitbox_point must be a non-null pointer to a writable Vector__3i32 object (no null-check; caller responsibility, consistent with the F4 variant).
2. p_hitbox_aabb must be a non-null pointer to a valid Hitbox_AABB (checked in debug builds via NDEBUG guard).
3. corner_direction must be one of DIRECTION__NORTH_EAST (0x03), DIRECTION__NORTH_WEST (0x09), DIRECTION__SOUTH_EAST (0x05), or DIRECTION__SOUTH_WEST (0x0B). Any other value (including DIRECTION__NONE/0) hits the default case, logs an error, and returns early without modifying hitbox_point.
4. width__quantity_u32 and height__quantity_u32 are used as-is (no range validation); assume reasonable dimensions (< 2^31 so the u32-to-i32 conversion is well-defined).

Post-conditions:
1. On success, hitbox_point is mutated so that x__i32, y__i32, and z__i32 hold the integer-space coordinates of the requested corner of the AABB.
2. On unexpected corner_direction, hitbox_point is left unmodified and the function returns early.

Correctness Verdict: Incorrect

Semantic Alignment:
The function intends to produce an integer-space (Vector__3i32) corner position from a fixed-point (Vector__3i32F4) hitbox. The x and y components are correctly converted from the hitbox's F4 fixed-point position to plain integers via get_x_i32_from__hitbox_aabb and get_y_i32_from__hitbox_aabb, which internally call i32F4_to__i32 (arithmetic right-shift by FRACTIONAL_PERCISION_4__BIT_SIZE = 4).

However, the z component is NOT converted:
    hitbox_point->z__i32 = p_hitbox_aabb->position__3i32F4.z__i32F4;

This assigns the raw F4 fixed-point value directly to the integer output. In the F4 variant (initialize_vector_3i32F4_as__aa_bb_without__velocity), this is correct because both input and output are F4. But in this i32 variant, the output is a plain integer, so z should be converted the same way as x and y, e.g.:
    hitbox_point->z__i32 = get_z_i32_from__hitbox_aabb(p_hitbox_aabb);
(or equivalently, get_z_i32_from__vector_3i32F4(p_hitbox_aabb->position__3i32F4).)

Without this conversion, z retains the fixed-point scaling and is 16x larger than the actual integer position value for non-zero z coordinates. This breaks semantic consistency with x and y and causes downstream consumers of the computed corner to receive an incorrect z value.

Implementation Correctness:
- Type compatibility — i32F4 and Signed_Index__i32 are both typedefs of int32_t, so the z assignment compiles without issue; the problem is semantic (missing conversion), not a type error.
- The u32-to-Signed_Index__i32 conversion for offset_half_width/offset_half_height (width>>1, height>>1) involves an implicit unsigned-to-signed conversion. This is acceptable for reasonable hitbox dimensions (< 2^31) and matches the F4 variant's pattern.
- No undefined behavior — no pointer arithmetic, no null dereference (hitbox_point null is caller's responsibility, consistent with codebase pattern), no type punning, no out-of-bounds access.
- Validation — the null check on p_hitbox_aabb is appropriate (debug-only). The switch default case properly handles unexpected corner_direction values. The lack of null-check on hitbox_point is consistent with the F4 variant and the codebase convention (output struct pointers are the caller's responsibility).
- Note: the debug_error string in the NDEBUG guard reads "initialize_vector_3i32F4_as__aa_bb_without__velocity" — a copy-paste error referencing the F4 variant name instead of the correct "initialize_vector_3i32_as__aa_bb_without__velocity". This is debug-only and does not affect release behavior, but it is misleading when diagnosing null-pointer issues.

Side Effects:
Mutates hitbox_point in place, writing x__i32, y__i32, and z__i32. In the default (unexpected direction) case, returns early with no mutation. No other state is modified. The debug_error call in the default case is an observable side effect (logging), but only in debug builds with an unexpected direction.
