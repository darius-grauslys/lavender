get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Extracts the south-west and north-east corners of a Hitbox_AABB as fixed-point Vector__3i32F4 tuples, each offset by the hitbox's velocity, writing them to the two output parameters.

Pre-conditions:
1. hitbox must be a non-null pointer to a valid Hitbox_AABB. In release builds this is only guarded by the callee (initialize_vector_3i32F4_as__aa_bb), which checks p_hitbox_aabb only under #ifndef NDEBUG; a NULL hitbox in release would dereference and cause undefined behavior.
2. aa must be a non-null pointer to a writable Vector__3i32F4. It is not null-checked anywhere in the call chain (not in this function, and not in initialize_vector_3i32F4_as__aa_bb, which writes to hitbox_point->x__i32F4 without guarding it).
3. bb must be a non-null pointer to a writable Vector__3i32F4. Same null-check gap as aa.
4. The hitbox's width__quantity_u32 and height__quantity_u32 should be valid quantities; they are right-shifted and re-scaled by the callee.

Post-conditions:
1. aa is set to the hitbox's south-west corner: (position.x - half_width + velocity.x, position.y - half_height + velocity.y, position.z).
2. bb is set to the hitbox's north-east corner: (position.x + half_width + velocity.x, position.y + half_height + velocity.y, position.z).
3. All three fields (x__i32F4, y__i32F4, z__i32F4) of both aa and bb are assigned. The z component receives no half-extent offset and no velocity, matching the 2D-AABB semantics used throughout the collision module.
4. No global or struct state is read aside from hitbox; the hitbox itself is not mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its intent. The SW corner is computed with both offset signs negated (DIRECTION__SOUTH_WEST) and the NE corner with no sign negation (DIRECTION__NORTH_EAST), which is correct. Velocity is added to x and y by the callee for both corners, and z is passed through unchanged. The aa/bb naming matches the min/max AABB convention and the order matches the existing 3i32 variant (get_aa_bb_as__vectors_3i32_from__hitbox_aabb, lines 505-517) for consistency. No field is omitted and no reordering occurs.

Implementation Correctness:
Type compatibility — every argument type matches its parameter type exactly (Hitbox_AABB * -> p_hitbox_aabb, Vector__3i32F4 * -> hitbox_point, Direction__u8 -> corner_direction). No implicit conversions or truncation.
Undefined behavior risk — aa and bb are never null-checked: the function dereferences them via initialize_vector_3i32F4_as__aa_bb (which writes to hitbox_point->x__i32F4 at lines 149-158 and then 176-179) without ever validating hitbox_point. In debug builds the hitbox argument is guarded by the callee, but the output vectors are not. A NULL aa or bb would dereference NULL. In practice both known call sites (collision_resolver_aabb.c:293 and this module, lines 544-548) pass stack-local Vector__3i32F4 objects, so the exposure is low, but this is a latent defect and an inconsistency: the hitbox pointer is treated defensively while the output pointers are not. This mirrors the concern raised in the collision_node.h review for initialize_vector_3i32F4_as__aa_bb's NULL handling.
Validation — appropriate for a leaf output routine, but it is uneven: p_hitbox_aabb receives a debug-only guard while hitbox_point receives none. Consider either guarding all pointer parameters consistently or documenting that all inputs must be non-null at all call sites.

Side Effects:
Mutates the two output parameters aa and bb in their entirety (writes x, y, z of each). No other observable effects — no global state, no heap allocation, no I/O. The hitbox is read but not modified.
