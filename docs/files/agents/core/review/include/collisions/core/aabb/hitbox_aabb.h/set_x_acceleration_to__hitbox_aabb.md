set_x_acceleration_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Sets the x-component of the hitbox's acceleration vector and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (only validated in debug builds; see Implementation Correctness).
2. x__acceleration is an i16F8 (int16_t) value with no range constraint; any i16F8 value is accepted.

Post-conditions:
1. p_hitbox_aabb->acceleration__3i16F8.x__i16F8 is set to x__acceleration.
2. The dirty bit in p_hitbox_aabb->hitbox_aabb_flags__u8 is set via set_hitbox_aabb_as__dirty. The y and z components of acceleration__3i16F8 are left unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function is a per-axis field setter: it writes only the x-component of the acceleration vector, consistent with its name. It is not a struct initializer, so the question of assigning all struct fields does not apply. The dirty flag is set, which is the expected side effect for any mutation of a Hitbox_AABB field — this matches the pattern used by all sibling setters (set_y_acceleration_to__hitbox_aabb, set_z_acceleration_to__hitbox_aabb, set_x_velocity_to__hitbox_aabb, etc.).

Implementation Correctness:
Type compatibility: x__acceleration (i16F8 = int16_t) is assigned to acceleration__3i16F8.x__i16F8 (i16F8 = int16_t). The types match exactly; no implicit conversion or truncation occurs.
Undefined behavior: No pointer arithmetic, no type punning, no out-of-bounds access. The null check on p_hitbox_aabb is guarded by #ifndef NDEBUG, so it executes only in debug builds. In release builds (NDEBUG defined) there is no null check — this is intentional and consistent with the codebase's pattern of omitting validation in low-level setters. Validation is the caller's responsibility; a valid p_hitbox_aabb is a pre-condition.
Validation scope: The debug-only null guard and debug_error call are appropriate for the function's role as a low-level struct field setter.

Side Effects:
Mutates two fields of the struct pointed to by p_hitbox_aabb:
1. Sets p_hitbox_aabb->acceleration__3i16F8.x__i16F8 = x__acceleration.
2. Sets the dirty flag via set_hitbox_aabb_as__dirty (sets HITBOX_FLAG__IS_DIRTY in p_hitbox_aabb->hitbox_aabb_flags__u8).
No other observable state is modified.
