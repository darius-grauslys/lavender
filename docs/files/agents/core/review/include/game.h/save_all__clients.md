save_all__clients — core/source/game.c

Iterates over all clients in the game's client pool (up to index_to__next_client_in__pool) and dispatches a save operation (save_client) for each.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game struct.
2. The client pool must have been allocated (p_game->pM_ptr_array_of__clients != 0); otherwise get_p_client_by__index_from__game will abort in debug builds or return garbage in release builds.
3. p_game->index_to__next_client_in__pool must accurately reflect the number of active client pointers in pM_ptr_array_of__clients.

Post-conditions:
1. save_client is invoked for each client pointer in the range [0, index_to__next_client_in__pool).
2. The return value (Process*) of save_client is discarded; save errors are silently ignored.
3. No mutation is performed on the Game struct itself by this function.

Correctness Verdict: Incorrect

Semantic Alignment:
The semantic intent is to save all active clients. The implementation iterates the pointer array and calls save_client for each entry. However, the function does not validate that each p_client obtained from get_p_client_by__index_from__game is non-null or non-deallocated before passing it to save_client. Other functions in the same file follow a defensive pattern:
- get_p_local_space_manager_thats__closest_to__this_position checks `if (!p_client) break;`
- get_p_client_by__uuid_from__game checks `if (IS_DEALLOCATED_P(p_client)) return 0;`
- dispatch_handler_process_to__load_client and dispatch_handler_process_to__create_client both check `if (!p_client)` before using the pointer.

save_all__clients omits this validation, violating the codebase's own convention.

Implementation Correctness:
- Type compatibility: Parameter types match target function signatures exactly. No implicit conversions or truncation.
- Undefined behavior: The function passes p_client (which may be null) directly to save_client. save_client dereferences p_client unconditionally via GET_UUID_P(p_client), which expands to (((Serialization_Header*)p_client)->uuid). A null p_client causes a null pointer dereference — undefined behavior. The IS_DEALLOCATED_P macro (defined in serialization/serialization_header.h) checks both null and deallocated status (uuid == IDENTIFIER__UNKNOWN__u32), but is not used here.
- Validation: Inappropriate for this function's role. The caller obtains a pointer from a lookup function that can return null, then passes it to a callee that dereferences it without checking. The null/deallocated check should be performed in save_all__clients before invoking save_client, consistent with the pattern used by get_p_local_space_manager_thats__closest_to__this_position and get_p_client_by__uuid_from__game.

Side Effects:
The function's own observable side effects are limited to invoking save_client for each client in the pool. save_client (and its callees) initiate asynchronous filesystem serialization processes, mark clients with CLIENT_FLAG__IS_SAVING, and may log debug errors. These are callee side effects and are not traced here per review scope.
