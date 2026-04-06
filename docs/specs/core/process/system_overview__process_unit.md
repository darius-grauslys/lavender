# 1. System Overview: Process Unit

## 1.1 Purpose

The `Process` struct is the engine's fundamental cooperative task unit. It
represents a single schedulable task that runs one step per poll cycle,
yielding control back to the scheduler after each invocation. This design
brings multi-threading-like capabilities to single-core hardware where
preemptive multithreading is not available.

Each `Process` carries its own run handler, dispose handler, opaque data
pointer, status, kind, priority, flags, and scratch values. The process
does not own its scheduling — that is managed by the `Process_Table` and
`Process_Manager`. The process only owns its own state and lifecycle
transitions.

## 1.2 Architecture

### 1.2.1 Data Layout

    Process
    +-- Serialization_Header _serialization_header
    |   +-- Quantity__u32 size_of__struct
    |   +-- Identifier__u32 uuid
    |
    +-- m_Process m_process_run__handler       (function pointer)
    +-- m_Process m_process_dispose__handler    (function pointer)
    |
    +-- union
    |   +-- Process *p_enqueued_process        (chained process)
    |   +-- Process *p_sub_process             (child process)
    |
    +-- void *p_process_data                   (opaque working data)
    |   +-- Game_Action*                       (in game action mode)
    |   +-- Serialization_Request*             (in serialized/TCP mode)
    |
    +-- union (scratch values)
    |   +-- i32 process_valueA__i32, process_valueB__i32
    |   +-- i16 process_valueA__i16 .. process_valueD__i16
    |   +-- u8  process_sub_state__u8
    |   +-- u8  process_value_bytes__u8[8]
    |
    +-- Process_Status_Kind the_kind_of_status__this_process_has
    +-- Process_Kind the_kind_of__process_this__process_is
    +-- Process_Flags__u8 process_flags__u8
    +-- Process_Priority__u8 process_priority__u8

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Process` | The cooperative task unit. Contains all state needed for scheduling, execution, and cleanup. |
| `m_Process` | Function pointer type: `void (*)(Process*, Game*)`. Used for both run and dispose handlers. |
| `Process_Status_Kind` | Enum tracking the process's lifecycle state (None, Idle, Busy, Stopping, Stopped, Enqueued, Complete, Fail). |
| `Process_Kind` | Enum discriminating the process type (None, Generic, Serialized, Game_Action). |
| `Process_Flags__u8` | Bit flags for critical and sub-process markers. |
| `Process_Priority__u8` | Priority level (0 = maximum, `PROCESS_MAX_PRIORITY_LEVEL - 1` = minimum). |
| `Serialization_Header` | UUID and struct size for pool management and hashed lookup. |

### 1.2.3 Status States

| Status | Meaning | Schedulable | Terminal |
|--------|---------|-------------|----------|
| `None` | Slot is available for allocation. | No | — |
| `Idle` | Active, waiting to be polled. | Yes | No |
| `Busy` | Active, currently executing work. | Yes | No |
| `Stopping` | External stop requested; handler should wind down. | Yes | No |
| `Stopped` | Handler has acknowledged the stop. | No | Yes |
| `Enqueued` | Waiting behind another process. | No | No |
| `Complete` | Finished successfully. | No | Yes |
| `Fail` | Finished with error. | No | Yes |

### 1.2.4 Flags

| Flag | Bit | Description |
|------|-----|-------------|
| `PROCESS_FLAG__IS_CRITICAL` | 0 | Process cannot be preempted or skipped during scheduling. |
| `PROCESS_FLAG__IS_SUB_PROCESS` | 1 | Process is a child of another process. |

## 1.3 Cooperative Execution Model

Processes are **cooperative** and **non-preemptive**:

- The scheduler invokes `m_process_run__handler(p_process, p_game)` once
  per poll cycle.
- The handler must return promptly. Long-running work must be split across
  multiple invocations.
- The scheduler does not interrupt a running handler.

### 1.3.1 State Machine Pattern

Handlers that perform multi-step work use `process_sub_state__u8` as a
state machine discriminator:

    void my_handler(Process *p_this_process, Game *p_game) {
        switch (p_this_process->process_sub_state__u8) {
            case 0:
                // Step 1: setup
                set_process__sub_state(p_this_process, 1);
                break;
            case 1:
                // Step 2: incremental work
                if (done) {
                    set_process__sub_state(p_this_process, 2);
                }
                break;
            case 2:
                // Step 3: finalize
                complete_process(p_this_process);
                break;
        }
    }

### 1.3.2 Scratch Value Convention

The scratch value union provides flexible storage for handler-local state
that persists across poll cycles:

| Access Pattern | Fields | Use Case |
|----------------|--------|----------|
| Two 32-bit values | `process_valueA__i32`, `process_valueB__i32` | Counters, indices, accumulated results |
| Four 16-bit values | `process_valueA__i16` .. `process_valueD__i16` | Compact multi-field state |
| Byte array | `process_value_bytes__u8[8]` | Raw byte storage |
| Sub-state byte | `process_sub_state__u8` | State machine discriminator |

All scratch values occupy the same memory (union). Only one access pattern
should be used per process instance.

## 1.4 Lifecycle

### 1.4.1 Initialization

A process is initialized in one of three ways:

**Empty (pool reset):**

    initialize_process_as__empty_process(p_process);
        -> UUID = IDENTIFIER__UNKNOWN__u32
        -> Status = None
        -> All handlers = NULL
        -> All scratch values = 0

**Full initialization:**

    initialize_process(
        p_process,
        uuid,
        m_run_handler,
        p_data,
        priority,
        flags);
        -> UUID set
        -> Status = Idle
        -> Run handler set
        -> p_process_data = p_data
        -> Priority and flags set

**Serialized process:**

    initialize_process_as__serialized_process(
        p_process,
        uuid,
        m_run_handler,
        p_serialization_request,
        priority,
        flags);
        -> Same as full initialization, plus:
        -> Kind = Process_Kind__Serialized
        -> IS_CRITICAL flag automatically set
        -> p_process_data = p_serialization_request

### 1.4.2 Execution (Per Poll Cycle)

Each poll cycle, the scheduler invokes:

    p_process->m_process_run__handler(p_process, p_game);

The handler performs one unit of work and returns. The process remains
in `Idle` or `Busy` status until it transitions to a terminal state.

### 1.4.3 Completion

Within the handler:

    // Success:
    complete_process(p_this_process);
    // Status -> Complete

    // Failure:
    fail_process(p_this_process);
    // Status -> Fail

After the handler returns, the scheduler detects the terminal status and
releases the process via `Process_Manager`.

### 1.4.4 External Stop

An external caller can request a stop:

    stop_process(p_process);
    // Status -> Stopping

The handler should check for `Stopping` status and wind down gracefully:

    if (p_this_process->the_kind_of_status__this_process_has
            == Process_Status_Kind__Stopping) {
        // Clean up...
        set_process_as__stopped(p_this_process);
        return;
    }

### 1.4.5 Disposal

When the scheduler releases a finished process:

    // Invoked by Process_Manager:
    p_process->m_process_dispose__handler(p_process, p_game);
    // Then: slot reset to empty (UUID = IDENTIFIER__UNKNOWN__u32, Status = None)

### 1.4.6 Status Lifecycle Diagram

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
                      release (dispose)               [Stopped]
                                  |                       |
                              [None]              release (dispose)
                                                          |
                                                      [None]

## 1.5 Process Enqueueing

Processes can be chained so that one runs only after another completes:

    enqueue_process(p_second, p_first);
        -> p_first->p_enqueued_process = p_second
        -> p_second status -> Enqueued

While enqueued, `p_second` is not polled by the scheduler. When `p_first`
completes or fails, the scheduler dequeues `p_second`:

    set_process_as__dequeued(p_second);
        -> p_second status -> Idle (now schedulable)

### 1.5.1 Constraints

- A process cannot be enqueued behind itself. `enqueue_process` calls
  `debug_error` if this is attempted.
- The `p_enqueued_process` and `p_sub_process` fields share a union.
  A process can have either an enqueued process or a sub-process, not both.

## 1.6 Opaque Data Pointer

The `p_process_data` field is a `void*` that carries the process's working
data. Its interpretation depends on the process kind:

| Process Kind | p_process_data Points To | Set By |
|--------------|--------------------------|--------|
| `Process_Kind__Generic` | Caller-defined data | `initialize_process` |
| `Process_Kind__Game_Action` | `Game_Action*` | `initialize_process_as__game_action_process` |
| `Process_Kind__Serialized` | `Serialization_Request*` | `initialize_process_as__serialized_process` or `initialize_process_as__filesystem_process` |
| TCP receiver mode | `Serialization_Request*` (with `Game_Action*` in `.p_data`) | `set_game_action_process_as__tcp_payload_receiver` |

The caller is responsible for releasing `p_process_data` before calling
`complete_process` or `fail_process`, unless a dispose handler is set that
handles cleanup automatically.

## 1.7 Capacity Constraints

- Processes are allocated from a fixed pool of `PROCESS_MAX_QUANTITY_OF`
  (512) slots in the `Process_Manager`.
- Each process occupies exactly one slot. The slot is identified by its
  `Serialization_Header.uuid`.
- Priority must be in the range 0 to `PROCESS_MAX_PRIORITY_LEVEL - 1` (0..3).

## 1.8 Relationship to Scheduling

The `Process` struct does not schedule itself. Scheduling is managed by:

| Concern | Managed By |
|---------|------------|
| Pool allocation and UUID assignment | `Process_Manager` |
| Priority-partitioned round-robin polling | `Process_Table` |
| Per-priority-level region management | `Process_Priority_Table_Entry` |
| Handler invocation and lifecycle transitions | `Process_Manager.poll_process_manager` |

The process only owns its own state transitions (`complete_process`,
`fail_process`, `stop_process`, `set_process_as__stopped`) and its
handler implementations.
