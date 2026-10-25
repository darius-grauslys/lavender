get_quantity_of__processes_in__process_table — core/source/process/process_table.c

Sums the count of processes across all priority levels in the Process_Table.

Pre-conditions:
1. p_process_table must be a non-null pointer to a valid, initialized Process_Table object.
2. The Process_Table must have been initialized (typically via initialize_process_table, which memsets the struct to zero). All Process_Priority_Table_Entry elements within process_priority_table should have their pointer fields in a consistent state (both null for empty entries, or oldest >= youngest for populated entries).

Post-conditions:
1. Returns a Quantity__u32 (uint32_t) representing the total number of processes across all priority levels (0 through PROCESS_MAX_PRIORITY_LEVEL - 1).
2. The Process_Table is not mutated; this is a read-only query.
3. Returns 0 if the table has been zero-initialized (all entries empty).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent of counting all processes stored in the process table. It iterates over each priority level from 0 to PROCESS_MAX_PRIORITY_LEVEL - 1, retrieves the corresponding Process_Priority_Table_Entry via the static helper get_p_process_priority_table_entry_by__priority, and accumulates the per-entry process count obtained from get_quantity_of__processes_in__process_priority_table_entry.

The loop bound (index_of__priority_table < PROCESS_MAX_PRIORITY_LEVEL) correctly covers all valid priority levels. The Process_Table struct declares process_priority_table as an array of size PROCESS_MAX_PRIORITY_LEVEL + 1, where the extra slot (index PROCESS_MAX_PRIORITY_LEVEL) serves as a sentinel/end marker for pointer arithmetic in polling functions (e.g., poll_next_p_process_from__process_table). The loop correctly excludes this sentinel entry from the count.

The helper get_quantity_of__processes_in__process_priority_table_entry computes (oldest - youngest) pointer arithmetic, which yields the correct count of processes in a populated entry (oldest is at a higher address than youngest after processes are added). For an empty entry (both pointers null/zero), this yields 0, which is also correct.

Implementation Correctness:
Type compatibility — The loop variable index_of__priority_table is Index__u32 (uint32_t), compared against PROCESS_MAX_PRIORITY_LEVEL (defined as 4, an int). The implicit conversion is safe since the value is a small positive constant. The loop variable is passed to get_p_process_priority_table_entry_by__priority, which expects uint8_t process_priority; the narrowing from uint32_t to uint8_t is safe because the loop only produces values 0 through PROCESS_MAX_PRIORITY_LEVEL - 1 (0 through 3). The return type Quantity__u32 matches the accumulator type. The per-entry quantity function returns Quantity__u32, and the subtraction of two Process** pointers (ptrdiff_t) is implicitly converted to uint32_t — this is well-defined as long as oldest >= youngest, which is the maintained invariant.

Undefined behavior — No out-of-bounds array access. The loop accesses indices 0 through PROCESS_MAX_PRIORITY_LEVEL - 1, all within the bounds of the process_priority_table array (which has PROCESS_MAX_PRIORITY_LEVEL + 1 elements). The get_p_process_priority_table_entry_by__priority helper always returns a valid, non-null pointer for in-range priorities. No null dereference occurs within this function for a properly initialized Process_Table. No type punning or broken pointer arithmetic.

Validation — No null check is performed on p_process_table, consistent with the codebase style for internal query functions (e.g., get_p_process_priority_table_entry_by__priority, get_p_process_by__uuid). The caller is responsible for ensuring a valid pointer. This is appropriate for a low-level accessor.

Side Effects:
No side effects. The function is purely read-only: it reads from the Process_Table and its priority table entries without modifying any state. No memory is allocated or freed, no I/O occurs, and no global state is touched.
