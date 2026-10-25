initialize_hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Resets a Hitbox_AABB to a deallocated, pool-returnable state (Lavender-style initialization, not RAII).

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object. (Checked only in debug builds via NDEBUG guard.)

Post-conditions:
1. All bytes of the Hitbox_AABB struct are zeroed via memset (position, velocity, acceleration, width, height, and hitbox_aabb_flags all become 0).
2. _serialization_header.uuid is set to IDENTIFIER__UNKNOWN__u32 (0xFFFFFFFF), marking the struct as deallocated so is_serialized_struct__deallocated returns true.
3. _serialization_header.size_of__struct is set to sizeof(Hitbox_AABB).

Correctness Verdict: Correct

Semantic Alignment:
This is Lavender-style initialization (pool cleanup, not RAII) — not resource acquisition. The memset zeroes all struct fields to their initial/default state, then the serialization header is explicitly set to the deallocated marker (IDENTIFIER__UNKNOWN__u32), indicating the slot can be returned to or reused from a free pool. The two-step approach is intentional: memset alone would set uuid to 0, but the proper deallocated sentinel is 0xFFFFFFFF, so initialize_serialization_header_for__deallocated_struct must run afterward to set the correct uuid. All struct fields end in a known default state.

Implementation Correctness:
Type compatibility — sizeof(Hitbox_AABB) (size_t, 64-bit) is implicitly narrowed to Quantity__u32 (uint32_t) when passed to initialize_serialization_header_for__deallocated_struct. For this small struct (Serialization_Header + 3 vectors + 2 u32s + u8) the value is well within uint32 range, so no truncation occurs in practice; this is a codebase-wide convention.
No undefined behavior — memset on a valid (non-null) pointer is safe; initialize_serialization_header_for__deallocated_struct receives a valid pointer to the _serialization_header field (first member of the struct); no null dereference, no pointer arithmetic, no type punning, no out-of-bounds access.
Validation — the debug-only null check is appropriate for this low-level initialization function. In release builds (NDEBUG defined), the caller is responsible for ensuring p_hitbox_aabb is valid, consistent with the codebase-wide convention.

Side Effects:
Mutates the Hitbox_AABB struct in-place: zeroes all bytes via memset, then overwrites _serialization_header.uuid to IDENTIFIER__UNKNOWN__u32 (0xFFFFFFFF) and _serialization_header.size_of__struct to sizeof(Hitbox_AABB).
