apply_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Delegates to apply_x/y/z_velocity_to__hitbox_aabb, adding each component of the given Vector__3i32F4 to the corresponding component of the Hitbox_AABB velocity vector.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.
2. vector is expected to be a non-null pointer to a Vector__3i32F4 object. However, this is NOT validated — only p_hitbox_aabb is null-checked in debug builds. If vector is NULL, dereferencing vector->x__i32F4 (and y__, z__) causes undefined behavior.

Post-conditions:
1. p_hitbox_aabb->velocity__3i32F4.x__i32F4 is incremented by vector->x__i32F4.
2. p_hitbox_aabb->velocity__3i32F4.y__i32F4 is incremented by vector->y__i32F4.
3. p_hitbox_aabb->velocity__3i32F4.z__i32F4 is incremented by vector->z__i32F4.
4. No dirty flag is set on the Hitbox_AABB (see Issues).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation correctly delegates to the three per-axis apply functions, which each add their respective velocity component to velocity__3i32F4. The intent — "add this velocity vector to the hitbox's velocity" — is fulfilled by the computation itself. However, the function omits a call to set_hitbox_aabb_as__dirty, which is present in every sibling velocity mutation function (set_x/y/z_velocity_to__hitbox_aabb at lines 374-413, and set_velocity_to__hitbox_aabb at line 458). If the dirty flag is meant to signal that the hitbox's spatial state needs recalculation, omitting it here is a semantic drift from the established pattern.

Implementation Correctness:
Type compatibility — vector->x__i32F4, vector->y__i32F4, and vector->z__i32F4 are all i32F4 (int32_t, per defines_weak.h:32), and apply_x/y/z_velocity_to__hitbox_aabb each take i32F4. Types match exactly. No implicit conversions or truncation.
Undefined behavior — A null vector pointer is not checked. In debug builds only p_hitbox_aabb is validated; vector is dereferenced unconditionally at lines 278-280. If vector is NULL, this is a null pointer dereference (undefined behavior). In release builds (NDEBUG defined), even the p_hitbox_aabb check is stripped, so a null p_hitbox_aabb would also cause undefined behavior.
Validation — The debug-only null check for p_hitbox_aabb is consistent with the codebase pattern. However, the absence of a corresponding check for vector is a gap. The caller may reasonably pass a NULL vector, and the function provides no protection.
Missing dirty flag — set_hitbox_aabb_as__dirty is not called, unlike all sibling velocity setters. This may be an oversight (see Semantic Alignment).

Side Effects:
Mutates p_hitbox_aabb->velocity__3i32F4 by incrementing each component (x, y, z) by the corresponding component from vector. Does not set the hitbox dirty flag. Does not modify vector.

Issues Found:
1. (Critical) Missing null check for vector: The debug null guard only covers p_hitbox_aabb. A null vector causes a null pointer dereference. Recommend adding:
   #ifndef NDEBUG
       if (!vector) {
           debug_error("apply_velocity_to__hitbox_aabb, vector == 0.");
           return;
       }
   #endif
2. (High) Missing set_hitbox_aabb_as__dirty call: All sibling functions that mutate velocity (set_x/y/z_velocity_to__hitbox_aabb, set_velocity_to__hitbox_aabb) call set_hitbox_aabb_as__dirty before mutation. apply_velocity_to__hitbox_aabb does not. This is likely an oversight that could cause stale spatial data in collision/collision-node systems. Recommend adding a call before delegating to the per-axis functions.
3. (Low) Inconsistent error message: The debug error string says "apply_velocity_to__hitbox" instead of the full function name "apply_velocity_to__hitbox_aabb". While consistent with the sibling functions' naming convention, it diverges from the actual function name and can confuse debugging.
4. (Low) TODO comment at lines 263-266 flags an unexplained requirement to take vector as a pointer ("really funny stuff happens when we don't take vector as a pointer"). The sibling function set_velocity_to__hitbox_aabb at line 458 takes Vector__3i32F4 by value without issue. The root cause of the pointer requirement is undocumented. Recommend investigating and resolving the TODO, or removing the pointer parameter if by-value is safe.
