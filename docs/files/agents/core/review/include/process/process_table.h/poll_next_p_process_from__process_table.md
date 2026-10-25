poll_next_p_process_from__process_table — core/source/process/process_table.c, lines 141-161

Iterates through process priority table entries starting from the current entry, polling the next process from the first non-empty entry found. Returns the polled process or NULL if all processes have been polled (wrap-around detected).

Pre-conditions:
1. p_process_table must be a non-null pointer to a valid, initialized Process_Table.
2. begin_polling_of__process_table must have been called (or initialize_process_table) to set p_process_priority_table_entry__current to a valid entry within process_priority_table[0..PROCESS_MAX_PRIORITY_LEVEL].
3. The process table may contain zero or more processes across its priority entries.

Post-conditions:
1. p_process_table->p_process_priority_table_entry__current is advanced to the next priority entry if the current entry is exhausted (all its processes polled).
2. If all entries have been polled (wrap-around at the sentinel entry at index PROCESS_MAX_PRIORITY_LEVEL), p_process_priority_table_entry__current is reset to process_priority_table[0] and the function returns NULL.
3. Returns a pointer to the next Process to be polled, or NULL if all processes have been polled.

Correctness Verdict: Incorrect

Semantic Alignment:
The function intends to poll processes in priority order, advancing through priority entries as each becomes exhausted. However, the implementation contains two critical bugs related to handling empty priority entries:

1. When the current entry is empty, poll_next_p_process_from__process_priority_table_entry returns false without writing to *p_ptr_OUT_process. The main function then breaks out of the loop and returns p_process, which is NULL (on first call) or a stale value from a previously polled process. The function should instead advance to the next entry and continue polling, skipping empty entries entirely.

2. When an entry is exhausted (poll returns true) and the next entry is empty, the poll function returns false without modifying p_process. The main function breaks and returns the stale p_process from the previous entry's last process, rather than skipping the empty entry and continuing to the next non-empty entry.

Both bugs stem from the function not distinguishing between "entry is empty" (should skip to next entry) and "entry has more processes" (should return the process) when poll_next_p_process_from__process_priority_table_entry returns false.

Additionally, the loop variable process_priority is never used inside the loop body — the function relies entirely on p_process_priority_table_entry__current for iteration. While not a correctness bug, this is a code smell.

Implementation Correctness:
- Type compatibility: p_process_table parameter is Process_Table *, matching the type expected by all callees. The return type is Process *, matching the declared return type. No implicit conversions or truncation.
- Undefined behavior: No direct undefined behavior in pointer arithmetic or null dereference (assuming pre-conditions are met). However, the stale p_process return constitutes a logic error that could lead to incorrect process execution.
- The loop bound (PROCESS_MAX_PRIORITY_LEVEL iterations) is sufficient to cover all non-sentinel entries (indices 0 to PROCESS_MAX_PRIORITY_LEVEL-1) plus the wrap check for the sentinel entry at index PROCESS_MAX_PRIORITY_LEVEL.
- Validation: No input validation is performed, which is appropriate for this low-level function — the caller is responsible for ensuring p_process_table is valid.

Side Effects:
- Mutates p_process_table->p_process_priority_table_entry__current (advances it to the next entry when the current entry is exhausted, or resets it to the beginning on wrap-around).
- Mutates p_process_priority_table_entry->p_ptr_process__current_priority_to__swap through the callee poll_next_p_process_from__process_priority_table_entry.
- Returns a pointer to a Process (the next process to execute) or NULL.
