f_hitbox_aabb_collision_handler__default — core/source/collisions/collision_resolver_aabb.c

Resolves collision between two AABB hitboxes by computing corrective velocities that separate them.

Pre-conditions:
1. p_game must be a valid Game pointer (not dereferenced in body; required by function-pointer signature).
2. p_world must be a valid World pointer (not dereferenced in body; required by function-pointer signature).
3. p_hitbox_aabb__colliding must be a non-null pointer to a valid, active Hitbox_AABB.
4. p_hitbox_aabb__collided must be a non-null pointer to a valid, active Hitbox_AABB.

Post-conditions:
1. On the x-axis: if delta_x^2 < COLLISION_DELTA_THRESHOLD (4096), the x-velocity of both hitboxes is overwritten with corrective values derived from the ideal delta and the current delta, each right-shifted by 2.
2. On the y-axis: if delta_y^2 < COLLISION_DELTA_THRESHOLD, the y-velocity of both hitboxes is overwritten similarly.
3. If an axis does not meet the threshold condition, that axis's velocity is left unmodified.

Correctness Verdict: Correct

Semantic Alignment:
The function computes the ideal separation distance (sum of both hitbox dimensions per axis), then distributes the correction across both hitboxes — the collided hitbox receives (ideal - delta)/4 and the colliding hitbox receives (ideal + delta)/4. This is a symmetric elastic response that pushes the two hitboxes apart. The >> 2 divisor scales the correction for stable physics. The implementation matches the semantic intent with no drift or missing steps.

Implementation Correctness:
Type compatibility — width_of__collided + width_of__source is computed in Quantity__u32 (uint32_t) arithmetic and assigned to Signed_Quantity__i32 (int32_t). This is an implicit unsigned-to-signed conversion; acceptable for the domain (hitbox dimensions are small integers), but technically a narrowing conversion.
Undefined behavior — ideal_delta_x and ideal_delta_y are Signed_Quantity__i32 results of unsigned addition, so they are non-negative. delta_x and delta_y are int32_t constrained to |delta| <= 63 by the threshold check. Therefore ideal_delta +/- delta is non-negative and the >> 2 right-shift operates on positive signed integers, which is well-defined. No UB in practice.
Validation — no validation is needed; the caller (poll_for__collisions_within_this__collision_node) ensures both hitbox pointers are valid. The unused p_game and p_world parameters are mandated by the f_Hitbox_AABB_Collision_Handler function-pointer type.

Side Effects:
Mutates velocity__3i32F4.x__i32F4 on p_hitbox_aabb__colliding and p_hitbox_aabb__collided (if x-axis condition met), and velocity__3i32F4.y__i32F4 on both (if y-axis condition met). No other memory is read or written beyond the four input pointers.
