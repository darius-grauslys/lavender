# System Overview: Process Scheduling System

## Purpose

The process scheduling system provides cooperative, non-preemptive
multitasking for the engine. It is designed to bring multi-threading-like
capabilities to single-core retro console hardware where preemptive
multithreading is not available. Each `Process` represents a single
schedulable task that runs one step per poll cycle, yielding control back
to the scheduler after each invocation.

The system supports priority-based scheduling, round-robin fairness within
priority levels, process enqueueing (chaining), and specialized process
types for game actions, TCP communication, and file system I/O.

## Architecture

### Data Hierarchy

    Game
    +-- Process_Manager
    |   +-- Process[0..PROCESS_MAX_QUANTITY_OF-1]  (process pool)
    |   |   +-- Serialization_Header  (UUID for pool management)
    |   |   +-- m_Process m_process_run__handler
    |   |   +-- m_Process m_process_dispose__handler
    |   |   +-- void *p_process_data
    |   |   |   +-- (Game_Action* in game action mode)
    |   |   |   +-- (Serialization_Request* in serialized/TCP mode)
    |   |   +-- Process *p_enqueued_process / p_sub_process
    |   |   +-- Process_Status_Kind, Process_Kind, Process_Flags__u8
    |   |   +-- Process_Priority__u8
    |   |   +-- Scratch values (i32, i16, u8 unions)
    |   |
    |   +-- Process_Table
    |   |   +-- Process_Priority_Table_Entry[0..PROCESS_MAX_PRIORITY_LEVEL]
    |   |   |   +-- Process **p_ptr_process__youngest_of__priority
    |   |   |   +-- Process **p_ptr_process__oldest_of__priority
    |   |   |   +-- Process **p_ptr_process__current_priority_to__swap
    |   |   |
    |   |   +-- Process *ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF]
    |   |   |   (contiguous pointer array partitioned by priority)
    |   |   |
    |   |   +-- Process_Priority_Table_Entry *p_process_priority_table_entry__current
    |   |
    |   +-- Repeatable_Psuedo_Random  (UUID generation)
    |   +-- Process *p_process__latest  (one-shot latest allocation)
    |   +-- Identifier__u32 next__uuid__u32

### Key Types

| Type | Role |
|------|------|
| `Process_Manager` | Top-level owner. Lives in `Game`. Holds the process pool, the `Process_Table`, and UUID generation state. Central hub for all cooperative task scheduling. |
| `Process` | A single cooperative task. Contains run/dispose handlers, opaque data pointer, status, kind, priority, flags, and scratch values. |
| `Process_Table` | Priority-based scheduling data structure. Maintains a pointer array partitioned by priority level and one `Process_Priority_Table_Entry` per level. |
| `Process_Priority_Table_Entry` | Manages a contiguous region of the pointer array for a single priority level. Supports insertion, removal, compaction, and round-robin polling. |
| `Game_Action` | A game action struct that can be wrapped as a process's `p_process_data` for cooperative game action execution. |
| `Serialization_Request` | A serialization context that can be wrapped as a process's `p_process_data` for file I/O or TCP payload reassembly. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `PROCESS_MAX_QUANTITY_OF` | 512 | Maximum number of processes in the pool. |
| `PROCESS_MAX_PRIORITY_LEVEL` | 4 | Number of priority levels (must be 1..255). |

## Cooperative Scheduling Model

Processes are **cooperative** and **non-preemptive**:

- Each process handler (`m_process_run__handler`) is invoked once per poll
  cycle by the `Process_Manager`.
- The handler must return promptly. Long-running work must be split across
  multiple invocations using `process_sub_state__u8` or similar state
  tracking.
- The scheduler does not interrupt a running handler.

This design is critical for single-core retro consoles where preemptive
multithreading is not available.

## Priority-Partitioned Round-Robin Scheduling

The `Process_Table` implements a priority-partitioned round-robin scheduler.
The pointer array is divided into contiguous regions, one per priority level:

    ptr_array_of__processes layout:
    [Priority 0 youngest ... oldest | Priority 1 youngest ... oldest | ... | Priority N youngest ... oldest]

### Polling Algorithm

1. `begin_polling_of__process_table()` resets the cursor to priority 0.
2. `poll_next_p_process_from__process_table()` returns one process from
   the current priority level via the round-robin cursor.
3. When the current priority level's cursor wraps around, the scheduler
   advances to the next priority level.
4. Returns `NULL` when all levels have been polled for this cycle.

### Priority Level Semantics

- **Priority 0** (`PROCESS_PRIORITY__0_MAXIMUM`): Polled first every cycle.
  Used for critical tasks (e.g. hitbox updates, TCP delivery).
- **Priority 1+**: Polled after all higher priorities. Used for background
  tasks (e.g. chunk generation, file I/O).
- Within a priority level, processes are polled in round-robin order,
  ensuring fairness.

### Pointer Array Compaction

When a process is added or removed, the pointer array must be compacted to
maintain contiguous regions per priority level. The
`Process_Priority_Table_Entry` functions handle this with strict ordering
constraints:

**Insertion into priority N:**

1. Move priority 0 region up by one slot.
2. Move priority 1 region up by one slot.
3. ... (continue through priority N-1)
4. Insert into priority N.

**Removal from priority N:**

1. Remove from priority N (compact within region).
2. Move priority N-1 region down by one slot.
3. ... (continue through priority 0)

Higher priority entries MUST be moved first during insertion and afterwards
during removal.

## Lifecycle

### 1. Initialization

    initialize_process_manager(&game.process_manager);
        -> All PROCESS_MAX_QUANTITY_OF process slots: initialized as empty
           (UUID = IDENTIFIER__UNKNOWN__u32, status = None).
        -> Process_Table: all priority entries initialized, pointer array cleared.
        -> UUID randomizer seeded.

### 2. Process Allocation and Start

    Process *p_proc = run_process(
            &game.process_manager,
            my_handler,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

        -> Generates a random UUID.
        -> Finds an available slot in the process pool (status == None).
        -> Initializes the process with the handler, priority, and flags.
        -> Adds the process to the Process_Table at the correct priority region.
        -> Sets status to Idle/Busy.
        -> Sets p_process__latest for one-shot retrieval.

    // Or with a specific UUID:
    Process *p_proc = run_process_with__uuid(
            &game.process_manager,
            my_handler,
            my_uuid,
            PROCESS_PRIORITY__1,
            PROCESS_FLAG__IS_CRITICAL);

### 3. Per-Frame Scheduling

    // Called once per game tick in the main loop:
    poll_process_manager(&game.process_manager, &game);

The scheduler performs the following each cycle:

1. Calls `begin_polling_of__process_table` to reset the cursor.
2. Calls `poll_next_p_process_from__process_table` repeatedly.
3. For each returned process:
   - Invokes `m_process_run__handler(p_process, p_game)`.
   - After invocation, checks if the process is finished:
     - If complete/failed: releases the process via
       `release_process_from__process_manager`.
     - If the process has an enqueued process: dequeues it (sets the
       enqueued process to Idle).
4. Continues until `poll_next_p_process_from__process_table` returns `NULL`.

### 4. Process Completion

Within a process handler:

    // Success:
    complete_process(p_this_process);
    // Status -> Complete. Process will be released after this poll cycle.

    // Failure:
    fail_process(p_this_process);
    // Status -> Fail. Process will be released after this poll cycle.

    // Request stop (external):
    stop_process(p_this_process);
    // Status -> Stopping. Handler should check and transition to Stopped.

### 5. Process Release

    release_process_from__process_manager(p_game, &process_manager, p_process);
        -> Invokes m_process_dispose__handler (if set).
        -> Removes from Process_Table (compacts pointer array).
        -> Marks slot as available (status = None, UUID = IDENTIFIER__UNKNOWN__u32).

### Process Status Lifecycle

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

## Process Enqueueing

Processes can be chained so that one runs only after another completes:

    Process *p_first = run_process(&pm, handler_a, priority, flags);
    Process *p_second = run_process(&pm, handler_b, priority, flags);
    enqueue_process(p_second, p_first);
    // p_second status -> Enqueued. It will not be polled.
    // When p_first completes, p_second is dequeued (status -> Idle).

A process cannot be enqueued behind itself.

## Specialized Process Types

### Game Action Process

A game action process wraps a `Game_Action` as its `p_process_data`,
enabling the game action to be processed cooperatively over multiple poll
cycles.

**Data pointer chain:**

    Process.p_process_data --> Game_Action

**Lifecycle:**

1. A `Game_Action` is allocated in a `Game_Action_Manager`.
2. `initialize_process_as__game_action_process(p_process, p_game_action)`.
   - Sets `p_process_data` to the game action.
   - Sets `Process_Kind` to `Process_Kind__Game_Action`.
3. The process's `m_process_run__handler` is set to the appropriate handler
   from the `Game_Action_Logic_Table`.
4. The process runs cooperatively, accessing the game action via
   `(Game_Action*)p_this_process->p_process_data`.
5. On completion/failure, the default dispose handler
   (`m_process__dispose_handler__game_action__default`) releases the game
   action from the client's game action manager and releases the
   serialization request if one was allocated.

### TCP Game Action Process

Extends the game action process for TCP multi-packet communication. A
process can act as a TCP payload receiver (reassembling multi-packet
deliveries) or a TCP payload sender (splitting data into delivery
fragments).

**Receiver data pointer chain:**

    Process.p_process_data
        --> Serialization_Request
            .p_data --> Game_Action (original)
            .p_tcp_packet_destination --> destination buffer
            .pM_packet_bitmap --> fragment tracking bitmap (heap allocated)
            .quantity_of__bytes_in__destination --> destination size
            .quantity_of__tcp_packets__anticipated --> expected fragment count

**Receiver lifecycle:**

1. The process handler calls
   `initialize_process_as__tcp_game_action_payload_receiver(p_game, p_proc,
   destination, size)`.
   - Allocates a `Serialization_Request` via
     `PLATFORM_allocate_serialization_request`.
   - Moves the original `Game_Action*` to `Serialization_Request.p_data`.
   - Sets `p_process_data` to the `Serialization_Request`.
2. Each poll cycle, the handler calls
   `poll_game_action_process__tcp_receive(p_game, p_proc)`.
   - Returns `PLATFORM_Read_File_Error__System_Busy` while waiting for
     fragments.
   - Returns `PLATFORM_Read_File_Error__End_Of_File` when all expected
     fragments have arrived.
3. The handler processes the reassembled data in the destination buffer.
4. The dispose handler releases both the serialization request and the
   game action.

**Sender pattern:**

1. Each poll cycle, the handler calls
   `poll_game_action_process__tcp_delivery(p_game, client_uuid,
   response_uuid, source, size, bitmap, bitmap_bits)`.
   - Returns `PLATFORM_Write_File_Error__System_Busy` while fragments
     remain.
   - Returns `PLATFORM_Write_File_Error__Max_Size_Reached` when all
     fragments have been sent.
2. The process does NOT need to be set as a TCP process to use the sender.

**Important constraint:** If `Serialization_Request.p_data` is NOT a
`Game_Action`, you MUST release `p_data` manually before calling
`complete_process` or `fail_process`, because the default dispose handler
assumes `p_data` is a `Game_Action*`.

### Filesystem Process

A filesystem process wraps a `Serialization_Request` as its
`p_process_data`, enabling cooperative file reading and writing over
multiple poll cycles.

**Data pointer chain:**

    Process.p_process_data
        --> Serialization_Request
            .p_data --> user data (e.g. struct to read into)
            .p_file_handler --> platform file handle
            .quantity_of__file_contents --> file size tracking

**Lifecycle:**

1. Call `initialize_process_as__filesystem_process__open_file(p_game,
   p_proc, path, file_descriptors, data, accept_non_existing)`.
   - Allocates a `Serialization_Request` via
     `PLATFORM_allocate_serialization_request`.
   - Opens the file via `PLATFORM_open_file`.
   - Sets `p_process_data` to the `Serialization_Request`.
   - Sets `Process_Kind` to `Process_Kind__Serialized`.
   - Automatically sets `IS_CRITICAL` flag.
   - Returns false on allocation or file open failure.
2. The process handler reads or writes data incrementally each poll cycle
   using `PLATFORM_read_file` / `PLATFORM_write_file` via
   `Serialization_Request.p_file_handler`.
3. On completion, the handler (or dispose handler) calls
   `deactivate_serialization_request` to close the file and release the
   serialization request.

## Integration Points

### Game Loop Integration

The `Process_Manager` is polled once per game tick:

    // Main game loop (simplified):
    while (running) {
        // ... input, world update ...
        poll_process_manager(&game.process_manager, &game);
        // ... rendering ...
    }

### Game Action System Integration

Game actions that require multi-step processing are wrapped in processes:

    Game_Action *p_ga = allocate_game_action(...);
    Process *p_proc = run_process(&pm, ga_handler, priority, flags);
    initialize_process_as__game_action_process(p_proc, p_ga);

The `Game_Action_Logic_Table` maps `Game_Action_Kind` values to process
handlers, enabling the game action system to dispatch actions as
cooperative processes.

### TCP Communication Integration

TCP multi-packet protocols use the TCP game action process pattern:

    // Server sends chunk data to client:
    // 1. Allocate game action for the request.
    // 2. Run a process with a handler that calls
    //    poll_game_action_process__tcp_delivery each cycle.
    // 3. The handler sends one fragment per poll cycle until complete.

    // Client receives chunk data:
    // 1. Receive initial game action via TCP.
    // 2. Run a process with a handler that calls
    //    initialize_process_as__tcp_game_action_payload_receiver (once),
    //    then poll_game_action_process__tcp_receive each cycle.
    // 3. When all fragments arrive, process the reassembled buffer.

### File System Integration

File I/O operations are wrapped in filesystem processes to avoid blocking:

    Process *p_proc = run_process(&pm, file_handler, priority, flags);
    initialize_process_as__filesystem_process__open_file(
        p_game, p_proc, path, "rb", my_data, false);

The platform layer provides `PLATFORM_allocate_serialization_request`,
`PLATFORM_open_file`, `PLATFORM_read_file`, and `PLATFORM_write_file`
for file system operations.

## Scratch Value Conventions

The `process_valueA__i32`, `process_valueB__i32` (and their i16/u8
variants) are free for use by the process handler. Common patterns:

- **Counters**: Track iteration progress across poll cycles.
- **State machines**: Use `process_sub_state__u8` for multi-step
  operations within a single handler.
- **Indices**: Track position in arrays being processed incrementally.

## Capacity Constraints

- The process pool has a fixed size of `PROCESS_MAX_QUANTITY_OF` (512)
  slots. Allocation fails if all slots are occupied.
- The process table pointer array has the same capacity. Each active
  process occupies exactly one slot in the pointer array.
- There are `PROCESS_MAX_PRIORITY_LEVEL` (4) priority levels. A process's
  priority must be in the range 0 to `PROCESS_MAX_PRIORITY_LEVEL - 1`.
- UUID collisions are handled by the hashing/dehashing functions used for
  pool lookup (`dehash_identitier_u32_in__contigious_array`).

## Relationship to Platform Layer

The process system itself is platform-independent. Platform-specific
behavior is accessed through opaque `PLATFORM_*` function calls:

| Concern | Platform Function |
|---------|-------------------|
| Serialization request allocation | `PLATFORM_allocate_serialization_request` |
| File open | `PLATFORM_open_file` |
| File read | `PLATFORM_read_file` |
| File write | `PLATFORM_write_file` |
| Serialization request deactivation | `deactivate_serialization_request` |

The `PLATFORM_File_System_Context` and `Serialization_Request` types are
defined per-platform but accessed uniformly through these interfaces.
