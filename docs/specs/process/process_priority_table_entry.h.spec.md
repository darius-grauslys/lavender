# Specification: core/include/process/process_priority_table_entry.h

## Overview

Provides low-level operations on individual `Process_Priority_Table_Entry`
instances within the `Process_Table`. Each entry manages a contiguous region
of the process pointer array for a single priority level, supporting
insertion, removal, compaction, and round-robin polling.

These functions are internal to the process scheduling system and are
called by `Process_Table` operations. They should not be called directly
by game code.

## Dependencies

- `defines.h` (for `Process_Priority_Table_Entry`, `Process_Table`, `Process`)
- `defines_weak.h` (forward declarations)

## Types

### Process_Priority_Table_Entry (struct)

    typedef struct Process_Priority_Table_Entry_t {
        Process **p_ptr_process__youngest_of__priority;
        Process **p_ptr_process__oldest_of__priority;
        Process **p_ptr_process__current_priority_to__swap;
    } Process_Priority_Table_Entry;

| Field | Type | Description |
|-------|------|-------------|
| `p_ptr_process__youngest_of__priority` | `Process**` | Start of this priority's region (most recently added). |
| `p_ptr_process__oldest_of__priority` | `Process**` | End of this priority's region (oldest). |
| `p_ptr_process__current_priority_to__swap` | `Process**` | Round-robin cursor for polling. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process_priority_table_entry` | `(Process_Priority_Table_Entry*, Process** p_ptr_process__first) -> void` | Initializes the entry with its starting position in the pointer array. |

### Region Movement

These functions shift the priority entry's region within the pointer array
to make room for insertions or to compact after removals. They must be
called in the correct order across priority levels.

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `move_process_priorty_table_entry_up__one_in__ptr_array_of__processes` | `(Process_Table*, Process_Priority_Table_Entry*) -> bool` | `bool` | Shifts the entry's region up by one slot. **Higher priority entries MUST be moved first.** Returns false on failure. |
| `move_process_priorty_table_entry_down__one_in__ptr_array_of__processes` | `(Process_Table*, Process_Priority_Table_Entry*) -> bool` | `bool` | Shifts the entry's region down by one slot. **Higher priority entries MUST be moved afterwards.** Returns false on failure. |

### Insertion / Removal

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_process_to__process_priorty_table_entry_in__ptr_array_of__processes` | `(Process_Table*, Process_Priority_Table_Entry*, Process*) -> bool` | `bool` | Moves the region up by one and inserts the process as the new youngest. **Higher priority entries MUST be moved first.** |
| `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes` | `(Process_Priority_Table_Entry*, Process*) -> bool` | `bool` | Removes the process from this entry's region and compacts. |

### Polling

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_next_p_process_from__process_priority_table_entry` | `(Process_Priority_Table_Entry*, Process** p_ptr_OUT_process) -> bool` | `bool` | Advances the round-robin cursor and writes the next process to `p_ptr_OUT_process`. Returns true when the cursor wraps around (time to move to next priority level). |

### Validation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_process_priority_table_entry__empty` | `(Process_Priority_Table_Entry*) -> bool` | `bool` | Returns true if either delimiter pointer is null. |
| `get_quantity_of__processes_in__process_priority_table_entry` | `(Process_Priority_Table_Entry*) -> Quantity__u32` | `Quantity__u32` | Returns the number of processes in this priority level (oldest - youngest). |

## Agentic Workflow

### Internal Use Only

These functions are called by `Process_Table` operations:

- `add_process_to__process_table` calls
  `add_process_to__process_priorty_table_entry_in__ptr_array_of__processes`
  for the target priority, after moving higher-priority entries up.
- `remove_process_from__process_table` calls
  `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes`
  and then moves higher-priority entries down.

### Ordering Constraints

The pointer array is partitioned by priority:

    [P0 youngest ... P0 oldest | P1 youngest ... P1 oldest | ...]

When inserting into priority N:

1. Move priority 0 up by one.
2. Move priority 1 up by one.
3. Move priority N-1 up by one.
4. Insert into priority N.

When removing from priority N:

1. Remove from priority N.
2. Move priority N-1 down by one.
3. Move priority 0 down by one.

### Preconditions

- The entry must be initialized before any operations.
- Movement functions must be called in the correct priority order.

### Postconditions

- After insertion: the process is the youngest in its priority region.
- After removal: the region is compacted with no gaps.
