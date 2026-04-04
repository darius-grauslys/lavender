# Specification: core/include/process/process.h

## Overview

Provides initialization, status management, and flag manipulation for the
`Process` struct — the engine's cooperative, non-preemptive task unit. Each
`Process` represents a single schedulable task that runs one step per poll
cycle, yielding control back to the scheduler after each invocation.

This is the foundational building block of the engine's multithreading
abstraction, designed to bring multi-threading-like capabilities to
single-core retro console hardware (e.g. Nintendo DS).

## Dependencies

- `defines.h` (for `Process`, `Process_Status_Kind`, `Process_Kind`,
  `Process_Flags__u8`, `Process_Priority__u8`, `m_Process`,
  `Identifier__u32`, `Serialization_Request`)
- `defines_weak.h` (forward declarations)
- `serialization/serialization_header.h` (for `IDENTIFIER__UNKNOWN__u32`)
- `timer.h` (for timer utilities)

## Types

### Process (struct)

    typedef struct Process_t {
        Serialization_Header _serialization_header;
        m_Process m_process_run__handler;
        m_Process m_process_dispose__handler;
        union {
            Process *p_enqueued_process;
            Process *p_sub_process;
        };
        void *p_process_data;
        union {
            struct {
                i32 process_valueA__i32;
                i32 process_valueB__i32;
            };
            struct {
                i16 process_valueA__i16;
                i16 process_valueB__i16;
                i16 process_valueC__i16;
                i16 process_valueD__i16;
            };
            union {
                u8 process_sub_state__u8;
                u8 process_value_bytes__u8[sizeof(i32)*2];
            };
        };
        Process_Status_Kind the_kind_of_status__this_process_has;
        Process_Kind the_kind_of__process_this__process_is;
        Process_Flags__u8 process_flags__u8;
        Process_Priority__u8 process_priority__u8;
    } Process;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management. |
| `m_process_run__handler` | `m_Process` | The function invoked each poll cycle. Signature: `void (*)(Process*, Game*)`. |
| `m_process_dispose__handler` | `m_Process` | Called when the process is released. Used for cleanup. |
| `p_enqueued_process` / `p_sub_process` | `Process*` | Union: either a process enqueued behind this one, or a sub-process. |
| `p_process_data` | `void*` | Opaque pointer to the process's working data (e.g. `Game_Action*`, `Serialization_Request*`). |
| `process_valueA__i32` / `process_valueB__i32` | `i32` | Free-use scratch values for the process handler. |
| `process_sub_state__u8` | `u8` | Sub-state byte for state machine implementations within a process. |
| `the_kind_of_status__this_process_has` | `Process_Status_Kind` | Current lifecycle status. |
| `the_kind_of__process_this__process_is` | `Process_Kind` | Discriminator for process type. |
| `process_flags__u8` | `Process_Flags__u8` | Flags (critical, sub-process). |
| `process_priority__u8` | `Process_Priority__u8` | Priority level (0 = maximum). |

### Process_Status_Kind (enum)

    typedef enum Process_Status_Kind {
        Process_Status_Kind__None = 0,   // Available for allocation
        Process_Status_Kind__Stopped,    // Manually stopped
        Process_Status_Kind__Idle,       // Active but waiting
        Process_Status_Kind__Busy,       // Active and running
        Process_Status_Kind__Stopping,   // Requested to stop
        Process_Status_Kind__Enqueued,   // Waiting behind another process
        Process_Status_Kind__Complete,   // Finished successfully
        Process_Status_Kind__Fail,       // Finished with error
        Process_Status_Kind__Unknown
    } Process_Status_Kind;

### Process_Kind (enum)

    typedef enum Process_Kind {
        Process_Kind__None,
        Process_Kind__Generic,
        Process_Kind__Serialized,
        Process_Kind__Game_Action,
        Process_Kind__Unknown
    } Process_Kind;

### Process_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `PROCESS_FLAG__IS_CRITICAL` | 0 | If set, the process cannot be preempted or skipped. |
| `PROCESS_FLAG__IS_SUB_PROCESS` | 1 | If set, this process is a child of another process. |

### Process_Priority__u8 (u8)

| Constant | Value | Description |
|----------|-------|-------------|
| `PROCESS_PRIORITY__0_MAXIMUM` | 0 | Highest priority. Polled first. |
| `PROCESS_PRIORITY__1` | 1 | Second priority level. |
| `PROCESS_PRIORITY__MINIMUM` | `PROCESS_MAX_PRIORITY_LEVEL - 1` | Lowest priority. |

### m_Process (function pointer)

    typedef void (*m_Process)(
            Process *p_this_process,
            Game *p_game);

The handler signature for all process run and dispose handlers.

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `PROCESS_MAX_QUANTITY_OF` | 512 | Maximum number of processes in the pool. |
| `PROCESS_MAX_PRIORITY_LEVEL` | 4 | Number of priority levels (must be 1..255). |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process` | `(Process*, Identifier__u32 uuid, m_Process run_handler, void* data, Process_Priority__u8, Process_Flags__u8) -> void` | Full initialization with all parameters. |
| `initialize_process_as__empty_process` | `(Process*) -> void` | Initializes as an empty, unallocated process with UUID `IDENTIFIER__UNKNOWN__u32`. (static inline) |
| `initialize_process_as__serialized_process` | `(Process*, Identifier__u32 uuid, m_Process run_handler, Serialization_Request*, Process_Priority__u8, Process_Flags__u8) -> void` | Initializes for serialization I/O. Automatically sets `IS_CRITICAL`. (static inline) |

### Status Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `complete_process` | `(Process*) -> void` | `void` | Sets status to `Complete`. Caller must release `p_process_data` first. |
| `fail_process` | `(Process*) -> void` | `void` | Sets status to `Fail`. Caller must release `p_process_data` first. |
| `stop_process` | `(Process*) -> void` | `void` | Sets status to `Stopping`. |
| `set_process_as__stopped` | `(Process*) -> void` | `void` | Sets status to `Stopped`. |
| `get_process_status` | `(Process*) -> Process_Status_Kind` | `Process_Status_Kind` | Returns current status. |

### Status Queries (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `is_process__active` | `bool` | True if `Busy`, `Idle`, or `Stopping`. |
| `is_process__finished` | `bool` | True if `Complete`, `Fail`, or `Stopped`. |
| `is_process__complete` | `bool` | True if `Complete`. |
| `is_process__failed` | `bool` | True if `Fail`. |
| `is_process__enqueued` | `bool` | True if `Enqueued`. |
| `is_process__available` | `bool` | True if `None` (available for allocation). |

### Enqueueing (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `enqueue_process` | `(Process* to_enqueue, Process* enqueue_behind) -> void` | Links `to_enqueue` behind `enqueue_behind`. Sets `to_enqueue` as `Enqueued`. Cannot enqueue a process behind itself. |
| `set_process_as__enqueued` | `(Process*) -> void` | Sets status to `Enqueued`. |
| `set_process_as__dequeued` | `(Process*) -> void` | Sets status to `Idle`. |

### Handler Queries (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `does_process_have__run_handler` | `bool` | True if `m_process_run__handler` is non-null. |
| `does_process_have__dispose_handler` | `bool` | True if `m_process_dispose__handler` is non-null. |
| `set_process__dispose_handler` | `void` | Sets the dispose handler. |

### Flag Management (static inline)

| Function | Description |
|----------|-------------|
| `is_process__critical` | True if `IS_CRITICAL` flag is set. |
| `set_process_as__critical` | Sets `IS_CRITICAL` flag. |
| `set_process_as__NOT_critical` | Clears `IS_CRITICAL` flag. |
| `is_process__sub_process` | True if `IS_SUB_PROCESS` flag is set. |
| `set_process_as__sub_process` | Sets `IS_SUB_PROCESS` flag. |
| `set_process_as__NOT_sub_process` | Clears `IS_SUB_PROCESS` flag. |

### Kind Management (static inline)

| Function | Description |
|----------|-------------|
| `get_the_kind_of__process` | Returns `Process_Kind`. |
| `set_the_kind_of__process` | Sets `Process_Kind`. |
| `get_process_priorty_of__process` | Returns `Process_Priority__u8`. |

### Sub-State (static inline)

| Function | Description |
|----------|-------------|
| `set_process__sub_state` | Sets `process_sub_state__u8`. Used for state machines within a process handler. |

## Agentic Workflow

### Cooperative Scheduling Model

Processes are **cooperative** and **non-preemptive**:

- Each process handler (`m_process_run__handler`) is invoked once per poll
  cycle by the `Process_Manager`.
- The handler must return promptly. Long-running work must be split across
  multiple invocations using `process_sub_state__u8` or similar state tracking.
- The scheduler does not interrupt a running handler.

This design is critical for single-core retro consoles (e.g. Nintendo DS)
where preemptive multithreading is not available.

### Process Lifecycle

    [None] --> initialize_process --> [Idle/Busy]
                                          |
                              m_process_run__handler (each poll)
                                          |
                          +-------+-------+-------+
                          |               |               |
                    complete_process  fail_process   stop_process
                          |               |               |
                     [Complete]        [Fail]        [Stopping]
                          |               |               |
                          +-------+-------+       set_process_as__stopped
                                  |                       |
                      release_process (dispose)       [Stopped]
                                  |                       |
                              [None]              release_process
                                                          |
                                                      [None]

### Scratch Value Convention

The `process_valueA__i32`, `process_valueB__i32` (and their i16/u8 variants)
are free for use by the process handler. Common patterns:

- **Counters**: Track iteration progress across poll cycles.
- **State machines**: Use `process_sub_state__u8` for multi-step operations.
- **Indices**: Track position in arrays being processed incrementally.

### Enqueueing Pattern

Processes can be chained so that one runs after another completes:

    Process *p_first = run_process(...);
    Process *p_second = run_process(...);
    enqueue_process(p_second, p_first);
    // p_second will not run until p_first completes.

### Preconditions

- All `static inline` functions require a non-null `p_process`. Debug builds
  call `debug_abort` on null.
- `complete_process` and `fail_process`: caller must release `p_process_data`
  before calling, as it will be lost when the process is disposed.
- `enqueue_process`: a process cannot be enqueued behind itself.

### Postconditions

- After `complete_process`: `is_process__finished` returns true,
  `is_process__complete` returns true.
- After `fail_process`: `is_process__finished` returns true,
  `is_process__failed` returns true.

### Error Handling

- All status/flag functions call `debug_abort` on null in debug builds.
- `enqueue_process` calls `debug_error` if attempting self-enqueue.
