apply_x_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Adds an x-axis velocity delta to a hitbox's velocity vector (in place).

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object. Validated in debug builds only (under #ifndef NDEBUG); in release builds (NDEBUG defined) a null pointer would dereference.
2. x__velocity is any i32F4 (int32_t) value; no range constraint is imposed.

Post-conditions:
1. p_hitbox_aabb->velocity__3i32F4.x__i32F4 is incremented by x__velocity.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent — it adds the supplied x velocity delta to the x component of the hitbox's velocity vector. The arithmetic (+=) is the correct operation for an "apply" (delta) helper as opposed to a "set" (overwrite) helper.
However, there is a consistency / semantic-alignment concern: every other mutating function in this file (set_*, offset_*_position, set_*_velocity, set_*_acceleration, set_size_of__hitbox_aabb, set_velocity_to__hitbox_aabb, etc.) calls set_hitbox_aabb_as__dirty(p_hitbox_aabb) before mutating the struct. The analogous "offset_*_position" helpers — which are the closest peers to this "apply" family — DO mark the hitbox dirty. apply_x_velocity_to__hitbox_aabb does NOT. If the dirty flag is relied upon to gate recalculation of derived state (e.g. the cached AABB bounds), then derived state may be left stale after a velocity change. The sibling apply_y_velocity_to__hitbox_aabb and apply_z_velocity_to__hitbox_aabb (and the apply_velocity_to__hitbox_aabb wrapper that calls all three) share the same omission. This should be investigated and, if dirty-tracking is required for velocity, the dirty flag should be set here too.

Implementation Correctness:
Type compatibility — x__velocity is i32F4 (int32_t, see defines.h:54) and the target field p_hitbox_aabb->velocity__3i32F4.x__i32F4 is also i32F4 (Vector__3i32F4.x__i32F4). Exact match; no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The debug-only null check prevents dereference when p_hitbox_aabb == 0 in debug builds; in release builds the null-deref responsibility falls to the caller, which is consistent with the rest of this header's low-level inline helpers.
Validation — the debug-only null check is appropriate for this role. The function is a low-level inline helper; enforcing validation here in release builds is not required and would be inconsistent with the existing set_*/offset_* peers.
Minor — the debug_error string reads "apply_x_velocity_to__hitbox, p_hitbox_aabb == 0." (missing the trailing "_aabb"). This is consistent with how the apply_* family names itself in this file, but slightly diverges from the actual function name. Low priority; flag only for consistency.

Side Effects:
Mutates p_hitbox_aabb in place — specifically its velocity__3i32F4.x__i32F4 field is incremented. Does not touch any other field, does not allocate, does not touch global state.
