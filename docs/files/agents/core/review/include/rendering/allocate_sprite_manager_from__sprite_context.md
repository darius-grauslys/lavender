allocate_sprite_manager_from__sprite_context — core/source/rendering/sprite_context.c

Allocates a Sprite_Manager slot from the Sprite_Context's pre-allocated pool of Sprite_Managers, dynamically allocates the internal sprite pool and render-record arrays for that manager, and tags it with the given UUID. Returns a pointer to the allocated Sprite_Manager, or NULL on failure.

Pre-conditions:
1. p_sprite_context must be a non-null pointer to an initialized Sprite_Context. The inline is_sprite_managers_allocated_in__sprite_context dereferences it without a null guard, so a null p_sprite_context is undefined behavior (consistent with the codebase-wide pattern — caller responsibility).
2. p_sprite_context->pM_sprite_managers must be non-null — allocate_sprite_managers_from__sprite_context must have been called previously to allocate and zero-initialize the pool. If not, the function logs an error and returns NULL.
3. uuid_of__sprite_manager is expected to be a valid Identifier__u32 (not IDENTIFIER__UNKNOWN__u32). The function does NOT validate this (see Implementation Correctness).
4. max_quantity_of__sprites_in__sprite_manager specifies the desired sprite capacity for the new Sprite_Manager.

Post-conditions:
1. On success: a Sprite_Manager slot is selected from the pool, pM_pool_of__sprites and pM_sprite_render_records are dynamically allocated, and the serialization header is tagged with uuid_of__sprite_manager (size_of__struct = sizeof(Sprite_Manager)). Returns a non-null Sprite_Manager *.
2. On failure (pool not allocated, pool full, or member allocation failure): returns NULL and logs an error/warning.

Correctness Verdict: Incorrect

Semantic Alignment:
For a valid UUID, the implementation correctly follows the allocation flow: validate pool -> find available slot -> allocate members -> tag with UUID. The ALLOCATE_P macro correctly preserves size_of__struct (read from the header, which was set to sizeof(Sprite_Manager) by initialize_sprite_manager within allocate_sprite_manager__members). However, the function does not validate that uuid_of__sprite_manager is not IDENTIFIER__UNKNOWN__u32. If an invalid UUID is passed, get_next_available__allocation_in__contiguous_array finds a deallocated slot (whose uuid is IDENTIFIER__UNKNOWN__u32), allocate_sprite_manager__members resets and allocates it, and ALLOCATE_P sets the header uuid back to IDENTIFIER__UNKNOWN__u32. The result is a non-null pointer to a Sprite_Manager that appears deallocated (is_serialized_struct__deallocated returns true), making it unfindable by UUID lookup. This violates the post-condition that the returned struct should be a properly allocated Sprite_Manager with the given UUID. The sibling allocate_sprite_from__sprite_manager (sprite_manager.c:85) validates the UUID with is_identifier_u32__invalid, establishing a precedent that this function should follow.

Note on initialization: the function calls initialize_sprite_manager (via allocate_sprite_manager__members), which is Lavender-style initialization — clearing the struct to its deallocated/empty state (memset + set header to IDENTIFIER__UNKNOWN__u32) — followed by resource acquisition (malloc). This is NOT RAII; initialization and resource acquisition are separate steps, consistent with the Lavender pattern.

Implementation Correctness:
- Type compatibility: parameter types match target fields exactly (Identifier__u32 -> Identifier__u32, Quantity__u32 -> Quantity__u32). The implicit widening of max_quantity_of__sprite_managers (Quantity__u8 -> Quantity__u32) in the call to get_next_available__allocation_in__contiguous_array is safe (no truncation). The (Serialization_Header*) cast in the ALLOCATE_P macro is valid since _serialization_header is the first member of Sprite_Manager (standard C struct casting rule).
- Undefined behavior: no null dereference of p_sprite_manager (checked with `if (!p_sprite_manager)`). No out-of-bounds access (hashing functions handle bounds internally). ALLOCATE_P reads size_of__struct from the header, which was correctly set to sizeof(Sprite_Manager) by initialize_sprite_manager. p_sprite_context is dereferenced without a null check in is_sprite_managers_allocated_in__sprite_context (consistent with the codebase pattern but technically UB if p_sprite_context is NULL — caller responsibility).
- Validation: uuid_of__sprite_manager is not checked with is_identifier_u32__invalid. This is the primary correctness defect — passing IDENTIFIER__UNKNOWN__u32 produces a silently incorrect result (non-null return of a seemingly-deallocated struct). A secondary concern: if get_next_available__allocation_in__contiguous_array returns an already-allocated slot with a matching UUID (not deallocated), allocate_sprite_manager__members calls initialize_sprite_manager (memset to 0) without freeing the old pM_pool_of__sprites and pM_sprite_render_records, leaking those allocations.

Side Effects:
1. Mutates p_sprite_context->pM_sprite_managers[n]._serialization_header to tag the allocated slot with the UUID (via ALLOCATE_P).
2. Mutates p_sprite_context->pM_sprite_managers[n] to allocate internal sprite pool data (pM_pool_of__sprites, pM_sprite_render_records, p_sprite_render_record__last, max_quantity_of__sprites) via allocate_sprite_manager__members.
3. Dynamically allocates memory (malloc) for the sprite pool and render record arrays; the caller is responsible for releasing the struct via release_sprite_manager_from__sprite_context (resets header) and ultimately the pool via release_sprite_managers_from__sprite_context (frees the array).
4. May log error/warning messages via debug_error/debug_warning on failure paths.
