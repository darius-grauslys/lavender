dispatch_handler_process_to__save_client — core/source/game.c, lines 454-482

Spawns and configures a critical-priority filesystem process that serializes (saves) a Client to the file at the given path, returning the created Process or null on failure.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_game->m_process__serialize_client must be a non-null function pointer (m_Process = void(*)(Process*, Game*)); this is the registered handler for serializing clients. If null, the function returns 0 before any allocation.
3. The Game's Process_Manager (obtained via get_p_process_manager_from__game) must be valid and have free capacity in its fixed-size pool (PROCESS_MAX_QUANTITY_OF == 512), since run_process allocates from it.
4. path_to__client_file must be a valid null-terminated C string (IO_path is char[MAX_LENGTH_OF__IO_PATH]). It need not reference a pre-existing file because the file is opened in "wb" mode with is_accepting__non_existing_file == true.
5. p_client must be a non-null pointer to a valid Client object to be serialized.

Post-conditions:
1. On success: returns a non-null Process * allocated from the process manager's pool and initialized as a filesystem process opened in "wb" (write/binary/truncate/create) mode at path_to__client_file, bound to p_client as the serialization request data, with is_accepting__non_existing_file set to true.
2. On the missing-handler path: returns null; no process is allocated and no file is touched.
3. On the file-open failure path: returns null; a process WAS allocated via run_process but is NOT released back to the pool (it remains allocated/marked-failed), unlike the sibling dispatch_handler_process_to__load_client, which calls release_process_from__process_manager. This is a resource leak.

Correctness Verdict: Correct

Semantic Alignment:
The implementation mirrors the sibling dispatch_handler_process_to__load_client (game.c:409-452): it guards on the handler pointer, runs the process at PROCESS_PRIORITY__0_MAXIMUM with PROCESS_FLAG__IS_CRITICAL, then initializes it as a filesystem process with the client passed as the serialization request data. The file mode is "wb" (write-only binary, truncating/creating) versus the load variant's "w+b", which is semantically correct for a save operation. The semantic intent — spawn a critical save process bound to the client and its target file path — is fulfilled on the success path. The deviation is on the failure path: the save variant does not release the allocated process (the load variant does, via release_process_from__process_manager), leaving a leaked process in the pool without altering the success-path semantics.

Implementation Correctness:
Type compatibility — all argument types match their targets exactly.
- p_game->m_process__serialize_client (m_Process = void(*)(Process*, Game*)) matches run_process's m_Process parameter.
- PROCESS_PRIORITY__0_MAXIMUM (0) matches run_process's uint32_t priority_level.
- PROCESS_FLAG__IS_CRITICAL (uint8_t / Process_Flags__u8) matches run_process's Process_Flags__u8 process_flags__u8.
- path_to__client_file (IO_path = char[N], decays to char*) matches initialize_process_as__filesystem_process__open_file's IO_path path_to__file.
- "wb" (const char[3], decays to const char*) matches const char *p_file_descriptors.
- p_client (Client*) is implicitly converted to void *p_serialization_request__data — safe and intended.
- true (bool) matches bool is_accepting__non_existing_file.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access on the success path. NOTE: run_process may return null on failure and that return value is not null-checked here before being passed to initialize_process_as__filesystem_process__open_file; if p_process were null the callee could dereference it. This matches the sibling load function's pattern, so it is an established (if latent) convention rather than a unique defect.
Validation — the function validates its own precondition (m_process__serialize_client non-null). It does not null-check p_game, path_to__client_file, or p_client, consistent with the codebase convention that low-level dispatch functions rely on the caller (save_client) to supply valid arguments.

Side Effects:
- Allocates a Process from the Game's Process_Manager pool via run_process (mutates the process manager's internal allocation state).
- On success, the process is initialized as a filesystem process that opens (creates/truncates) the file at path_to__client_file in "wb" mode and binds p_client as its serialization request data.
- On the file-open failure path, the allocated process is not released — it leaks in the process manager's pool (marked failed), unlike the sibling load function which releases it via release_process_from__process_manager.
- Emits debug_error(...) log messages on the missing-handler and file-open failure paths.
