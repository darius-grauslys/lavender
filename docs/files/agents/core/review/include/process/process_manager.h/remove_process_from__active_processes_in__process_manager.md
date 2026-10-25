# remove_process_from__active_processes_in__process_manager

## File of Origin
`core/source/process/process_manager.c`

## Semantic
Removes a process from the active process table managed by the `Process_Manager`. This is a thin wrapper that delegates to `remove_process_from__process_table`, which unlinks the process from its priority-level linked list and shifts down the pointer array entries of all higher-priority entries to close the gap.

## Pre-conditions
1. `p_process_manager` must point to a valid, initialized `Process_Manager` struct.
2. `p_process` must point to a valid `Process` that resides within `p_process_manager->processes[PROCESS_MAX_QUANTITY_OF]`.
3. `p_process` must currently be present in the process table (i.e., it was previously added via `add_process_to__active_processes_in__process_manager`).
4. The caller is responsible for ensuring `p_process` has not already been removed; the function does not guard against double-removal.

## Post-conditions
1. The process referenced by `p_process` is unlinked from its `Process_Priority_Table_Entry` in `p_process_manager->process_table`.
2. All `Process_Priority_Table_Entry` instances at higher priority levels (i.e., priority values greater than the removed process's priority) have their pointer-array entries shifted down by one to close the gap in `ptr_array_of__processes`.
3. The `Process` struct pointed to by `p_process` is **not** reinitialized or deallocated — its fields remain intact. The caller (e.g., `release_process_from__process_manager`) is responsible for calling `initialize_process_as__empty_process` if the process slot should be returned to the free pool.
4. The function returns `void` — no return value is provided.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation correctly fulfills its semantic intent. The function is a straightforward delegation to `remove_process_from__process_table`, which performs the actual linked-list unlinking and pointer-array compaction. The function name accurately reflects its behavior: it removes a process from the active processes (the process table) within the process manager. There is no semantic drift.

## Implementation Correctness
- **Type compatibility**: The `Process_Manager*` parameter is dereferenced to access `process_table`, which is of type `Process_Table` — types match exactly. The `Process*` parameter is passed directly to `remove_process_from__process_table`, which expects `Process*` — types match exactly. No implicit conversions or truncation occur.
- **Undefined behavior**: No pointer arithmetic, no null dereference (in release builds; debug builds rely on the caller to pass valid pointers), no out-of-bounds access. The function simply passes a pointer to the `process_table` member and the `p_process` pointer to the callee.
- **Validation**: No null-check is performed on `p_process_manager` or `p_process`. This is consistent with the codebase pattern — the immediate caller `release_process_from__process_manager` performs its own debug-mode bounds check on `p_process` (verifying it falls within the `processes` array), and other callers are expected to follow the same contract. The absence of validation is appropriate for a low-level internal helper.

## Side Effects
- **Mutates** `p_process_manager->process_table`:
  - Unlinks `p_process` from the linked list maintained by the `Process_Priority_Table_Entry` at the priority level of `p_process`.
  - Shifts down (compacts) the `ptr_array_of__processes` entries for all priority table entries at higher priority levels (priority values greater than the removed process's priority), adjusting their `p_ptr_process__oldest_of__priority`, `p_ptr_process__youngest_of__priority`, and `p_ptr_process__current_priority_to__swap` pointers accordingly.
- Does **not** modify `p_process` itself or any other field of `p_process_manager`.

## Lavender-Specific Semantics
This function is **not** an initialization function (despite residing in the process manager). Its name contains "remove", not "init", "initialize", or "reset". It does not perform Lavender-style initialization (pool cleanup) nor RAII-style resource acquisition. It is a removal/deregistration operation that only mutates the process table's internal linked-list and pointer-array structures. The actual reinitialization of the `Process` struct to its empty/default state is performed by a separate call to `initialize_process_as__empty_process`, typically invoked by the higher-level `release_process_from__process_manager`.
