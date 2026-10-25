set_z_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Sets the z-component of the velocity vector on a Hitbox_AABB struct and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.
2. z__velocity is any i32F4 value (int32_t fixed-point with 4-bit fractional precision); no range constraint.

Post-conditions:
1. p_hitbox_aabb->velocity__3i32F4.z__i32F4 is set to z__velocity.
2. The hitbox is marked as dirty via set_hitbox_aabb_as__dirty.
3. The function returns void.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly assigns the z-velocity field. The pattern matches sibling functions (set_x_velocity_to__hitbox_aabb at lines 369-385, set_y_velocity_to__hitbox_aabb at lines 387-399), which each set their respective component field identically. The function does what its name and intent dictate.

Implementation Correctness:
Type compatibility — z__velocity is i32F4 (int32_t per defines.h:54) and the target field velocity__3i32F4.z__i32F4 is also i32F4 (per Vector__3i32F4_t in defines_weak.h:77). No implicit conversions or truncation occur.
No undefined behavior — in debug builds the null pointer is checked (NDEBUG guard) and the function returns early on null. There is no pointer arithmetic, type punning, or out-of-bounds access. In release builds the null check is compiled out, consistent with the codebase convention for performance; the caller is responsible for passing a valid pointer.
Validation is appropriate — the debug-only null check matches the pattern used by all sibling setter functions in this file.

Side Effects:
1. Mutates p_hitbox_aabb->velocity__3i32F4.z__i32F4 to the value of z__velocity.
2. Calls set_hitbox_aabb_as__dirty, which sets the dirty flag in p_hitbox_aabb->hitbox_aabb_flags__u8.
