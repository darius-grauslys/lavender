get_p_collision_node_entry_by__index_from__collision_node_pool — core/source/collisions/collision_node_pool.c

Returns a pointer to a Collision_Node_Entry within the pool's collision_node_entries array at the requested index.

Pre-conditions:
1. p_collision_node_pool must point to a valid, writable Collision_Node_Pool. Checked for null in debug builds only; in release builds (NDEBUG) it is the caller's responsibility.
2. index_of__collision_node_entry must be strictly less than MAX_QUANTITY_OF__HITBOX_AABB (256). Bounds-checked in debug builds only; in release builds it is the caller's responsibility.

Post-conditions:
1. If pre-conditions hold, returns a valid pointer to the Collision_Node_Entry at collision_node_pool->collision_node_entries[index_of__collision_node_entry].
2. If a pre-condition is violated in a debug build, returns 0 (NULL) and emits a debug_error; no entry is accessed.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent as a pure indexed accessor. It returns the address of the requested element of the collision_node_entries array, which is exactly what "get entry by index from collision node pool" promises. No off-by-one in the access itself: the array is sized MAX_QUANTITY_OF__HITBOX_AABB (256) and the guard rejects index >= 256.

Implementation Correctness:
Type compatibility — index_of__collision_node_entry is Index__u32 (uint32_t); it is used directly as the array subscript, which is compatible with size_t/pointer arithmetic with no truncation. The returned address is &collision_node_entries[...] of type Collision_Node_Entry *, matching the declared return type exactly. No implicit conversions.
Undefined behavior — in debug builds, a null pool or out-of-bounds index is guarded before any dereference or array access, so no null dereference or OOB access occurs. In release builds validation is absent, so an invalid caller value would be UB; this matches the codebase convention for these static inline helpers (see the sibling get_p_collision_node_by__index_from__collision_node_pool, which is also debug-guarded only).
Validation — debug-only validation is appropriate for this role as a low-level static inline accessor. The caller is responsible for correctness in release builds, consistent with the rest of the module.
Minor note — the debug error string says "index_of__collision_node_entry > MAX_QUANTITY_OF__HITBOX_AABB" but the actual guard uses >=; the symbol in the message text is slightly inaccurate (it also triggers when the index equals the max), but the behavior is correct and the message does not affect correctness.

Side Effects:
No side effects — the function is a read-only accessor. It does not mutate the pool; it only reads the array and returns an address. (The caller may subsequently mutate the returned entry, but that is outside this function's observable effects.)
