release_hitbox_aabb_from__hitbox_aabb_manager — core/source/collisions/core/aabb/hitbox_aabb_manager.c

Removes a Hitbox_AABB from the manager's pointer-array of active records, detaches it from the collision system, and reinitializes (clears) the struct to pool-ready state.

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager whose pool (pM_pool_of__hitboxes) and pointer-array (pM_ptr_array_of__hitbox_records) are allocated with at least quantity_of__hitboxes slots.
2. p_hitbox_aabb must point within pM_pool_of__hitboxes (validated in debug via pointer subtraction on line 253-254 and a bounds check on line 255). It must not be NULL — if NULL, the pointer subtraction on line 253-254 is technically undefined behavior (address 0 minus a valid pointer is UB per the C standard, though it usually "works" on platforms where NULL is address 0).
3. p_game must be a non-null pointer to a valid Game object. is_world_allocated_for__game(p_game) on line 288 dereferences p_game->pM_world; if p_game is NULL this is undefined behavior. Unlike p_hitbox_aabb_manager, p_game is NOT validated even in debug builds (#ifndef NDEBUG) — this is a validation gap.

Post-conditions:
1. If p_hitbox_aabb was found in pM_ptr_array_of__hitbox_records, it has been removed via swap-with-last-and-null-out: the entry at the found index is overwritten with the entry at index_of__next_hitbox_aabb_in__records (after decrementing it), the old last slot is set to NULL, and index_of__next_hitbox_aabb_in__records is decremented.
2. If the world was allocated (p_game->pM_world != NULL) and a Global_Space was found for the hitbox's position, the hitbox's collision-node entry (identified by UUID) has been removed from that Global_Space's collision node.
3. p_hitbox_aabb has been reinitialized to a zeroed state via initialize_hitbox_aabb (memset to 0 plus serialization-header reset for deallocation), making it safe to return to the free pool.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent: release a hitbox from the manager. The swap-remove on lines 275-283 correctly removes the pointer from the records array while maintaining contiguity of active entries (0 to index_of__next_hitbox_aabb_in__records - 1). The collision-node removal on lines 287-303 correctly detaches the hitbox from the spatial partitioning system. The final initialize_hitbox_aabb call on line 305 is correct Lavender-style initialization (clearing to pool-ready state, NOT RAII resource teardown).

However, two issues prevent full semantic alignment:
- The loop on line 261 uses p_hitbox_aabb_manager->quantity_of__hitboxes as the upper bound, but only index_of__next_hitbox_aabb_in__records entries are active (non-NULL) in the pointer array. The break-on-NULL on lines 269-272 compensates for this, so the function still works correctly in practice, but the loop bound should be index_of__next_hitbox_aabb_in__records for semantic clarity and to avoid iterating over irrelevant NULL slots.
- When the hitbox is not found in the pointer array (NULL encountered), the function still proceeds to remove the collision-node entry and reinitialize the struct. This is actually the correct behavior (the hitbox may still be registered in the collision system even if absent from the records array), but the debug_warning on line 270 could be misleading — it implies a failure when the subsequent operations are still valid.

Implementation Correctness:
- Type compatibility: All types match correctly. The void* cast in the ternary on line 287 is appropriate. GET_UUID_P yields Identifier__u32 which matches remove_entry_from__collision_node's uuid parameter. No implicit conversions or truncation.
- Undefined behavior: No out-of-bounds access — the loop condition on line 262 uses quantity_of__hitboxes (which bounds the ptr_array allocation), and get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager also validates against quantity_of__hitboxes in debug. The pointer subtraction on line 253-254 is valid only when p_hitbox_aabb points within the pool; in debug this is bounds-checked on line 255, but p_hitbox_aabb is not NULL-checked before the subtraction (UB if NULL). In release builds (when NDEBUG is defined), none of the debug validation runs, so all pointer usage is caller's responsibility.
- Missing p_game validation: is_world_allocated_for__game(p_game) on line 288 dereferences p_game without any null check (not even in debug). This is inconsistent with the p_hitbox_aabb_manager null check on lines 249-252 and should be addressed with a debug-only guard.
- No type punning. No broken pointer arithmetic in normal operation (valid range confirmed by debug check).

Side Effects:
1. Mutates p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records (swap-remove of the target pointer, nulling of the vacated last slot).
2. Decrements p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records by 1 (if the hitbox was found in the records array).
3. If world is allocated and global space exists: calls remove_entry_from__collision_node, which mutates the Collision_Node's linked list and may release a Collision_Node_Entry back to the pool.
4. Mutates p_hitbox_aabb via initialize_hitbox_aabb (memset to 0, serialization-header reset).
