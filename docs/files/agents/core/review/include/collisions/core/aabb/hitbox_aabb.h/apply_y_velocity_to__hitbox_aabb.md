apply_y_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Adds a y-axis velocity delta to a hitbox's velocity vector (in place).

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object. Validated in debug builds only (under #ifndef NDEBUG); in release builds (NDEBUG defined) a null pointer would dereference.
2. y__velocity is any i32F4 (int32_t) value; no range constraint is imposed.

Post-conditions:
1. p_hitbox_aabb->velocity__3i32F4.y__i32F4 is incremented by y__velocity.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent — it adds the supplied y velocity delta to the y component of the hitbox's velocity vector. The arithmetic (+=) is the correct operation for an "apply" (delta) helper as opposed to a "set" (overwrite) helper.
However, there is a consistency / semantic-alignment concern (identical to the sibling apply_x_velocity_to__hitbox_aabb and apply_z_velocity_to__hitbox_aabb, and the apply_velocity_to__hitbox_aabb wrapper): every other mutating function in this header — offset_x/y/z_position_to__hitbox_aabb (lines 334-371), set_x/y/z_velocity_to__hitbox_aabb (lines 373-413), set_x/y/z_acceleration_to__hitbox_aabb (lines 415-455), and set_velocity_to__hitbox_aabb (line 458) — calls set_hitbox_aabb_as__dirty(p_hitbox_aabb) before mutating the struct. The apply_* family does NOT. If the dirty flag is relied upon to gate recalculation of derived state (e.g. the cached AABB bounds used by is_hitbox_aabb__colliding and the collision resolver), then derived state may be left stale after a velocity change. This should be investigated and, if dirty-tracking is required for velocity, the dirty flag should be set here too.

Implementation Correctness:
Type compatibility — y__velocity is i32F4 (int32_t, see defines_weak.h:32 / defines.h:54) and the target field p_hitbox_aabb->velocity__3i32F4.y__i32F4 is also i32F4 (Vector__3i32F4.y__i32F4, defines_weak.h:76-78). Exact match; no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. Unlike apply_velocity_to__hitbox_aabb (which dereferences an unvalidated vector pointer), the scalar i32F4 parameter cannot be null, so there is no null-dereference surface. The debug-only null check on p_hitbox_aabb prevents dereference when p_hitbox_aabb == 0 in debug builds; in release builds the null-deref responsibility falls to the caller, which is consistent with the rest of this header's low-level inline helpers (offset_*_position, set_*_velocity, set_*_acceleration).
Validation — the debug-only null check is appropriate for this role. The function is a low-level inline helper; enforcing validation here in release builds is not required and would be inconsistent with the existing set_*/offset_* peers.
Inconsistent error message — the debug_error string reads "apply_y_velocity_to__hitbox, p_hitbox_aabb == 0." (missing the trailing "_aabb"), diverging from the actual function name. This is consistent with how the apply_* family names itself in this file (apply_x/apply_y/apply_z all use the shorter form), so flag only for consistency; low priority.

Side Effects:
Mutates p_hitbox_aabb in place — specifically its velocity__3i32F4.y__i32F4 field is incremented. Does not touch any other field, does not allocate, does not touch global state. Does not set the hitbox dirty flag (see Semantic Alignment).

Issues Found:
1. (Medium) Missing set_hitbox_aabb_as__dirty call: Every sibling mutating function in this header (offset_*_position, set_*_velocity, set_*_acceleration, set_velocity_to__hitbox_aabb) calls set_hitbox_aabb_as__dirty(p_hitbox_aabb) before mutating velocity__/position__/acceleration. The entire apply_* family (apply_x/y/z_velocity_to__hitbox_aabb and apply_velocity_to__hitbox_aabb) omits it. This is likely an oversight that could cause stale spatial data in the collision/collision-node systems that rely on the dirty flag. Recommend adding set_hitbox_aabb_as__dirty(p_hitbox_aabb); before the += at line 246, consistent with the established pattern.
2. (Low) Inconsistent debug_error naming: the message uses "apply_y_velocity_to__hitbox" rather than the full function name "apply_y_velocity_to__hitbox_aabb". Consistent across the apply_* family but diverges from the actual symbol name; low priority for debuggability.
