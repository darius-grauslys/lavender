get_p_chunk_pool_from__world — core/include/world/world.h

Returns a pointer to the `chunk_pool` field within the `World` struct.

Pre-conditions:
1. `p_world` must be a non-null pointer to a valid, initialized `World` object.

Post-conditions:
1. Returns a valid `Chunk_Pool *` pointing to `p_world->chunk_pool`. The returned pointer is within the bounds of the `World` struct and remains valid as long as `p_world` is valid.

Correctness Verdict: Correct

Semantic Alignment:
The implementation directly returns `&p_world->chunk_pool`, which is semantically correct — it provides access to the chunk pool stored within the world. This is consistent with the pattern used by all other accessor functions in this header (e.g., `get_p_camera_from__world`, `get_p_collision_node_pool_from__world`).

Implementation Correctness:
Type compatibility — `p_world->chunk_pool` is of type `Chunk_Pool` (as defined in `core/include/defines.h`), and the function returns `Chunk_Pool *`, which matches `&p_world->chunk_pool` exactly. No implicit conversions or truncation.
No undefined behavior — there is no pointer arithmetic, no null dereference (the function assumes a non-null `p_world` per the pre-conditions), no type punning, and no out-of-bounds access. The `chunk_pool` field is a direct member of the `World` struct, so taking its address is always valid.
Validation is appropriate for the caller — this is a low-level accessor function. The caller is responsible for ensuring `p_world` is non-null and valid. This matches the pattern of other simple accessors in the same header (e.g., `get_p_camera_from__world`, `get_p_inventory_manager_from__world`). Note that some accessors in this header (like `get_p_entity_manager_from__world`) include debug-only null checks, but this function does not include one, which is acceptable for a simple inline accessor.

Side Effects:
No side effects — the function is a pure accessor that only reads the pointer value of `p_world` and returns the address of a struct member. No state is mutated.
