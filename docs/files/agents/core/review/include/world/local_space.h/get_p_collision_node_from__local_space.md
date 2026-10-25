get_p_collision_node_from__local_space — core/include/world/local_space.h

Returns the Collision_Node pointer associated with a Local_Space by delegating through the Local_Space's Global_Space.

Pre-conditions:
1. p_local_space may be NULL; the function handles this case by returning 0.
2. If p_local_space is non-null, it must point to a valid Local_Space object whose p_global_space member is non-null. A non-null p_local_space with a NULL p_global_space is NOT safely handled (see Implementation Correctness below).

Post-conditions:
1. Returns a pointer to the Collision_Node stored in the local space's associated Global_Space, or 0 if p_local_space is NULL.
2. No state is mutated — this is a pure accessor function.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to retrieve the Collision_Node from the Local_Space's Global_Space. The delegation chain is correct: it gets the Global_Space from the Local_Space, then retrieves the Collision_Node from that Global_Space. The semantic intent is sound, but the implementation has a null-safety gap in the downstream callee.

Implementation Correctness:
Type compatibility — all types match correctly. Local_Space * is passed to get_p_global_space_from__local_space (which expects Local_Space *), and Global_Space * is passed to get_p_collision_node_from__global_space (which expects Global_Space *). No implicit conversions or truncation.

Undefined behavior — **null pointer dereference risk**. The function `get_p_collision_node_from__global_space` (in global_space.h, line 212) does NOT null-check its `p_global_space` parameter; it directly dereferences it via `p_global_space->p_collision_node`. This means if `p_local_space` is non-null but `p_local_space->p_global_space` is NULL, the call chain will dereference a null pointer. This is inconsistent with the sibling function `get_p_chunk_from__global_space` (line 196), which does null-check before accessing `p_global_space->p_chunk`. The caller `get_p_collision_node_from__local_space` checks p_local_space for null but does not guard against a null p_global_space returned by `get_p_global_space_from__local_space`.

Validation — the null check on p_local_space is appropriate, but additional null-checking on the intermediate Global_Space pointer is missing. This is a bug in the implementation, not just a caller responsibility, because the function is designed to handle the null-local-space case gracefully (returning 0) and should maintain the same safety guarantee for a null global_space.

Side Effects:
No side effects — this is a pure accessor function that reads struct members and returns a pointer. No state is mutated.
