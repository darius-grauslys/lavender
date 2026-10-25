initialize_vector_3i32F4_as__aa_bb — core/source/collisions/core/aabb/hitbox_aabb.c

Computes a corner point of a Hitbox_AABB in world space, offsetting by the hitbox's velocity (x and y components only), for use in AABB-to-AABB collision corner checks.

Pre-conditions:
1. hitbox_point must be a non-null pointer to a writable Vector__3i32F4 (caller's responsibility; not checked).
2. p_hitbox_aabb must be a non-null pointer to a valid, already-initialized Hitbox_AABB struct (checked in debug builds only via assert-style guard).
3. corner_direction must be exactly one of DIRECTION__NORTH_EAST, DIRECTION__NORTH_WEST, DIRECTION__SOUTH_EAST, or DIRECTION__SOUTH_WEST; any other value (including DIRECTION__NONE) is a pre-condition violation.

Post-conditions:
1. hitbox_point->x__i32F4 is set to p_hitbox_aabb->position.x + half-width offset (signed per corner direction) + p_hitbox_aabb->velocity.x.
2. hitbox_point->y__i32F4 is set to p_hitbox_aabb->position.y + half-height offset (signed per corner direction) + p_hitbox_aabb->velocity.y.
3. hitbox_point->z__i32F4 is set to p_hitbox_aabb->position.z (velocity.z is intentionally NOT applied).
4. p_hitbox_aabb is unchanged (read-only).

Correctness Verdict: Correct

Semantic Alignment:
The implementation delegates corner-position computation to initialize_vector_3i32F4_as__aa_bb_without__velocity, which computes the position-space corner using half-width and half-height offsets signed by the corner direction. This function then adds the velocity x and y components to produce the moving world-space corner point. All three output fields (x, y, z) are assigned — no member is omitted. The z component intentionally receives no velocity offset, which is consistent with 2D AABB semantics where z serves as a layer/elevation dimension rather than a velocity-driven axis. The computation matches the semantic intent.

Implementation Correctness:
Type compatibility — velocity__3i32F4.x__i32F4 is i32F4 (int32_t) and hitbox_point->x__i32F4 is also i32F4; the += is i32F4 += i32F4 with no implicit conversion or truncation. Same for y. No type mismatch.
Undefined behavior — no pointer arithmetic; p_hitbox_aabb is null-guarded in debug builds; hitbox_point is not dereferenced null-guarded (consistent with the file's convention — caller's responsibility). No out-of-bounds access, no type punning.
Validation — the null guard on p_hitbox_aabb is debug-only, consistent with the rest of the file. No validation on hitbox_point or corner_direction beyond the switch default in the callee — appropriate for a low-level struct-computation function; the caller is responsible. Note: if corner_direction is invalid, the callee returns early leaving hitbox_point uninitialized, then the caller still adds velocity to the stale values — this is a pre-condition violation, not a bug, as the function contract requires a valid corner direction.

Side Effects:
hitbox_point is mutated — all three fields (x__i32F4, y__i32F4, z__i32F4) are written. p_hitbox_aabb is read-only (no mutation). debug_error may be called in debug builds if p_hitbox_aabb is null or if corner_direction is invalid (via the callee's switch default).

Lavender Initialization Semantics:
This is Lavender-style initialization (NOT RAII). The function does not acquire resources; it computes/clamps a derived point value based on existing hitbox state (position, dimensions, velocity) so it can be used in collision checks. "Initialize" here means "compute the initial state of this derived vector," consistent with the engine's convention of initialization-as-pool-cleanup/computation rather than resource acquisition.
