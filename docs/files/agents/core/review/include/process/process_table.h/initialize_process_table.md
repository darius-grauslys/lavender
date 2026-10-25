initialize_process_table — core/source/process/process_table.c

Resets a Process_Table struct to its initial (zeroed) state and sets the current priority table entry pointer to the first element of the priority table array.

Pre-conditions:
1. p_process_table must be a non-null pointer to a writable Process_Table object.

Post-conditions:
1. All bytes of the Process_Table are zeroed via memset.
2. p_process_priority_table_entry__current is set to point to the first element of process_priority_table.

Correctness Verdict: Correct

Semantic Alignment:
This is Lavender-style initialization (cleanup to initial conditions / pool reset), not RAII. The function zeroes all fields of the Process_Table struct and then positions the current pointer at the start of the priority table array, which is the correct initial state for polling.

The Process_Table struct has three fields:
- process_priority_table[PROCESS_MAX_PRIORITY_LEVEL + 1]
- ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF]
- p_process_priority_table_entry__current

The memset zeroes all three fields, and then p_process_priority_table_entry__current is explicitly set to &process_priority_table[0]. No fields are omitted or reordered.

Implementation Correctness:
Type compatibility — sizeof(Process_Table) is correct for the memset size. The assignment of p_process_priority_table_entry__current to p_process_table->process_priority_table is valid: process_priority_table is an array of Process_Priority_Table_Entry, and when used in this context it decays to a pointer to its first element (Process_Priority_Table_Entry *), which matches the type of p_process_priority_table_entry__current.
No undefined behavior — no null dereference (assuming pre-condition holds), no broken pointer arithmetic, no type punning, no out-of-bounds access.
No validation is needed — this is a low-level initialization function. The caller is responsible for ensuring p_process_table is valid.

Side Effects:
Mutates the Process_Table pointed to by p_process_table: all fields are zeroed, and p_process_priority_table_entry__current is set to point to the first element of process_priority_table.
