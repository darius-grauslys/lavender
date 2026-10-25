allocate_chunk_from__chunk_pool — core/source/world/chunk_pool.c

Allocates a chunk from the chunk pool by finding an available slot (either deallocated or matching the requested UUID), validating availability, and initializing the chunk with the given UUID.

Pre-conditions:
1. p_chunk_pool must be a non-null pointer to a valid, initialized Chunk_Pool (initialized via initialize_chunk_pool).
2. uuid__u64 must not be IDENTIFIER__UNKNOWN__u64; passing the unknown identifier would cause the initialized chunk to appear deallocated.
3. The chunk pool must have at least one deallocated slot or a slot matching uuid__u64 for allocation to succeed.

Post-conditions:
1. On success: returns a non-null pointer to a Chunk whose _serialization_header.uuid is set to uuid__u64, whose chunk_flags is set to CHUNK_FLAGS__NONE (0), and whose tiles/chunk_data are zeroed (via memset in initialize_chunk).
2. On failure (pool full or UUID already in use): returns 0 (null). The pool state is unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent: it finds an available slot in the chunk pool, validates that the slot is not already in use with the same UUID, and initializes the chunk with the requested UUID. The initialize_chunk function performs Lavender-style initialization (memset to zero, then set serialization header with UUID) — this is NOT RAII; no external resources are acquired. The memset zeroes the entire Chunk struct including chunk_flags (set to 0, which equals CHUNK_FLAGS__NONE), ensuring a clean initial state. The call to initialize_chunk is consistent with the allocation pattern seen in allocate_serialization_header_with__this_uuid__u64 in hashing.h, which uses ALLOCATE_P__u64 to set the UUID after finding an available slot.

Implementation Correctness:
Type compatibility — p_chunk_pool->chunks (type Chunk[]) is cast to Serialization_Header__UUID_64*, which is valid because Chunk's first member is _serialization_header of type Serialization_Header__UUID_64 (standard C struct layout pattern). The return of get_next_available__allocation_in__contiguous_array__u64 (Serialization_Header__UUID_64*) is cast to Chunk*, also valid due to the same layout. uuid__u64 is Identifier__u64 (uint64_t), matching the parameter type of the callee. QUANTITY_OF__GLOBAL_SPACE is used as Quantity__u32, matching the callee's parameter type.
No undefined behavior — no null dereference (p_chunk is checked before use), no type punning (casts rely on valid struct layout), no out-of-bounds access (bounds checking is handled internally by poll_for__uuid_collision__uuid_64 via the length parameter). The IS_DEALLOCATED_P__u64 check correctly validates that the returned slot is deallocated (not already holding the same UUID), preventing double-allocation of the same UUID.
Validation — null check on p_chunk is appropriate. The IS_DEALLOCATED_P__u64 check catches the case where the UUID is already in use. Null validation of p_chunk_pool is the caller's responsibility, consistent with the codebase pattern.

Side Effects:
Mutates one Chunk element within the Chunk_Pool's chunks array: zeroes the entire struct (including chunk_flags and tiles/chunk_data) and sets the _serialization_header.uuid to uuid__u64 and _serialization_header.size_of__struct to sizeof(Chunk). No other observable side effects.
