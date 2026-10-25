m_process__game_action__global_space__resolve — core/source/game_action/core/global_space/game_action__global_space__resolve.c

Resolves a global space by allocating its chunk and collision node, then either dispatching a deserialization sub-process (if a chunk file exists on disk) or transforming this process into a chunk generator (if no file exists). If the global space already has a chunk (indicating prior deserialization), the process is completed.

## Pre-conditions
1. `p_this_process` must be a non-null pointer to a valid `Process` struct.
2. `p_game` must be a non-null pointer to a valid `Game` struct with an initialized world, process manager, global space manager, chunk pool, and collision node pool.
3. `p_this_process->p_process_data` must be a non-null pointer to a `Game_Action` struct that was initialized via `initialize_game_action_for__global_space__resolve`, so that the payload union contains a valid `GA_Global_Space__Resolve` with a valid `gsv__3i32`.
4. The global space manager must contain an entry for the vector specified in the game action's payload (i.e., `get_p_global_space_from__global_space_manager` must return non-null for that vector).
5. If the global space does not yet have a chunk, the chunk pool and collision node pool must have available elements (otherwise allocation fails and the process is failed).

## Post-conditions
1. If the global space already has a chunk (post-deserialization re-entry): `complete_process(p_this_process)` is called; the process status is set to `Process_Status_Kind__Complete`. No resources are allocated or modified.
2. If the global space is not found: `fail_process(p_this_process)` is called; the process status is set to `Process_Status_Kind__Fail`. No resources are allocated.
3. If chunk allocation fails: `fail_process(p_this_process)` is called; `drop_global_space_within__global_space_manager` is invoked to release the global space entry. The chunk pool is unchanged (allocation failed).
4. If collision node allocation fails: the previously allocated chunk is released back to the chunk pool via `release_chunk_from__chunk_pool`; `fail_process(p_this_process)` is called; `drop_global_space_within__global_space_manager` is invoked. No resources remain allocated.
5. If a chunk file exists on disk and deserialization dispatch succeeds: a deserialization sub-process is dispatched and enqueued behind this process via `enqueue_process`. The current process remains active (not completed/failed) and will re-run; on its next invocation, the global space will have a chunk (set during deserialization), causing the process to complete.
6. If a chunk file exists on disk but deserialization dispatch fails: `fail_process(p_this_process)` is called. **However, the already-allocated chunk and collision node remain assigned to the global space and are not released** — this is a resource leak (see Implementation Correctness).
7. If no chunk file exists and no chunk generator is available: `memset` zeroes the chunk's `chunk_data`; `complete_process(p_this_process)` is called. The global space has a valid chunk and collision node, but the chunk data is empty.
8. If no chunk file exists and a chunk generator is available: the process is transformed in-place — its dispose handler is invoked (clearing `p_generation_process`, marking the global space as not constructing and dirty), `p_generation_process` is set to this process, the `PROCESS_FLAG__IS_CRITICAL` flag is cleared, `p_process_data` is repointed from the `Game_Action` to the `Global_Space`, the run handler is replaced with the chunk generator, and the dispose handler is replaced with `m_process__dispose_handler__game_action__global_space__resolve`. The process continues running as a chunk generator.

## Correctness Verdict
Correct

## Semantic Alignment
The function correctly fulfills its semantic intent of resolving a global space. The two primary code paths — deserialization from disk and generation from scratch — are both handled appropriately. The re-entry check (checking if the global space already has a chunk) enables the process to be run multiple times until it completes, which is the expected behavior for a process that dispatches sub-processes.

The in-place process transformation for chunk generation is semantically sound: the dispose handler clears the generation process pointer and marks the global space as dirty (so it will be saved later), while repointing the process data to the global space allows the chunk generator to operate on it directly.

The `memset` call when no generator is available correctly zeroes the chunk data, leaving a valid but empty chunk in place.

## Implementation Correctness
**Type compatibility:** All parameter types match their target field/function types exactly. The cast of `p_this_process->p_process_data` to `Game_Action*` is appropriate since the process was initialized with this data type. The `GET_UUID_P__u64(p_global_space)` macro correctly extracts the UUID from the `Serialization_Header__UUID_64` struct. The `stat_chunk_file__tiles` return value (`Index__u32`, i.e., `uint32_t`) is used as a boolean — non-zero (truthy) means the file exists, which matches the implementation of `stat_chunk_file` (returns `end_of_path + 2` on success, `0`/`false` on failure).

**Undefined behavior:** No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. All pointers are checked for null before use (`p_global_space`, `p_chunk`, `p_collision_node`, `p_process`). The `memset` call uses `&get_p_chunk_from__global_space(p_global_space)->chunk_data` which correctly resolves to `&p_chunk->chunk_data` (since `p_chunk` was just assigned), and `sizeof(Chunk_Data)` matches the union member size.

**Validation:** Validation is appropriate for the function's role. Null checks are performed on the global space, chunk, collision node, and dispatched process. The caller (process manager) is responsible for ensuring `p_this_process` and `p_game` are valid.

**Resource leak in deserialization failure path:** When `dispatch_process__deserialize_global_space` returns null, the function calls `fail_process` and returns without releasing the chunk or collision node that were already allocated and assigned to the global space. This is inconsistent with the other failure paths (chunk allocation failure and collision node allocation failure), which properly release resources and drop the global space. The leaked resources remain assigned to the global space, potentially causing pool exhaustion over time. This is a minor resource management issue in an edge-case failure path, not a correctness or undefined behavior issue.

## Side Effects
1. **Mutates `p_global_space`**: Sets `p_chunk` and `p_collision_node` to newly allocated resources from their respective pools. May also set `p_generation_process` to point to the current process (in the generation path).
2. **Mutates `p_this_process`**: May set process status to Complete or Fail, or transform the process in-place by changing its run handler, dispose handler, process data pointer, and flags (in the generation path).
3. **Allocates from pools**: Allocates a `Chunk` from the chunk pool and a `Collision_Node` from the collision node pool (unless the global space already has a chunk).
4. **Drops global space**: May call `drop_global_space_within__global_space_manager` to release the global space entry (on chunk or collision node allocation failure).
5. **Releases chunk**: May call `release_chunk_from__chunk_pool` to return an allocated chunk to the pool (on collision node allocation failure).
6. **Dispatches and enqueues sub-process**: May call `dispatch_process__deserialize_global_space` and `enqueue_process` to create and queue a deserialization sub-process.
7. **Zeroes chunk data**: May call `memset` to zero the chunk's `chunk_data` (when no generator is available).
8. **Debug logging**: Emits verbose debug messages and error messages via `debug_info__verbose` and `debug_error`.