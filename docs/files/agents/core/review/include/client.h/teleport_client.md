teleport_client — core/source/client.c, lines 116-166

Teleports a client to a new position: removes the client's stale collision entry, sets the hitbox to the new position, updates the local space manager center, and schedules an asynchronous process callback (m_process__teleport_client) to re-register the collision record at the new position.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game object with a valid hitbox context, world, collision node pool, and process manager.
2. p_client must be a non-null pointer to a valid Client object that has been initialized with a UUID (Client is cast to Serialization_Header* via GET_UUID_P to read its uuid field).
3. position__3i32F4 is any valid Vector__3i32F4 value representing the target position; no range constraint is imposed by this function.
4. The client's UUID does not necessarily need to resolve to a hitbox entry; if no hitbox is found for the UUID, the hitbox-related mutations are skipped and only the local space manager is updated.

Post-conditions:
1) If the client's hitbox exists in the hitbox AABB manager:
   - The stale collision node entry for the hitbox is removed from the world's collision node pool (only if a local space is found for the hitbox's current position).
   - The hitbox's position is set to position__3i32F4.
2) The client's local space manager center is set to the chunk-vector form of the new position (vector_3i32F4_to__chunk_vector_3i32).
3) A new Process is allocated and scheduled via run_process with callback m_process__teleport_client, priority PROCESS_PRIORITY__0_MAXIMUM, and flag PROCESS_FLAG__IS_CRITICAL.
4) The new process's process_valueA__i32 is set to the client's UUID (GET_UUID_P).
5) The new Process* is returned to the caller.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of a teleport operation. It:
- Retrieves the client's hitbox via UUID and removes the old collision entry before moving the hitbox, preventing the hitbox from remaining registered at its old position.
- Sets the hitbox to the new position after removing the old entry, ensuring consistency between the hitbox state and the collision pool.
- Updates the local space manager center to the new position so subsequent local-space lookups are coherent.
- Schedules the m_process__teleport_client callback to re-add the collision record at the new position asynchronously (the removal-then-deferred-readd pattern avoids a transient state where the hitbox occupies two collision slots simultaneously).
This function is a teleportation action, not a Lavender-style initialization. It does not clean a struct to its initial conditions or remove a struct from a pool for return to a free pool. The only pool manipulation (remove_entry_from__collision_node) is removing a collision entry so it can be re-added at the new position — consistent with Lavender's pool-management pattern but not an initialization. The init/RAII caveat is not triggered.

Implementation Correctness:
Type compatibility — GET_UUID_P(p_client) returns Identifier__u32 (uint32_t), which is stored directly into process_valueA__i32 (int32_t / i32). This is a signed/unsigned store, but for UUID identifiers (small positive values from a hashed contiguous array) it is safe and consistent: the downstream callback m_process__teleport_client reads process_valueA__i32 back as Identifier__u32 and passes it to get_p_client_by__uuid_from__game, which takes Identifier__u32. The explicit cast (Hitbox_AABB_Manager*) matches the return type of get_pV_hitbox_manager_from__hitbox_context. Vector__3i32F4 is passed consistently to set_hitbox_aabb__position_with__3i32F4 and vector_3i32F4_to__chunk_vector_3i32.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The function null-checks p_hitbox_of__client and p_local_space before use. p_process from run_process is dereferenced without a null check, but run_process is the engine's standard process allocator and is expected to return a valid pointer; this is consistent with the caller-responsibility pattern used throughout the codebase (an IS_CRITICAL flag implies allocation failure would be handled at a higher level).
Validation — appropriate for a high-level coordinator. Null checks are performed for p_hitbox_of__client and p_local_space (objects that may legitimately not exist for a given UUID). p_game and p_client are not null-checked, consistent with the codebase convention where high-level callers are responsible for passing valid pointers. A debug_error is emitted when the hitbox is not found in local space.

Side Effects:
1. Mutates the client's hitbox position (via set_hitbox_aabb__position_with__3i32F4).
2. Removes a collision node entry from the world's collision node pool (via remove_entry_from__collision_node).
3. Mutates the client's local space manager center (via set_center_of__local_space_manager).
4. Allocates and schedules a new Process via the game's process manager (via run_process), which performs further mutations when executed asynchronously by m_process__teleport_client (out of scope for this function's own side-effect trace).
5. Writes the client's UUID to the new process's process_valueA__i32 field.
6. Emits a debug_error log if the client's hitbox is not found in local space.
