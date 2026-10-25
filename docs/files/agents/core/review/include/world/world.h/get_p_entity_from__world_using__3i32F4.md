get_p_entity_from__world_using__3i32F4 — core/source/world/world.c

Retrieves the entity located at a given 3D fixed-point position by resolving the position through the global space, collision node, and hitbox systems, ultimately returning the entity associated with the hitbox AABB found at that position.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_world must be a non-null pointer to a valid World object.
3. position__3i32F4 is any valid Vector__3i32F4 position; it need not be within an allocated global space.

Post-conditions:
1. On success, returns a pointer to the Entity whose hitbox AABB contains the given position.
2. If no global space exists at the position's chunk coordinates, the function will dereference a null pointer (undefined behavior).
3. If no collision node is found for the global space, the function will dereference a null pointer (undefined behavior).
4. If no hitbox AABB is found at the position, returns NULL (0).
5. If no entity is found for the hitbox's UUID, returns NULL (0).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation follows the intended lookup chain: position → global space → collision node → hitbox AABB → entity. The semantic intent is correctly expressed in the sequence of lookups. However, the implementation fails to guard against null returns at two critical points, which violates the safety expectations of this lookup function.

Implementation Correctness:
Type compatibility — all types are compatible. p_global_space is a Global_Space* and GET_UUID_P__u64 is applied to it (via the _serialization_header.uuid field). p_collision_node is a Collision_Node* and is passed to the hitbox lookup function. p_hitbox_aabb_manager is a Hitbox_AABB_Manager* obtained via a cast from void*. p_entity_manager is an Entity_Manager*. The final return is an Entity*. No implicit conversions or truncation issues.
Undefined behavior — the function contains two null pointer dereference bugs:
  a) After calling get_p_global_space_from__global_space_manager, the result p_global_space is immediately dereferenced via p_global_space->_serialization_header.uuid without any null check. This function can legitimately return NULL when the global space is not allocated or not present at the given chunk coordinates.
  b) After calling get_p_collision_node_by__uuid_64_from__collision_node_pool, the result p_collision_node is passed directly to get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node, which dereferences p_collision_node->p_linked_list__collision_node_entries__tail without a null check. The collision node lookup can return NULL if the UUID is not found in the pool.
Validation — no validation is present for p_game, p_world, p_global_space, or p_collision_node. Given the function's role as a lookup that may be called with arbitrary positions (including positions where no global space or collision node exists), this is insufficient. The caller should not be expected to pre-validate whether a global space exists at an arbitrary position.

Side Effects:
No side effects — the function performs read-only lookups across the world's global space manager, collision node pool, hitbox context, and entity manager. No state is mutated.
