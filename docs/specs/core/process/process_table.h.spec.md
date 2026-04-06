# 1. Specification: core/include/process/process_table.h

## 1.1 Overview

The `Process_Table` is the priority-based scheduling data structure used by
the `Process_Manager`. It maintains an array of `Process_Priority_Table_Entry`
instances (one per priority level) and a pointer array that orders all active
processes by priority for round-robin polling.

The table ensures that higher-priority processes are polled before
lower-priority ones, while processes within the same priority level are
polled in round-robin order.

## 1.2 Dependencies

- `defines.h` (for `Process_Table`, `Process_Priority_Table_Entry`,
  `Process`, `PROCESS_MAX_QUANTITY_OF`, `PROCESS_MAX_PRIORITY_LEVEL`)

## 1.3 Types

### 1.3.1 Process_Table (struct)

    typedef struct Process_Table_t {
        Process_Priority_Table_Entry process_priority_table[
            PROCESS_MAX_PRIORITY_LEVEL + 1];
        Process *ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF];
        Process_Priority_Table_Entry *p_process_priority_table_entry__current;
    } Process_Table;

| Field | Type | Description |
|-------|------|-------------|
| `process_priority_table` | `Process_Priority_Table_Entry[PROCESS_MAX_PRIORITY_LEVEL + 1]` | One entry per priority level, plus one sentinel. |
| `ptr_array_of__processes` | `Process*[512]` | Contiguous pointer array partitioned by priority. Higher priority entries occupy lower indices. |
| `p_process_priority_table_entry__current` | `Process_Priority_Table_Entry*` | Tracks the current priority level being polled. |

### 1.3.2 Process_Priority_Table_Entry (struct)

    typedef struct Process_Priority_Table_Entry_t {
        Process **p_ptr_process__youngest_of__priority;
        Process **p_ptr_process__oldest_of__priority;
        Process **p_ptr_process__current_priority_to__swap;
    } Process_Priority_Table_Entry;

| Field | Type | Description |
|-------|------|-------------|
| `p_ptr_process__youngest_of__priority` | `Process**` | Points to the most recently added process in this priority's region of the pointer array. |
| `p_ptr_process__oldest_of__priority` | `Process**` | Points to the oldest process in this priority's region. |
| `p_ptr_process__current_priority_to__swap` | `Process**` | Round-robin cursor for polling within this priority level. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process_table` | `(Process_Table*) -> void` | Initializes all priority entries and clears the pointer array. |

### 1.4.2 Process Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_process_to__process_table` | `(Process_Table*, Process*) -> bool` | `bool` | Adds a process to the table at its priority level. Returns false on failure (table full or priority level full). |
| `remove_process_from__process_table` | `(Process_Table*, Process*) -> void` | `void` | Removes a process from the table, compacting the pointer array. |

### 1.4.3 Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `begin_polling_of__process_table` | `(Process_Table*) -> void` | Resets the polling cursor to the highest priority level. Must be called before each polling cycle. |
| `poll_next_p_process_from__process_table` | `(Process_Table*) -> Process*` | Returns the next process to run, advancing the round-robin cursor. Returns NULL when all priority levels have been polled for this cycle. |

### 1.4.4 Query

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__processes_in__process_table` | `(Process_Table*) -> Quantity__u32` | `Quantity__u32` | Returns the total number of active processes across all priority levels. |

## 1.5 Agentic Workflow

### 1.5.1 Scheduling Algorithm

The process table implements a **priority-partitioned round-robin** scheduler:

    ptr_array_of__processes layout:
    [Priority 0 processes | Priority 1 processes | ... | Priority N processes]

    Each priority level has a region in the pointer array delimited by
    youngest and oldest pointers. The round-robin cursor advances through
    the region one process per poll cycle.

    Polling order:
    1. begin_polling_of__process_table() resets cursor to priority 0.
    2. poll_next_p_process_from__process_table() returns one process
       from the current priority level.
    3. When the current priority level wraps around, the cursor advances
       to the next priority level.
    4. Returns NULL when all levels have been polled.

### 1.5.2 Priority Level Semantics

- **Priority 0** (`PROCESS_PRIORITY__0_MAXIMUM`): Polled first every cycle.
  Used for critical game actions (e.g. hitbox updates, TCP delivery).
- **Priority 1+**: Polled after all higher priorities. Used for background
  tasks (e.g. chunk generation, file I/O).
- Within a priority level, processes are polled in round-robin order,
  ensuring fairness.

### 1.5.3 Pointer Array Compaction

When a process is removed, the pointer array must be compacted to maintain
contiguous regions per priority level. This is handled by
`remove_process_from__process_table` which shifts pointers and updates
the priority table entry delimiters.

### 1.5.4 Preconditions

- `initialize_process_table` must be called before any operations.
- `add_process_to__process_table` requires the process to have a valid
  priority level (0 to `PROCESS_MAX_PRIORITY_LEVEL - 1`).

### 1.5.5 Postconditions

- After `add_process_to__process_table`: the process is in the pointer
  array at the correct priority region.
- After `remove_process_from__process_table`: the process is no longer
  in the pointer array and the regions are compacted.

### 1.5.6 Error Handling

- `add_process_to__process_table` returns false if the table is full.
