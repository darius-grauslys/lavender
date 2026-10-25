load_world — core/source/world/world.c

Dispatches a game action to the server to asynchronously load the world for the local client, returning the created process handle.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game struct.
2. p_game->pM_ptr_array_of__clients must be allocated (non-null) so that a local client can be retrieved.
3. p_game->pM_ptr_array_of__clients[0] must be a valid, non-null Client (the local client).
4. p_game->m_game_action_handler__dispatch must be a valid function pointer (set by the backend) for dispatch_game_action_to__server to function.
5. The game action logic table must have an entry registered for Game_Action_Kind__World__Load_World, otherwise dispatch_game_action__world__load_world will fail.

Post-conditions:
1. On success: Returns a non-null Process* representing the game action process created for loading the world. The process manager's p_process__latest field is cleared (set to 0) after retrieval.
2. On failure (no local client): Returns NULL (0) and logs a debug error.
3. On failure (game action dispatch fails): Returns NULL (0) and logs a debug error.
4. On failure (no process was created by the dispatch): Returns NULL (0) and logs a debug error.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent of loading a world by dispatching a game action to the server. The dispatch mechanism (dispatch_game_action__world__load_world) internally calls dispatch_game_action_to__server, which routes through the backend's m_game_action_handler__dispatch. This handler creates a process via dispatch_game_action_process -> run_process_with__uuid, which sets p_process_manager->p_process__latest. The function then retrieves this latest process and returns it. The initial (void) call to get_p_latest_allocated_process_from__process_manager clears any stale "latest process" pointer before the dispatch, ensuring a clean state. The logic flow is correct and aligns with the engine's asynchronous process-based architecture.

Implementation Correctness:
Type compatibility — all types match exactly: p_game is Game*, p_client__local is Client*, p_process is Process*. No implicit conversions or truncation occur.
Undefined behavior — no null pointer dereference. p_client__local is checked before use, and p_process is checked before being returned. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — the function performs appropriate validation for its role: it checks for a valid local client before dispatching, checks the return value of the dispatch, and checks that a process was actually created. These are the correct validation boundaries for this function; deeper validation (e.g., world directory existence) is handled by the dispatched game action process itself.
The first (void) call to get_p_latest_allocated_process_from__process_manager is a defensive clearing of stale state, which is correct behavior.

Side Effects:
1. Clears p_process_manager->p_process__latest to 0 at the start (via the (void) call).
2. Dispatches a game action to the server, which creates a new Process in the process manager and sets p_process__latest.
3. Clears p_process_manager->p_process__latest to 0 again after retrieving the process.
4. The game action dispatch may trigger additional side effects through the backend's m_game_action_handler__dispatch implementation (e.g., network communication), but those are outside the scope of this function's own observable effects.
