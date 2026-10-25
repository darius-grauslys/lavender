get_aa_bb_as__vectors_3i32_from__hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Computes the two opposite corners of a hitbox's axis-aligned bounding box as 3i32 vectors (velocity-inclusive).

Pre-conditions:
1. hitbox must be a non-null pointer to a valid Hitbox_AABB.
2. aa must be a non-null pointer to a writable Vector__3i32 (will receive the south-west / minimum corner).
3. bb must be a non-null pointer to a writable Vector__3i32 (will receive the north-east / maximum corner).

Post-conditions:
1) *aa is set to the south-west corner of the hitbox (position + half-width/half-height negated, plus velocity).
2) *bb is set to the north-east corner of the hitbox (position + half-width/half-height, plus velocity).

Correctness Verdict: Correct

Semantic Alignment:
Fulfills intent. It delegates to initialize_vector_3i32_as__aa_bb with DIRECTION__SOUTH_WEST for aa and DIRECTION__NORTH_EAST for bb, yielding the minimum (SW) and maximum (NE) corners respectively. This matches the caller clamp_p_vector_3i32_to__hitbox_aabb, which treats aa.x/aa.y as lower bounds and bb.x/bb.y as upper bounds. The behavior is identical to the sibling get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb, so the velocity-inclusive computation is consistent across both vector widths.

Implementation Correctness:
Type compatibility — parameter types (Hitbox_AABB *, Vector__3i32 *) match the callee's expected types exactly. No implicit conversions.
No undefined behavior — no pointer arithmetic, type punning, or out-of-bounds access. The callee validates p_hitbox_aabb for null in debug builds (NDEBUG undefined); in release builds null dereference would be undefined, which is consistent with this codebase's low-level-helper convention where the caller guarantees valid pointers.
Validation — no validation is performed in this function. This is appropriate: it is a thin delegating wrapper, and the codebase convention places debug-only null checks in the lower-level callee while treating pointer validity as the caller's responsibility for release builds. Note aa and bb are not null-checked by the callee either, so their non-nullness rests entirely on the caller.

Side Effects:
Mutates *aa and *bb via the callee initialize_vector_3i32_as__aa_bb, which writes all three components (x__i32, y__i32, z__i32) of each output vector.
