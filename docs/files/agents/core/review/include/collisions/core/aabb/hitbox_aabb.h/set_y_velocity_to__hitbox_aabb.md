set_y_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Sets the Y-component of the hitbox's velocity vector and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (checked in debug builds via NDEBUG guard).
2. y__velocity is any i32F4 (int32_t); a 4-bit-fractional fixed-point value representing the Y velocity.

Post-conditions:
1. p_hitbox_aabb->velocity__3i32F4.y__i32F4 is set to y__velocity.
2. p_hitbox_aabb's dirty flag bit is set (via set_hitbox_aabb_as__dirty), indicating cached state must be recomputed.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its intent — assigning the Y velocity component and marking dirty. This function is structurally identical to its siblings set_x_velocity_to__hitbox_aabb (line 374) and set_z_velocity_to__hitbox_aabb (line 402), differing only in which vector component is written. The dirty flag is set before the assignment, which is the correct ordering used consistently across all setter functions in this file.

Implementation Correctness:
Type compatibility — y__velocity (i32F4, int32_t) is assigned to velocity__3i32F4.y__i32F4 (i32F4, int32_t). Exact type match with no implicit conversion or truncation.
No undefined behavior — no pointer arithmetic, no null dereference in debug (null is checked), no type punning, no out-of-bounds access. The field velocity__3i32F4.y__i32F4 is a direct struct member access on a valid pointer.
Validation — the null-pointer check is guarded by #ifndef NDEBUG, consistent with the Lavender pattern throughout this file. In release builds validation is omitted and responsibility falls on the caller, which is the established convention here.

Side Effects:
Mutates p_hitbox_aabb: sets the dirty flag bit on hitbox_aabb_flags__u8 and writes the y velocity component. No other state is touched.
