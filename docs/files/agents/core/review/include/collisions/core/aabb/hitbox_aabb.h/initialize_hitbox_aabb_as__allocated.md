initialize_hitbox_aabb_as__allocated — core/source/collisions/core/aabb/hitbox_aabb.c, lines 26-49

Sets up a Hitbox_AABB for use as an allocated (active-pool) entry: assigns a real serialization-header UUID, dimensions, zero velocity, and position, and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB. (Validated in debug builds via NDEBUG-guarded null check; no validation in release.)
2. uuid__u32 is any Identifier__u32 — no range constraint. Note: some callers pass IDENTIFIER__UNKNOWN__u32, which semantically marks the entry as deallocated despite the "as__allocated" name.
3. width and height are any Quantity__u32 (u32); no range validation.
4. position__3i32F4 is any Vector__3i32F4; no range validation.

Post-conditions:
1. p_hitbox_aabb->_serialization_header.uuid is set to uuid__u32.
2. p_hitbox_aabb->_serialization_header.size_of__struct is set to sizeof(Hitbox_AABB).
3. p_hitbox_aabb->width__quantity_u32 equals width.
4. p_hitbox_aabb->height__quantity_u32 equals height.
5. p_hitbox_aabb->velocity__3i32F4 is zeroed (x, y, z all 0).
6. p_hitbox_aabb->position__3i32F4 equals position__3i32F4 (via set_hitbox_aabb__position_with__3i32F4).
7. p_hitbox_aabb->hitbox_aabb_flags__u8 has the IS_DIRTY bit set (via the position setter).

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization (pool cleanup / allocation), NOT RAII — it populates a struct for entry into an active pool rather than acquiring resources. The function correctly performs its named task: assigning a real UUID (distinguishing it from initialize_hitbox_aabb, which uses IDENTIFIER__UNKNOWN__u32 for deallocation), setting dimensions, zeroing velocity, and setting position with a dirty flag.

However, ONE struct field is omitted:
- acceleration__3i16F8 is NOT assigned. The sibling velocity vector is explicitly zeroed (x=y=z=0), but the analogous acceleration vector (Vector__3i16F8) is left untouched. Unlike initialize_hitbox_aabb (the deallocated/reset counterpart), which performs memset(p_hitbox_aabb, 0, sizeof(Hitbox_AABB)) to zero the entire struct, this function does NOT zero the struct first. If the caller passes an uninitialized struct (e.g., a stack variable as seen in tests/core/source/collisions/test_suite_collisions_collision_resolver_aabb.c:44-53 and core/source/rendering/font/typer.c:38), the acceleration field will contain indeterminate values. In pool-allocated contexts (e.g., ui_element.c:326) where the struct was previously zeroed by initialize_serialization_header__contiguous_array, the acceleration is coincidentally zero. The omission is a latent bug that should be resolved by either zeroing acceleration explicitly or performing a memset at the top of the function.

No reordering or field-assignment errors are present among the fields that are assigned.

Implementation Correctness:
- Type compatibility: All parameter types match their target field types exactly. Identifier__u32 -> uuid, Quantity__u32 -> width/height/size_of__struct (u32), Vector__3i32F4 -> position (exact struct match). The literal 0 assigned to i32F4 (int32_t) velocity components is unambiguously representable. No implicit conversions or truncation.
- Undefined behavior: None. No pointer arithmetic, no null dereference (debug null check present, release callers are expected to pass valid pointers), no type punning, no out-of-bounds access. initialize_serialization_header writes only to the first two fields of the Serialization_Header (uuid and size_of__struct); sizeof(Hitbox_AABB) is the correct struct size.
- Validation: Appropriate for the function's role. Debug-only null check matches the codebase pattern used by all sibling functions (initialize_hitbox_aabb, set_hitbox_aabb__position_with__3i32F4, etc.). Caller responsibility for valid pointers is consistent with the low-level struct initialization layer.

Side Effects:
1. Mutates p_hitbox_aabb: writes _serialization_header (uuid + size), width__quantity_u32, height__quantity_u32, velocity__3i32F4 (all components to 0), and position__3i32F4 (delegates to set_hitbox_aabb__position_with__3i32F4).
2. Sets the IS_DIRTY flag on hitbox_aabb_flags__u8 via set_hitbox_aabb_as__dirty, which is called inside set_hitbox_aabb__position_with__3i32F4. The IS_ACTIVE bit is NOT set by this function; it is left to the caller to set separately (allocated != active in the Lavender model).
