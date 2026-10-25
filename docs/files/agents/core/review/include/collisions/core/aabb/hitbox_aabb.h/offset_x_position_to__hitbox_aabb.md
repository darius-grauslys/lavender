offset_x_position_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Offsets the x-component of a hitbox's position by a given amount and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.
2. x__position is any i32F4 value (signed fixed-point, 4-bit fractional); no range constraint.

Post-conditions:
1. p_hitbox_aabb->position__3i32F4.x__i32F4 is incremented by x__position.
2. p_hitbox_aabb->hitbox_aabb_flags__u8 is set as dirty via set_hitbox_aabb_as__dirty.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent: it offsets the x position of the hitbox by the given delta and marks the hitbox dirty so the collision system knows the AABB needs recomputation. The arithmetic (+=) matches the "offset" naming. No semantic drift detected.

Implementation Correctness:
Type compatibility — x__position (i32F4) is added to position__3i32F4.x__i32F4 (i32F4). Exact type match; no implicit conversion or truncation.
No undefined behavior — the function performs a single field mutation via pointer dereference after the debug null guard, plus a flag-setting call. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — the null check is debug-only (#ifndef NDEBUG), consistent with the rest of the file (e.g., set_y_position_to__hitbox_aabb at line 300). In release builds the caller is responsible for ensuring p_hitbox_aabb is valid. This is acceptable for a low-level inline helper. Note the function is annotated with a TODO to remove it in favor of dispatch_game_action__hitbox, but that does not affect correctness.

Side Effects:
1. p_hitbox_aabb->hitbox_aabb_flags__u8 is mutated (dirty flag set) via set_hitbox_aabb_as__dirty.
2. p_hitbox_aabb->position__3i32F4.x__i32F4 is mutated (incremented by x__position).
