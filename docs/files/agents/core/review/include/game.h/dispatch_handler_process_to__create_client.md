dispatch_handler_process_to__create_client — core/source/game.c

Dispatches (runs) the game's registered "create client" process handler for a client identified by UUID, attaching the resolved Client pointer as the new Process's data.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game object (its process_manager must be initialized). Null-checking p_game is the caller's responsibility.
2. uuid_of__client__u32 must identify a Client that already exists in the game's client pool (the client must have been previously allocated); get_p_client_by__uuid_from__game returns null otherwise.
3. p_game->m_process__create_client must be non-null (registered via set_dispatch_handler_process_for__create_client); otherwise the function bails early and returns 0.
4. The process manager must have available capacity for a new Process (PROCESS_MAX_QUANTITY_OF); run_process returns 0 when the pool is exhausted.
5. p_game->m_process__create_client is of type m_Process (void (*)(Process*, Game*)), matching run_process's expected handler signature.

Post-conditions:
1. On success: a new Process is allocated and enqueued in the game's process manager, scheduled at maximum priority (PROCESS_PRIORITY__0_MAXIMUM) with PROCESS_FLAG__IS_CRITICAL; the Process's p_process_data is set to point to the resolved Client; the Process * is returned to the caller.
2. On success: the caller becomes the owner of the returned Process*; the client pool client itself is not mutated.
3. On failure (handler not registered, client not found, or run_process returns 0): returns 0. If the failure occurred after client lookup, the client is marked failed-to-load via set_client_as__failed_to_load.
4. No mutation occurs to p_game's client pool, the Client's core fields, or the handler callback in any path.

Correctness Verdict: Correct

Semantic Alignment:
The function does exactly what its name implies — it dispatches the registered create-client process handler against an existing client. It validates the handler is registered, validates the target client exists, spawns a critical maximum-priority process, binds the client as process data, and returns the process. No struct-initialization drift is involved (this is a launcher/dispatch, not an initializer). The implementation fulfills the semantic intent. Note: per Lavender semantics this is a dispatch/launch, not an "initialize" function, so the initialization-vs-RAII distinction does not apply here; the create-client handler itself is responsible for whatever client creation work it performs.

Implementation Correctness:
- Type compatibility: every argument matches its target. m_process__create_client (m_Process) is passed as run_process's m_Process parameter; PROCESS_PRIORITY__0_MAXIMUM (macro 0) is passed to uint32_t priority_level (0 fits); PROCESS_FLAG__IS_CRITICAL (BIT(0) = 1) is passed to Process_Flags__u8 (1 fits, no truncation); p_process_data (void *) receives a Client * (any object pointer is assignable to void *); uuid_of__client__u32 (Identifier__u32) matches get_p_client_by__uuid_from__game's parameter; get_p_process_manager_from__game returns Process_Manager * matching run_process's first parameter. run_process's Process * return is assigned to Process * p_process.
- Undefined behavior: none. No pointer arithmetic, no type punning, no out-of-bounds access. p_process is only dereferenced after the `!p_process` null check. p_game is dereferenced but null-p_game is a caller-violated pre-condition (consistent with the engine convention that p_game null-checking is the caller's responsibility and is not performed in game.c dispatchers). get_p_client_by__uuid_from__game is only invoked on a valid p_game.
- Validation: appropriate for a dispatch handler. The function checks (a) the handler is registered, (b) the client was found, and (c) process allocation succeeded — the latter being meaningful because run_process (→ run_process_with__uuid → allocate_process_in__process_manager) returns null when the process pool is exhausted. Each failure path returns 0 and logs an error; only the allocation-failure path mutates the client (marks failed-to-load). The caller is responsible for validating p_game and the UUID's existence semantics.

Side Effects:
- Mutates the game's Process_Manager: allocates and enqueues a new entry in its process table via run_process (this is the primary observable effect).
- If run_process returns 0: mutates the resolved Client's client_flags__u16, clearing all flags and setting CLIENT_FLAG__IS_FAILED_TO_LOAD via set_client_as__failed_to_load.
- Writes the resolved Client * into the returned Process's p_process_data field.
- Emits log output: debug_warning (unregistered handler path, twice), debug_error (unregistered handler path, and each failure path).
- Does not mutate p_game's client pool, the Client's gameplay state, or any handler callback.
