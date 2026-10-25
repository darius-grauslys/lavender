# release_chunk_from__chunk_pool

**File of origin:** `core/source/world/chunk_pool.c`

## Semantic
Resets a previously allocated `Chunk` back to its initial (deallocated) state so that it can be reused by the chunk pool. This is Lavender-style initialization (pool cleanup), not RAII resource teardown — the function clears the serialization header and flags but does not free any external resources.

## Pre-conditions
1. `p_chunk_pool` must be a valid, non-null pointer to an initialized `Chunk_Pool`.
2. `p_chunk` must point to a `Chunk` that resides within `p_chunk_pool->chunks[0..QUANTITY_OF__GLOBAL_SPACE-1]`. In debug builds this is validated; in release builds it is the caller's responsibility.
3. The chunk pointed to by `p_chunk` should have been previously allocated (i.e., obtained via `allocate_chunk_from__chunk_pool`) and be in an active/allocated state.

## Post-conditions
1. `p_chunk->_serialization_header.uuid` is set to `IDENTIFIER__UNKNOWN__u64`, marking the chunk as deallocated and available for reallocation.
2. `p_chunk->_serialization_header.size_of__struct` is set to `sizeof(Chunk)`.
3. `p_chunk->chunk_flags` is set to `CHUNK_FLAGS__NONE`, clearing all active/updated/serialization flags.
4. The chunk is now eligible to be returned by a future call to `allocate_chunk_from__chunk_pool`.

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation fulfills the semantic intent of releasing a chunk back to the pool. It performs Lavender-style initialization by:
- Setting the serialization header to the "deallocated" state via `initialize_serialization_header_for__deallocated_struct__uuid_64`, which internally calls `initialize_serialization_header__uuid_64` with `IDENTIFIER__UNKNOWN__u64` and `sizeof(Chunk)`.
- Clearing all chunk flags to `CHUNK_FLAGS__NONE`.

This matches the pattern used by `initialize_chunk` (which sets a real UUID and `sizeof(Chunk)` on allocation) and by `initialize_chunk_pool` (which marks all chunks as deallocated). The function does not perform RAII-style resource deallocation, which is consistent with Lavender's design philosophy.

## Implementation Correctness
- **Type compatibility:** All parameter types match their target fields. `p_chunk_pool` is `Chunk_Pool*`, `p_chunk` is `Chunk*`. The `sizeof(Chunk)` argument passed to the serialization header initializer is of type `Quantity__u32`, which matches the `size_of__struct` field type.
- **Pointer arithmetic:** The debug-only bounds check uses `p_chunk - p_chunk_pool->chunks` to compute the index. This is valid pointer arithmetic since `p_chunk` is expected to point into the `chunks` array. If `p_chunk` is not from this pool, the index will be out of bounds and the function returns early (debug builds only).
- **No undefined behavior:** No null dereferences (debug build checks are guarded by `NDEBUG`). No out-of-bounds access on the array. No type punning.
- **Validation:** The debug-only check is appropriate for this function's role. In release builds, the caller is responsible for ensuring `p_chunk` belongs to `p_chunk_pool`. This is consistent with the codebase's pattern of debug-only validation for performance-critical paths.

## Side Effects
- **Mutates** `p_chunk->_serialization_header` (sets `uuid` to `IDENTIFIER__UNKNOWN__u64`, sets `size_of__struct` to `sizeof(Chunk)`).
- **Mutates** `p_chunk->chunk_flags` (sets to `CHUNK_FLAGS__NONE`).
- In debug builds only, reads `p_chunk_pool->chunks` to perform a bounds check.
- No side effects on `p_chunk_pool` itself.
