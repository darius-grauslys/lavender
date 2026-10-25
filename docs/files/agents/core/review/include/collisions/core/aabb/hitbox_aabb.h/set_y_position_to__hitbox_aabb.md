set_y_position_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Sets the y-component of the hitbox's position vector and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.
2. y__position is any i32F4 value (fixed-point with 4 fractional bits); no range constraint.

Post-conditions:
1. p_hitbox_aabb->position__3i32F4.y__i32F4 is set to y__position.
2. p_hitbox_aabb is marked dirty via set_hitbox_aabb_as__dirty.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly sets the y-component of the hitbox position and marks the hitbox as dirty, which is consistent with the engine's dirty-flag pattern used by all sibling setters (set_x_position_to, set_z_position_to, etc.). The TODO comment indicates this function is deprecated in favor of dispatch_game_action__hitbox, but the implementation itself fulfills its stated purpose.

Implementation Correctness:
Type compatibility — the parameter y__position is i32F4 and the target field p_hitbox_aabb->position__3i32F4.y__i32F4 is also i32F4. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (null is checked in debug builds), no type punning, no out-of-bounds access.
Validation — the null check is guarded by #ifndef NDEBUG, which is appropriate for this low-level setter; the caller is responsible for passing a valid pointer in release builds.

Side Effects:
1. Mutates p_hitbox_aabb->position__3i32F4.y__i32F4 to the value of y__position.
2. Mutates p_hitbox_aabb->hitbox_aabb_flags__u8 by setting the dirty flag via set_hitbox_aabb_as__dirty.
