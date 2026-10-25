set_x_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h, lines 373-385

Sets the x-component of the hitbox's velocity vector to a given value and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (the NDEBUG-guarded debug check rejects a null pointer and returns early).
2. x__velocity is any i32F4 (a 32-bit fixed-point scalar); no range constraint is imposed by the function.

Post-conditions:
1. p_hitbox_aabb is mutated so that velocity__3i32F4.x__i32F4 equals x__velocity.
2. The dirty flag of p_hitbox_aabb is set (its other velocity components y and z are untouched).
3. When NDEBUG is defined, the null check is elided and the caller is responsible for passing a valid pointer.

Correctness Verdict: Correct

Semantic Alignment:
The function does exactly what its name intends — it sets the x velocity component (rather than adding to it, which is the role of the sibling add_x_velocity_to__hitbox_aabb). The computation matches the intent: a single field assignment of the matching type.

Implementation Correctness:
Type compatibility — the parameter x__velocity is i32F4 (typedef int32_t at defines.h:54) and is assigned to velocity__3i32F4.x__i32F4, which is also i32F4 (Vector__3i32F4.x__i32F4 at defines_weak.h:77). Exact type match; no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference in the NDEBUG path (a null is rejected before dereference in debug builds; in release builds the caller is responsible), no type punning, no out-of-bounds access. The member access p_hitbox_aabb->velocity__3i32F4.x__i32F4 uses a direct, in-range struct field.
Validation — the NDEBUG-guarded null check is appropriate for a low-level inline setter; validation is the caller's responsibility in release builds, consistent with the rest of the file's setters (set_y_velocity_to__hitbox_aabb, set_z_velocity_to__hitbox_aabb, set_x_acceleration_to__hitbox_aabb, etc.).
Consistency — follows the identical structure used by all sibling setters in the file, so the dirty flag is set before the field is written.

Side Effects:
Mutates p_hitbox_aabb: sets its dirty flag (via set_hitbox_aabb_as__dirty) and overwrites velocity__3i32F4.x__i32F4 with the new value. No other state, globals, or memory are touched.
