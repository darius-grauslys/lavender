# m_process__game_action__global_space__store

**File of origin:** `core/source/game_action/core/global_space/game_action__global_space__store.c`

---

## Semantic

Dispatches a serialization process for a global space identified by the game action's stored chunk vector, handling null or unallocated global space cases by failing or completing the process accordingly.

---

## Pre-conditions

1. `p_this_process` must be non-null (it is dereferenced immediately without a null guard).
2. `p_game` must be non-null (passed to `get_p_global_space_manager_from__game`, `get_p_PLATFORM_file_system_context_from__game`, `get_p_world_from__game`).
3. `p_this_process->p_process_data` must point to a valid `Game_Action` that was initialized via `initialize_game_action_for__global_space__store` (so the payload contains a valid `gsv__3i32`).
4. The `Game_Action_Logic_Table` entry for `Game_Action_Kind__Global_Space__Store` must have been registered with `register_game_action__global_space__store` (this is a registration precondition, not checked at runtime).

---

## Post-conditions

1. If `p_global_space` is null (the chunk vector does not map to an allocated global space), the process is failed via `fail_process(p_this_process)` and the function returns.
2. If `p_global_space` exists but is not allocated (`is_global_space__allocated` returns false), the process is completed via `complete_process(p_this_process)` and the function returns.
3. If `p_global_space` exists and is allocated, a serialization process is dispatched via `dispatch_process__serialize_global_space`. 
   - If that dispatch fails (returns null), the process is failed via `fail_process(p_this_process)`.
   - If dispatch succeeds, the current process is completed via `complete_process(p_this_process)`.
4. In all cases, `p_this_process` is either completed or failed — it is never left in a pending state.

---

## Correctness Verdict

**Incorrect**

---

## Semantic Alignment

The implementation does not fully fulfill its semantic intent. Two issues are present:

1. **Redundant `stat_chunk_file__tiles` call (dead code):** On line 47, `stat_chunk_file__tiles` is called to populate a local `IO_path path` variable. However, this `path` variable is **never used** after the call. The subsequent `dispatch_process__serialize_global_space` (called on line 53) internally calls `stat_chunk_file__tiles` again (see `core/source/world/global_space.c` line 721) to compute its own path. The `stat_chunk_file__tiles` call on line 47 is therefore completely redundant — it performs unnecessary file system stat work and writes to a buffer that is discarded. The `// TODO: handle local file IO.` comment at the top suggests this was intended for future local file IO handling that was never implemented.

2. **Misleading error message:** On line 59, the error message reads "failed to dispatch deserialization process," but the function being dispatched is `dispatch_process__serialize_global_space`, which performs **serialization**, not deserialization. This is a copy-paste error from a deserialization counterpart and misrepresents the failure.

---

## Implementation Correctness

- **Type compatibility:** All parameter types match their expected target types. `p_this_process->p_process_data` is cast to `Game_Action*`, which is consistent with how game actions are stored as process data. The `IO_path` type (a `char[MAX_LENGTH_OF__IO_PATH]` array) is correctly passed to `stat_chunk_file__tiles` which expects `char *buffer`.

- **Undefined behavior:** No null pointer dereferences, out-of-bounds accesses, or type punning issues. The function checks `p_global_space` for null before use. The `path` buffer is stack-allocated and properly sized for the `stat_chunk_file__tiles` call.

- **Validation:** The function appropriately checks `p_global_space` for null and checks `is_global_space__allocated`. However, it does not validate `p_this_process` or `p_game` for null, which is consistent with the engine's convention (callers are expected to provide valid pointers). The `stat_chunk_file__tiles` return value (`Index__u32`) is ignored, but this is acceptable since the path it computes is not used.

---

## Side Effects

1. **Process state mutation:** The current process (`p_this_process`) is either completed or failed.
2. **Process dispatch:** A new serialization process for the global space is dispatched via `dispatch_process__serialize_global_space`, which opens a file for writing (`"wb"`), sets the global space as deconstructing, and registers the process with the game's process manager.
3. **Global space state mutation:** The dispatched serialization process sets the global space's deconstruction flags (`set_global_space_as__deconstructing` and `set_global_space_as__NOT_awaiting_deconstruction`).
4. **Debug logging:** Debug messages are emitted via `debug_error` and `debug_info__verbose`.
5. **File system access:** `stat_chunk_file__tiles` performs a file system stat operation (though the result is discarded).
