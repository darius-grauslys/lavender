get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node — core/source/collisions/collision_node.c

Iterates the linked list of Collision_Node entries (from tail to head), looks up each entry's Hitbox_AABB by UUID via the hitbox AABB manager, and returns a pointer to the first hitbox whose AABB contains the given Vector__3i32F4. Returns null (0) if the node's entry list is empty or if no containing hitbox is found.

Pre-conditions:
1. p_collision_node must be a non-null pointer to a valid Collision_Node. The function dereferences it immediately without a null guard.
2. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager. The callee get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager performs a debug-mode (NDEBUG) null guard that returns 0, but in release builds a null manager yields undefined behavior, so the caller must guarantee non-null.
3. vector__3i32F4 is passed by value and has no constraints — any Vector__3i32F4 is acceptable.

Post-conditions:
1. Returns a pointer to the first Hitbox_AABB (in linked-list order, starting from the tail) whose AABB contains vector__3i32F4, or null (0) if p_collision_node has no entries or no containing hitbox was found.
2. The collision node and hitbox manager are not modified; all reads are observable-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the semantic intent. The top guard returns 0 for an empty list (null tail), then a do-while traverses p_previous_entry from tail toward head. Because the guard guarantees p_entry (initialized to tail) is non-null before the first body executes, the do-while is safe: p_entry is only ever null when the while-assignment of p_previous_entry terminates the loop, so the body always dereferences a non-null pointer. At least one iteration is guaranteed, which is correct since a non-null tail implies at least one entry exists.

Type compatibility — every parameter type matches its callee exactly:
- p_hitbox_aabb_manager (Hitbox_AABB_Manager *) -> param 1 of get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager (Hitbox_AABB_Manager *).
- p_entry->uuid_of__hitbox__u32 (Identifier__u32) -> param 2 (Identifier__u32).
- vector__3i32F4 (Vector__3i32F4) -> param 1 of is_vector_3i32F4_inside__hitbox_aabb (Vector__3i32F4).
- p_hitbox_aabb (Hitbox_AABB *) -> param 2 (Hitbox_AABB *).
- The returned Hitbox_AABB * matches the declared return type. No implicit conversions or truncation.

Undefined behavior — none introduced by this function:
- No pointer arithmetic, no type punning, no out-of-bounds access.
- p_entry is guaranteed non-null inside the loop body (see Semantic Alignment), so p_entry->uuid_of__hitbox__u32 and p_entry->p_previous_entry are safe.
- The loop terminates as long as the linked list is well-formed (head's p_previous_entry is null). The top guard ensures the empty-list case is handled before any dereference.

Validation — appropriate for the function's role:
- The empty-list case is handled via the null-tail guard. Null p_collision_node / p_hitbox_aabb_manager are intentionally not validated here; that validation is the caller's responsibility (the callee's debug guard is a defensive nicety, not a contract).

Note (cross-cutting, in a callee — not a defect of this function):
The containment check is delegated to is_vector_3i32F4_inside__hitbox_aabb (core/source/collisions/core/aabb/hitbox_aabb.c, lines 541-563). That callee contains a bug on line 561: the z-axis upper-bound test reads `vector.z__i32F4 <= aa.z__i32F4` where it should read `vector.z__i32F4 <= bb.z__i32F4`. This makes the z containment test compare against the lower bound instead of the upper bound, so the function under review may reject hitboxes that actually contain the vector (or accept incorrect ones) in the z dimension. The function under review itself is structurally correct and forwards the call faithfully; this is a defect in the callee, not in get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node.

Side Effects:
No side effects — the function is effectively pure with respect to the collision node and hitbox manager. It performs only reads (following p_previous_entry links, dehashing into the hitbox pool) and returns a pointer. No state is mutated and no observable effect occurs at any callee site (out of scope per review policy).
