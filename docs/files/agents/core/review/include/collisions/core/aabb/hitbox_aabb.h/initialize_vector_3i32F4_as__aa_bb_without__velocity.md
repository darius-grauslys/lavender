initialize_vector_3i32F4_as__aa_bb_without__velocity — core/source/collisions/core/aabb/hitbox_aabb.c

Computes one corner point of an AABB hitbox in F4 fixed-point coordinates, without applying velocity.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to an initialized Hitbox_AABB (checked in debug builds only via #ifndef NDEBUG).
2. hitbox_point must be a non-null pointer to a writable Vector__3i32F4 (not checked — caller's responsibility, consistent with the codebase's low-level assignment pattern).
3. corner_direction must be one of DIRECTION__NORTH_EAST, DIRECTION__NORTH_WEST, DIRECTION__SOUTH_EAST, or DIRECTION__SOUTH_WEST. Any other value triggers the default case, which logs an error and returns without modifying hitbox_point.
4. p_hitbox_aabb must have valid position__3i32F4, width__quantity_u32, and height__quantity_u32 fields set prior to the call.

Post-conditions:
1. hitbox_point->x__i32F4 is set to p_hitbox_aabb->position__3i32F4.x__i32F4 plus a signed half-width offset (positive for East-facing corners, negative for West-facing corners).
2. hitbox_point->y__i32F4 is set to p_hitbox_aabb->position__3i32F4.y__i32F4 plus a signed half-height offset (positive for North-facing corners, negative for South-facing corners).
3. hitbox_point->z__i32F4 is set to p_hitbox_aabb->position__3i32F4.z__i32F4 (copied verbatim; no z-axis offset is applied since this is a 2D AABB in 3D space).
4. If corner_direction is invalid, hitbox_point is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes corner positions of an AABB given its position and dimensions. The width and height are halved (>> 1) and then converted to F4 fixed-point (<< FRACTIONAL_PERCISION_4__BIT_SIZE). The sign of the half-width/half-height offset is selected by the corner_direction switch: NORTH_EAST is (+,+), NORTH_WEST is (-,+), SOUTH_EAST is (+,-), SOUTH_WEST is (-,-). The z-coordinate is copied directly from the position. The implementation fulfills the semantic intent — the sibling function initialize_vector_3i32F4_as__aa_bb calls this one and then adds velocity, confirming that this function's contract is "corner position without velocity."

Implementation Correctness:
- Type compatibility — width__quantity_u32 (uint32_t) is right-shifted and assigned to Signed_Index__i32 (int32_t), an implicit unsigned-to-signed conversion. For typical hitbox dimensions (well under INT32_MAX) this is safe. The subsequent addition of two int32_t values to populate i32F4 (int32_t) is type-safe with no truncation for normal game object sizes. No implicit conversions cause data loss under practical assumptions.
- Undefined behavior — no broken pointer arithmetic, no null dereference (p_hitbox_aabb is checked in debug), no type punning, no out-of-bounds access. The right-shift of an unsigned type (>> 1) is a well-defined logical shift. The switch has a default case that returns, so no uninitialized-value path exists.
- Validation — p_hitbox_aabb is validated in debug builds. hitbox_point is not validated for null, but this is consistent with the codebase's low-level struct-assignment convention (cf. initialize_audio_effect), where the caller ensures valid pointers. The corner_direction switch handles all invalid values via the default case with a logged error.
- Note: width__quantity_u32 >> 1 truncates for odd widths (e.g., width=5 yields 2 rather than 2.5), introducing a minor asymmetry in the computed AABB corners. Whether this is acceptable depends on engine-level invariants guaranteeing even dimensions; the truncation itself is well-defined.

Side Effects:
Modifies the Vector__3i32F4 struct pointed to by hitbox_point, setting all three fields (x__i32F4, y__i32F4, z__i32F4). No other observable state is changed — no memory allocation, no pool registration, no I/O, no global side effects.

Lavender-Specific Semantics:
This is NOT RAII-style initialization. It is a struct field population — the function writes corner-point coordinates into an existing Vector__3i32F4 that is typically used as a transient hitbox corner. It performs no resource acquisition, allocation, or pool management. The name "initialize" follows Lavender's convention of meaning "populate/reset a struct's fields to a computed default state," not resource acquisition.
