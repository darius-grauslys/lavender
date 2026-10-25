get_chunk_x_i32_from__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Returns the chunk X index (Signed_Index__i32) derived from the hitbox's position vector.

Pre-conditions:
1. p_hitbox must be a non-null pointer to a valid, initialized Hitbox_AABB object (non-null check is enforced in debug builds via NDEBUG guard; in release builds, null-safety is the caller's responsibility).

Post-conditions:
1. Returns the chunk X coordinate of the hitbox's position, computed via normalize_xyz_i32F4_to__chunk_xyz_i32 on the X component of the hitbox's position__3i32F4 field.
2. The Hitbox_AABB object is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function delegates to get_chunk_x_i32_from__vector_3i32F4(get_position_3i32F4_of__hitbox_aabb(p_hitbox)), which first extracts the position vector from the hitbox and then normalizes its X component into a chunk index. This matches the semantic intent of the function name exactly. No fields are omitted or reordered — the function is a thin accessor and does not construct any struct. Consistent with its sibling accessors get_chunk_y_i32_from__hitbox_aabb (line 574) and get_chunk_z_i32_from__hitbox_aabb (line 588).

Implementation Correctness:
- Type compatibility — the return type Signed_Index__i32 matches the return type of get_chunk_x_i32_from__vector_3i32F4 exactly. The parameter Hitbox_AABB *p_hitbox matches the parameter of get_position_3i32F4_of__hitbox_aabb (Hitbox_AABB *p_hitbox_aabb). No implicit conversions or truncation occur.
- Undefined behavior — no pointer arithmetic, no null dereference (null is caught and handled in debug), no type punning, no out-of-bounds access.
- Validation — the debug-only null check (guarded by #ifndef NDEBUG) is appropriate for a low-level accessor: it provides safety during development without adding release-mode overhead. The caller is responsible for ensuring validity in release builds, consistent with the codebase convention.

Side Effects:
No side effects in release builds. In debug builds, the only side effect is the call to debug_error when p_hitbox is null, which is a diagnostic log and does not alter program state. The function does not mutate the Hitbox_AABB object.
