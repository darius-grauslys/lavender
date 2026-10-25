initialize_process_as__filesystem_process — core/source/process/filesystem_process.c, lines 87-98

### Semantic
Routes a Serialization_Request and its data pointer into a Process struct's process data, and sets the filesystem default dispose handler. This is a Lavender-style initialization: it configures struct internals for an already-allocated Process, not RAII resource acquisition.

### Pre-conditions
1. p_process must be a non-null pointer to a writable, already-initialized (via initialize_process) Process object.
2. p_serialization_request must be a non-null pointer to a valid Serialization_Request that has been allocated and has an open file handler (typically obtained via PLATFORM_allocate_serialization_request and PLATFORM_open_file).
3. p_serialization_request__data may be NULL (type is void *); it is optional user data.

### Post-conditions
1. p_process->p_process_data is set to p_serialization_request (the Serialization_Request pointer).
2. p_serialization_request->p_data is set to p_serialization_request__data.
3. p_process->m_process_dispose__handler is set to m_process__dispose_handler__filesystem__default via set_process__dispose_handler.
4. The Process struct is now configured for filesystem serialization; on disposal, the default handler will close the file and release the serialization request.

### Correctness Verdict
Correct

### Semantic Alignment
The implementation fulfills the semantic intent. It assigns p_serialization_request to p_process->p_process_data and p_serialization_request__data to p_serialization_request->p_data, then sets the dispose handler. All three operations are straightforward pointer assignments consistent with the Lavender pattern of setting struct internals. No struct fields are omitted or reordered — only the relevant fields are set.

### Implementation Correctness
- Type compatibility: p_process is Process*, p_serialization_request is Serialization_Request*, and p_serialization_request__data is void*. All parameter types match their target field types exactly. p_process_data is void*, so assigning a Serialization_Request* to it is an implicit but safe conversion (Serialization_Request* → void*), which is idiomatic in this codebase.
- No undefined behavior: no pointer arithmetic, no null dereference (caller guarantees non-null p_process and p_serialization_request), no type punning, no out-of-bounds access.
- Validation: No validation is needed within this function. This is a low-level struct assignment function. Validation of p_process and p_serialization_request is the caller's responsibility (the caller initialize_process_as__filesystem_process__open_file performs null checks on p_process and validates the serialization request allocation).

### Side Effects
1. p_process->p_process_data is mutated (set to p_serialization_request).
2. p_serialization_request->p_data is mutated (set to p_serialization_request__data).
3. p_process->m_process_dispose__handler is mutated (set to m_process__dispose_handler__filesystem__default).
