allocate_hitbox_aabb_from__hitbox_aabb_manager — core/source/collisions/core/aabb/hitbox_aabb_manager.c

Allocates a Hitbox_AABB from the manager's contiguous pool by finding a free (deallocated) slot or rejecting if the requested UUID is already in use by an allocated slot. In Lavender semantics, "allocation" means claiming a pool slot by setting its serialization header UUID — this is NOT RAII; no memory is acquired or resources opened.

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null, properly initialized pointer (checked in debug mode only via NDEBUG guard).
2. p_hitbox_aabb_manager->pM_pool_of__hitboxes must be a valid contiguous array of Hitbox_AABB of length quantity_of__hitboxes.
3. p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records must be a valid array of Hitbox_AABB* of length quantity_of__hitboxes.
4. p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records must accurately reflect the number of currently-allocated slots (i.e., maintained consistently by allocate/release).
5. uuid__u32 must NOT be IDENTIFIER__UNKNOWN__u32 (0xFFFFFFFF). This is NOT validated by the function. Callers pass entity UUIDs (e.g. GET_UUID_P(p_entity)) which are always valid. If the sentinel were passed, poll_for__uuid_collision would match the first deallocated slot (which also carries the sentinel uuid), the is_serialized_struct__deallocated check would pass, and the slot would be "allocated" with the deallocated sentinel — rendering it invisible to future lookups.

Post-conditions:
1. On success (non-null return): the returned Hitbox_AABB's _serialization_header is set to uuid__u32 with size_of__struct = sizeof(Hitbox_AABB) (via initialize_serialization_header).
2. On success: p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records is incremented by 1.
3. On success: the returned pointer is stored in pM_ptr_array_of__hitbox_records at the pre-increment index.
4. On failure (null manager in debug, full pool, uuid already in use, or pool fully occupied with no matching/deallocated slot): returns null and no state is mutated except debug logging.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements Lavender-style "allocation" — claiming a pool slot by setting its uuid via initialize_serialization_header, not RAII resource acquisition. The allocation flow matches the semantic intent: poll_for__uuid_collision finds the first slot that is either deallocated or has a matching UUID; if the matching slot is already allocated, the function rejects ("uuid already in use"); otherwise it records the pointer, increments the counter, and stamps the header. No semantic drift. The initialize_serialization_header call here is Lavender-initialization (resetting the struct to an "allocated" state with the given uuid), not RAII.

Implementation Correctness:
- Type compatibility: All parameter types match their targets exactly. IDENTIFIER__u32 is passed to poll_for__uuid_collision (expects Identifier__u32). INDEX__UNKNOWN__u32 matches Index__u32. sizeof(Hitbox_AABB) is Quantity__u32 which matches initialize_serialization_header's size_of__struct parameter. No implicit conversions or truncation.
- Undefined behavior: No UB. The pool base pointer is cast to Serialization_Header* and passed to poll_for__uuid_collision; since _serialization_header is the first member of Hitbox_AABB (offset 0), this cast is valid. poll_for__uuid_collision only returns indices in [0, quantity_of__hitboxes) or INDEX__UNKNOWN__u32 (the latter is checked and rejected). The returned index is used to index pM_pool_of__hitboxes, which is within bounds. No null dereference (p_hitbox_aabb is always valid when index is valid), no type punning, no out-of-bounds access.
- Validation: Appropriate for the function's role. The debug null-check on p_hitbox_aabb_manager is appropriate (debug-only per existing convention). The capacity check (index_of__next_hitbox_aabb_in__records >= quantity_of__hitboxes) prevents overflow of the records array. The INDEX__UNKNOWN__u32 check on poll_for__uuid_collision's return prevents indexing with an invalid sentinel. The is_serialized_struct__deallocated check after poll is defense-in-depth: it rejects the case where poll returned a slot whose UUID matches but is already allocated. The one validation gap is uuid__u32 != IDENTIFIER__UNKNOWN__u32 (documented in pre-conditions); this is a caller responsibility — all current callers pass valid entity UUIDs.

Side Effects:
1. Mutates p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records (incremented by 1).
2. Mutates p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[old index] (stores the new Hitbox_AABB pointer).
3. Mutates the allocated Hitbox_AABB in the pool: calls initialize_serialization_header on &p_hitbox_aabb->_serialization_header, setting uuid to uuid__u32 and size_of__struct to sizeof(Hitbox_AABB).
4. On failure paths only: calls debug_error(...) (logging side effect only).
