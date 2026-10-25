release_client_pool_from__game — core/source/game.c

Frees the client pool allocated for the game, after verifying no clients are still active.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. If p_game->pM_clients is null, the function returns true immediately (idempotent no-op).
3. If p_game->pM_clients is non-null, p_game->pM_ptr_array_of__clients must also be non-null and valid (both are allocated together in allocate_client_pool_for__game).
4. No clients in the pool should be active (CLIENT_FLAG__IS_ACTIVE). The caller is responsible for disconnecting all clients before calling this function.
5. p_game->max_quantity_of__clients must be set to the pool capacity (set during allocate_client_pool_for__game).

Post-conditions:
1. If any client is active, the function returns false and the pool is NOT freed.
2. If no clients are active, p_game->pM_clients is freed via free(). The function returns true.
3. NOTE: p_game->pM_ptr_array_of__clients is NOT freed (memory leak — see Implementation Correctness).
4. NOTE: p_game->pM_clients, p_game->pM_ptr_array_of__clients, p_game->max_quantity_of__clients, and p_game->index_to__next_client_in__pool are NOT reset to 0 after freeing (dangling pointers — see Implementation Correctness).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to safely release the client pool: verify no clients are active, then free the allocated memory. The active-client check correctly iterates over all client slots and returns false if any client has CLIENT_FLAG__IS_ACTIVE set. However, the function fails to fully achieve its semantic intent because:
- It only frees pM_clients but not pM_ptr_array_of__clients (both are allocated in allocate_client_pool_for__game).
- It does not reset any state after freeing, leaving dangling pointers that would cause use-after-free on subsequent calls or access.

Implementation Correctness:
1. MEMORY LEAK: p_game->pM_ptr_array_of__clients is allocated in allocate_client_pool_for__game via malloc() but is never freed here. Only p_game->pM_clients is freed. This leaks the entire pointer array.

2. DANGLING POINTERS / USE-AFTER-FREE: After free(p_game->pM_clients), the function does not reset:
   - p_game->pM_clients (dangling non-null pointer)
   - p_game->pM_ptr_array_of__clients (dangling non-null pointer, also leaked)
   - p_game->max_quantity_of__clients (still holds old value)
   - p_game->index_to__next_client_in__pool (still holds old value)
   
   A subsequent call to release_client_pool_from__game would fail the early-return guard (if (!p_game->pM_clients) would be false since the pointer is non-null but points to freed memory), and would then call get_p_client_by__index_from__game which dereferences p_game->pM_ptr_array_of__clients (also freed). This is undefined behavior.
   
   Similarly, any other code accessing the client pool after release (e.g., get_p_client_by__uuid_from__game, get_p_local_client_by__from__game, etc.) would access freed memory.

3. INEFFICIENT LOOP BOUNDS: The loop iterates from 0 to get_max_quantity_of__clients_for__game(p_game) (i.e., max_quantity_of__clients), which is the total pool capacity. It should iterate only up to p_game->index_to__next_client_in__pool, which tracks the number of actually allocated clients. Iterating over unallocated slots:
   - In debug builds, get_p_client_by__index_from__game prints spurious "index out of bounds" error messages for each unallocated slot (it checks index_of__client >= p_game->index_to__next_client_in__pool).
   - In release builds, it accesses null pointers in pM_ptr_array_of__clients, which is functionally harmless (is_client__active(0) returns false) but wasteful.

4. No type compatibility issues — all parameter and field types match.
5. No null dereference on p_game itself — the function dereferences p_game immediately without a null check, but this is consistent with the codebase convention (see allocate_client_pool_for__game and other functions which also assume non-null p_game).

Side Effects:
1. Mutates: frees p_game->pM_clients (heap deallocation).
2. Does NOT free p_game->pM_ptr_array_of__clients (memory leak).
3. Does NOT reset p_game->pM_clients, p_game->pM_ptr_array_of__clients, p_game->max_quantity_of__clients, or p_game->index_to__next_client_in__pool to zero after freeing (leaves dangling pointers).
4. Reads: iterates over all client slots via get_p_client_by__index_from__game and checks is_client__active for each.
5. Debug logging: emits debug_error messages if active clients are found.
