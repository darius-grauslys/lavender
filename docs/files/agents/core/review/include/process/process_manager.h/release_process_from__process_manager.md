release_process_from__process_manager — core/source/process/process_manager.c

Releases a process from the process manager, removing it from active tracking, invoking its dispose handler if present, and resetting it to an empty state.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid Game object.
2. `p_process_manager` must be a non-null pointer to a valid Process_Manager whose `processes` array contains `p_process`.
3. `p_process` must be a non-null pointer to a Process that was allocated from `p_process_manager->processes` (i.e., `p_process` points within the `p_process_manager->processes` array). In debug builds, an index bounds check validates this; in release builds this is the caller's responsibility.
4. The process may or may not have a dispose handler (`m_process_dispose__handler` may be NULL).
5. The process may or may not be currently registered in the process table.

Post-conditions:
1. The process is removed from the process manager's active process table via `remove_process_from__active_processes_in__process_manager`.
2. If the process had a non-null `m_process_dispose__handler`, that handler is invoked with `p_process` and `p_game` as arguments.
3. The process is reset to an empty/default state via `initialize_process_as__empty_process`, which sets: UUID to `IDENTIFIER__UNKNOWN__u32`, run handler to NULL, process data to NULL, priority to 1, process kind to `Process_Kind__None`, status to `Process_Status_Kind__None`, process flags to `PROCESS_FLAGS__NONE`, and zeroes all other fields via `memset`.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of releasing a process from the process manager. The three-step sequence (remove from active processes, invoke dispose handler if present, reset to empty state) correctly tears down the process lifecycle. The `initialize_process_as__empty_process` call performs Lavender-style initialization (pool cleanup / reset to default state), not RAII-style resource acquisition. This is consistent with the engine's pattern where initialization means cleaning up a struct to its initial conditions for pool reuse. The `memset` in `initialize_process` zeroes the entire struct before setting individual fields, ensuring no stale data remains.

Implementation Correctness:
- Type compatibility: All parameter types match exactly. `Game *`, `Process_Manager *`, and `Process *` are all correctly typed pointers. The function pointer `m_process_dispose__handler` is called with the correct signature `(Process *, Game *)`.
- Undefined behavior: No undefined behavior in the normal execution path. The debug-only index check (`p_process - p_process_manager->processes`) is valid pointer arithmetic within the same array. The `does_process_have__dispose_handler` check guards against null function pointer dereference. No out-of-bounds access occurs.
- Validation: The debug-only bounds check (`index >= PROCESS_MAX_QUANTITY_OF`) is appropriate for catching misuse during development. In release builds, validation is the caller's responsibility, which is consistent with the engine's performance-conscious design.

Side Effects:
1. Mutates the `Process_Manager`'s process table by removing the process from active tracking (via `remove_process_from__active_processes_in__process_manager`, which calls `remove_process_from__process_table` to remove the process pointer from the priority table's pointer array and shift remaining entries).
2. Invokes the process's dispose handler, which may have arbitrary side effects (e.g., freeing resources, modifying game state).
3. Mutates the `Process` object itself by resetting all its fields to default/empty values.
