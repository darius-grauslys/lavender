set_z_position_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h, lines 314-326

Sets the z-component of the hitbox position to the given value and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (debug-only null check via debug_error + early return).
2. z__position may be any i32F4 value (no range constraint).

Post-conditions:
1. p_hitbox_aabb is mutated: position__3i32F4.z__i32F4 is set to z__position.
2. The hitbox's dirty flag is set to true (via set_hitbox_aabb_as__dirty).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent — it sets only the z-component of the position, leaving x and y untouched, consistent with the sibling functions set_x_position_to__hitbox_aabb and set_y_position_to__hitbox_aabb. Marking the hitbox as dirty after a position change is semantically correct since the AABB bounds depend on position. The function is annotated with a TODO: REMOVE, must use dispatch_game_action__hitbox instead — this is a deprecation note indicating the function should not be called directly when an entity is registered to the collision system, but it is not a correctness bug in the implementation itself.

Implementation Correctness:
Type compatibility — the parameter z__position (i32F4, which is int32_t) matches the target field z__i32F4 (i32F4) exactly. No implicit conversions or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference on the hot path (null is guarded in debug), no type punning, no out-of-bounds access.
Validation — the null check is debug-only (#ifndef NDEBUG), which is consistent with the codebase convention seen in all sibling set_*_position_to__hitbox_aabb functions. This is appropriate for a low-level inline function; production callers are expected to ensure non-null pointers.

Side Effects:
Mutates the pointed-to Hitbox_AABB struct: sets the dirty flag and writes the z-component of position__3i32F4. No other observable state is modified.
