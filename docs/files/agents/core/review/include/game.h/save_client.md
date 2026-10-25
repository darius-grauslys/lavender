save_client — core/source/game.c, lines 529-565

Dispatches a filesystem process to serialize (write) a client's data to its client file, constructing the file path via stat_client_file and marking the client as saving.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object with an initialized PLATFORM_File_System_Context, World, and Process_Manager.
2. p_client must be a non-null pointer to a valid Client object whose first member is Serialization_Header (required for GET_UUID_P to correctly access the uuid field).
3. p_game->p_PLATFORM_file_system_context must be non-null (passed to stat_client_file).
4. p_game->pM_world must be non-null (passed to stat_client_file).
5. p_game->m_process__serialize_client must be set (non-null) for dispatch_handler_process_to__save_client to succeed.
6. The client file referenced by GET_UUID_P(p_client) must exist on the filesystem (stat_client_file checks this via PLATFORM_access).

Post-conditions:
1. On success: Returns a non-null Process pointer representing the serialization process. The client's CLIENT_FLAG__IS_SAVING flag is set via set_client_as__saving. The file path is constructed in a local IO_path buffer and passed to the serialization process.
2. On failure (path construction fails or process creation fails): Returns null (0). The client's state is unchanged (CLIENT_FLAG__IS_SAVING is not set).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to save a client by constructing its file path, verifying the file exists, and dispatching a serialization process. The path construction, UUID extraction, and process dispatch are all semantically correct. However, the error-checking logic is flawed — the return value of stat_client_file is stored but never checked, and the check that is performed (on index_of__path_to__base_directory) does not cover all failure cases. See Implementation Correctness for details.

Implementation Correctness:
- Type compatibility: All parameter types match their targets. IO_path is `typedef char IO_path[MAX_LENGTH_OF__IO_PATH]`; as a local variable, sizeof(path_to__client) correctly yields the full array size for memset. GET_UUID_P(p_client) casts Client* to Serialization_Header*, which is valid because Client's first member is Serialization_Header _serialization_header. The uuid field (Identifier__u32) matches stat_client_file's expected parameter type. No implicit conversions or truncation. ✓
- Undefined behavior: No pointer arithmetic, no null dereference (assuming valid pointers from caller, consistent with codebase conventions), no type punning (GET_UUID_P cast is valid due to first-member layout), no out-of-bounds access. ✓
- Validation: Validation is appropriate for the function's role. Null checks on p_game/p_client are omitted, consistent with the codebase's convention (e.g., dispatch_handler_process_to__save_client also dereferences p_game without null-checking). ✓
- BUG: The return value of stat_client_file is stored in index_of__path but is never checked. The error check uses index_of__path_to__base_directory instead. However, stat_client_file sets *p_OUT_index_of__path_to__file_base_directory to a non-zero value (line 523-524 of world_directory.c) BEFORE checking whether the client file actually exists via PLATFORM_access (line 532). If the client file does not exist, stat_client_file returns 0 (indicating failure), but index_of__path_to__base_directory is already non-zero. This means the check `if (!index_of__path_to__base_directory)` does NOT detect the case where the client file doesn't exist. The function proceeds to dispatch_handler_process_to__save_client with a path to a non-existent file, which would create the file via "wb" mode. The correct check should be on index_of__path (the return value), which is 0 in all failure cases including file non-existence. The unused variable index_of__path is a strong indicator of an oversight — the developer likely intended to check the return value but accidentally checked the wrong variable.
- Minor issue: The variable index_of__path is assigned but never used, which may generate compiler warnings in strict compilation modes.

Side Effects:
- Mutates p_client by setting the CLIENT_FLAG__IS_SAVING flag (via set_client_as__saving).
- Spawns a new Process via dispatch_handler_process_to__save_client, which allocates a Process and initializes it as a filesystem process to write the client file.
- The spawned Process performs file I/O (opening the client file in "wb" mode and serializing client data), but this occurs asynchronously in the process and is outside the scope of save_client's direct observable effects.
