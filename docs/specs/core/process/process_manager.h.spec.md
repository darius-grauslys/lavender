# Specification: core/include/process/process_manager.h

## Overview

The `Process_Manager` owns the pool of all `Process` instances and the
`Process_Table` that schedules them. It provides allocation, deallocation,
polling (the main scheduler loop), and convenience functions for running
processes.

The `Process_Manager` lives in `Game` and is the central hub for all
cooperative task scheduling in the engine.

## Dependencies

- `defines.h` (for `Process_Manager`, `Process`, `Process_Table`,
  `Identifier__u32`, `m_Process`, `Process_Priority__u8`, `Process_Flags__u8`)
- `defines_weak.h` (forward declarations)
- `serialization/hashing.h` (for `dehash_identitier_u32_in__contigious_array`)

## Types

### Process_Manager (struct)

    typedef struct Process_Manager_t {
        Process processes[PROCESS_MAX_QUANTITY_OF];
        Process_Table process_table;
        Repeatable_Psuedo_Random repeatable_psuedo_random_for__process_uuid;
        Process *p_process__latest;
        Identifier__u32 next__uuid__u32;
    } Process_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `processes` | `Process[512]` | Contiguous pool of process slots. |
| `process_table` | `Process_Table` | Priority-based scheduling table. |
| `repeatable_psuedo_random_for__process_uuid` | `Repeatable_Psuedo_Random` | Randomizer for UUID generation. |
| `p_process__latest` | `Process*` | Pointer to the most recently allocated process. Consumed by `get_p_latest_allocated_process_from__process_manager`. |
| `next__uuid__u32` | `Identifier__u32` | Next UUID to assign. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `PROCESS_MAX_QUANTITY_OF` | 512 | Maximum number of processes in the pool. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process_manager` | `(Process_Manager*) -> void` | Initializes all process slots as empty, initializes the process table, and seeds the randomizer. |

### Allocation / Deallocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_process_in__process_manager` | `(Process_Manager*, Identifier__u32 uuid, uint32_t priority_level) -> Process*` | `Process*` or `NULL` | Allocates a process slot with the given UUID and priority. Does NOT set the run handler; caller must do so. |
| `release_process_from__process_manager` | `(Game*, Process_Manager*, Process*) -> void` | `void` | Invokes the dispose handler (if any), removes from the process table, and marks the slot as available. |

### Running Processes

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `run_process_with__uuid` | `(Process_Manager*, m_Process, Identifier__u32 uuid, Process_Priority__u8, Process_Flags__u8) -> Process*` | `Process*` or `NULL` | Allocates a process with the given UUID, sets the run handler, adds to the process table, and starts it. |
| `run_process` | `(Process_Manager*, m_Process, uint32_t priority_level, Process_Flags__u8) -> Process*` | `Process*` or `NULL` | Generates a random UUID and calls `run_process_with__uuid`. |

### Polling (Scheduler Loop)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_process_manager` | `(Process_Manager*, Game*) -> Quantity__u32` | `Quantity__u32` | The main scheduler loop. Polls the process table, invoking each active process's run handler once. Returns the number of ticks elapsed. Handles process completion, failure, enqueueing, and disposal. **Do not invoke directly** — called by the game loop. |

### Lookup (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_process_by__uuid` | `(Process_Manager*, Identifier__u32) -> Process*` | `Process*` or `NULL` | UUID-based lookup via `dehash_identitier_u32_in__contigious_array`. |
| `get_p_latest_allocated_process_from__process_manager` | `(Process_Manager*) -> Process*` | `Process*` or `NULL` | Returns `p_process__latest` and clears it. One-shot consumption pattern. |

### Query

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__processes_in__process_manager` | `(Process_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns the total number of active processes across all priority levels. |

## Agentic Workflow

### Initialization Sequence

    initialize_process_manager(&game.process_manager);
    // Process manager is now ready. All 512 slots are available.

### Running a Process

    // Simple: auto-generated UUID
    Process *p_proc = run_process(
            &game.process_manager,
            my_handler,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    // With specific UUID
    Process *p_proc = run_process_with__uuid(
            &game.process_manager,
            my_handler,
            my_uuid,
            PROCESS_PRIORITY__1,
            PROCESS_FLAG__IS_CRITICAL);

### Per-Frame Scheduling

    // Called once per game tick in the main loop:
    poll_process_manager(&game.process_manager, &game);

The scheduler performs the following each cycle:

1. Calls `begin_polling_of__process_table` to reset the cursor.
2. Calls `poll_next_p_process_from__process_table` repeatedly.
3. For each returned process, invokes `m_process_run__handler(p_process, p_game)`.
4. After invocation, checks if the process is finished:
   - If complete/failed: releases the process via `release_process_from__process_manager`.
   - If the process has an enqueued process: dequeues it.
5. Continues until `poll_next_p_process_from__process_table` returns NULL.

### Latest Process Pattern

    run_process(&pm, handler, priority, flags);
    Process *p = get_p_latest_allocated_process_from__process_manager(&pm);
    // p is the process just allocated. p_process__latest is now NULL.
    // This is a one-shot pattern; calling again returns NULL.

### Preconditions

- `initialize_process_manager` must be called before any other operations.
- `run_process` / `run_process_with__uuid` require a free slot in the pool.
- `release_process_from__process_manager` requires a valid `Game*` for
  dispose handler invocation.

### Postconditions

- After `run_process`: the process is in the process table and will be
  polled on the next `poll_process_manager` call.
- After `release_process_from__process_manager`: the process slot is
  available for reuse.

### Error Handling

- `allocate_process_in__process_manager` returns NULL if the pool is full.
- `run_process` / `run_process_with__uuid` return NULL on allocation failure.
