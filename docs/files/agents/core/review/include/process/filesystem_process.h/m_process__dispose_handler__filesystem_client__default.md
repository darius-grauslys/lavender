# m_process__dispose_handler__filesystem_client__default

**File of origin:** `core/source/process/filesystem_process.c`

## Semantic

Disposes of a filesystem process's serialization request by resolving any associated game action, closing the file handle if open, and releasing the serialization request back to the platform. This is the "client" variant of the filesystem dispose handler, intended for processes where the serialization request's `p_data` holds a `Game_Action*` that must be resolved upon disposal.

## Pre-conditions

1. `p_this_process` must be non-null; it is dereferenced immediately to read `p_process_data`.
2. `p_game` must be non-null; it is passed to `resolve_game_action` and `get_p_PLATFORM_file_system_context_from__game`.
3. The process must have been previously initialized as a filesystem process (via `initialize_process_as__filesystem_process`), so that `p_this_process->p_process_data` points to a valid `Serialization_Request` (or is null, in which case the function returns early).
4. If `p_this_process->p_process_data` is non-null, it must point to a valid `Serialization_Request`.
5. If `p_serialization_request->p_data` is non-null, it must point to a valid `Game_Action`.

## Post-conditions

1. If `p_this_process->p_process_data` was null, the function returns immediately with no side effects.
2. If the serialization request's `p_data` (cast to `Game_Action*`) was non-null, `resolve_game_action` is called with the game action and its client UUID, resolving the game action through the game's resolve handler.
3. If the serialization request's `p_file_handler` was non-null, `PLATFORM_close_file` is called to close the file handle.
4. `PLATFORM_release_serialization_request` is always called (when the serialization request is non-null), releasing the request back to the platform's file system context.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of disposing a filesystem-client process. The function:
- Properly extracts the `Serialization_Request` from `p_process_data`.
- Guards against null serialization requests with an early return.
- Resolves the game action (if present) before releasing resources, which is the correct order — the game action may depend on data in the serialization request or file.
- Closes the file handle (if open) before releasing the serialization request, preventing resource leaks.
- Releases the serialization request unconditionally (when non-null).

The function is semantically identical to `m_process__dispose_handler__filesystem_game_action__default` in the same file (lines 31–49). While this represents code duplication, it does not introduce a correctness bug. The duplication may exist to allow future divergence between the "game_action" and "client" variants, or it may be an oversight. Either way, both functions are correct.

## Implementation Correctness

- **Type compatibility:** All casts are appropriate. `p_process_data` is `void*`, cast to `Serialization_Request*` — this matches the initialization in `initialize_process_as__filesystem_process` where `p_process->p_process_data = p_serialization_request`. The cast of `p_serialization_request->p_data` (also `void*`) to `Game_Action*` is consistent with the codebase's pattern of storing typed data in the serialization request's generic `p_data` field.
- **GA_UUID_SOURCE macro:** The macro expands to `((Game_Action*)game_action)->uuid_of__client__u32`. Since `p_game_action` is already a `Game_Action*`, the cast is redundant but harmless. The resulting `Identifier__u32` matches the expected parameter type of `resolve_game_action`.
- **Null dereference:** No null dereferences occur. The function checks `p_serialization_request`, `p_game_action`, and `p_file_handler` before using each pointer.
- **Undefined behavior:** None present. No broken pointer arithmetic, no out-of-bounds access, no type punning through unions in a way that would be UB (the `Serialization_Request` union is accessed through its named members, not through type-punning).
- **Validation:** The function performs appropriate null checks for its role as a dispose handler. It does not validate `p_this_process` or `p_game` for null, but this is consistent with all other dispose handlers in the codebase (e.g., `m_process__dispose_handler__filesystem__default`, `m_process__dispose_handler__game_action__default`). The convention is that callers provide valid pointers; validation is delegated to the caller or to debug-only assertions in setter functions like `set_process__dispose_handler`.

## Side Effects

1. **Resolves a game action** (if `p_serialization_request->p_data` is non-null) by calling `resolve_game_action`, which invokes the game's `m_game_action_handler__resolve` callback. This may mutate game state, dispatch responses, or free game action resources.
2. **Closes a file handle** (if `p_serialization_request->p_file_handler` is non-null) via `PLATFORM_close_file`.
3. **Releases the serialization request** via `PLATFORM_release_serialization_request`, returning it to the platform's pool for reuse.
