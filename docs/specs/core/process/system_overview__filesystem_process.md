# 1. System Overview: Filesystem Process

## 1.1 Purpose

The filesystem process pattern wraps a `Serialization_Request` as a
process's `p_process_data`, enabling cooperative file reading and writing
over multiple poll cycles. This prevents file I/O from blocking the main
loop on single-core hardware where all operations must share a single
thread of execution.

Filesystem processes are used throughout the engine for chunk saving,
collision node persistence, local space node saving, and any other
operation that requires reading from or writing to persistent storage.

## 1.2 Architecture

### 1.2.1 Data Layout

    Process
    +-- m_process_run__handler    -> file I/O handler
    +-- m_process_dispose__handler -> (caller-defined or NULL)
    +-- void *p_process_data      -> Serialization_Request*
    |                                +-- void *p_data -> user data (e.g. struct to read into)
    |                                +-- Serialization_Header *p_serialization_header
    |                                +-- void *p_file_handler -> platform file handle
    |                                +-- Quantity__u32 quantity_of__file_contents
    +-- Process_Kind = Process_Kind__Serialized
    +-- Process_Flags__u8: PROCESS_FLAG__IS_CRITICAL (automatically set)
    +-- process_sub_state__u8 (handler state machine)
    +-- scratch values (handler working data)

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Process` | The cooperative task unit carrying the file I/O operation. |
| `Serialization_Request` | Wraps the file handle, user data pointer, and file size tracking. Allocated from the platform's serialization request pool. |
| `IO_path` | Fixed-size path string for file system operations. |
| `PLATFORM_Read_File_Error` | Return type from `PLATFORM_read_file`. |
| `PLATFORM_Write_File_Error` | Return type from `PLATFORM_write_file`. |

## 1.3 Initialization

### 1.3.1 Low-Level Initialization

    initialize_process_as__filesystem_process(
            p_process,
            p_serialization_request,
            p_data);

Sets:
- `p_process->p_process_data` = `p_serialization_request`
- `p_serialization_request->p_data` = `p_data`
- `p_process->the_kind_of__process_this__process_is` = `Process_Kind__Serialized`

This is the low-level initializer. The caller must have already allocated
the `Serialization_Request` and opened the file.

### 1.3.2 High-Level Initialization

    bool success = initialize_process_as__filesystem_process__open_file(
            p_game,
            p_process,
            path,
            file_descriptors,  // e.g. "rb", "wb"
            p_data,
            accept_non_existing);

This function performs the full setup sequence:

1. Allocates a `Serialization_Request` via
   `PLATFORM_allocate_serialization_request`.
2. Opens the file at `path` with the given descriptors via
   `PLATFORM_open_file`.
3. Calls `initialize_process_as__filesystem_process` with the allocated
   request and user data.
4. Automatically sets the `PROCESS_FLAG__IS_CRITICAL` flag (file I/O
   processes should not be skipped).

**Returns:** true on success, false on failure.

**Failure cases:**
- `PLATFORM_allocate_serialization_request` returns NULL (pool exhausted).
- `PLATFORM_open_file` returns an error.
- `accept_non_existing` is false and the file does not exist.

On failure, the process is marked as failed (`fail_process`).

## 1.4 Lifecycle

### 1.4.1 Process Creation and File Open

    Process *p_proc = run_process(
            &game.process_manager,
            my_file_handler,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    bool ok = initialize_process_as__filesystem_process__open_file(
            p_game, p_proc,
            "/saves/chunk_0_0.dat",
            "rb",
            &my_data_struct,
            false);

    if (!ok) {
        // Process already failed. It will be released next poll cycle.
    }

### 1.4.2 Cooperative File I/O (Per Poll Cycle)

Each poll cycle, the handler reads or writes one chunk of data:

    void my_file_handler(Process *p_proc, Game *p_game) {
        Serialization_Request *p_sr =
            (Serialization_Request*)p_proc->p_process_data;

        switch (p_proc->process_sub_state__u8) {
            case 0: // Read phase
            {
                Quantity__u32 bytes = sizeof(MyData);
                PLATFORM_Read_File_Error err = PLATFORM_read_file(
                        get_p_PLATFORM_file_system_context_from__game(p_game),
                        (u8*)p_sr->p_data,
                        &bytes,
                        1,
                        p_sr->p_file_handler);

                if (err == PLATFORM_Read_File_Error__None) {
                    set_process__sub_state(p_proc, 1);
                } else {
                    fail_process(p_proc);
                }
                break;
            }
            case 1: // Finalize
                deactivate_serialization_request(
                        get_p_PLATFORM_file_system_context_from__game(p_game),
                        p_sr);
                complete_process(p_proc);
                break;
        }
    }

### 1.4.3 File Close and Cleanup

The file must be closed and the serialization request released before or
during process disposal:

    deactivate_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game),
            p_serialization_request);

This function:
- Closes the file handle via the platform layer.
- Returns the `Serialization_Request` to the platform's pool.

This can be called either:
- By the handler itself (before `complete_process`), or
- By a custom dispose handler.

### 1.4.4 Lifecycle Diagram

    [run_process] --> initialize_process_as__filesystem_process__open_file
                          |
                          v
                  [PLATFORM_allocate_serialization_request]
                  [PLATFORM_open_file]
                  [Process_Kind = Serialized, IS_CRITICAL set]
                          |
                          v
                  +-----> [Handler invoked each poll cycle]
                  |           |
                  |           v
                  |   [PLATFORM_read_file / PLATFORM_write_file]
                  |           |
                  |       [More I/O needed?] --Yes--> (next poll cycle) --+
                  |           |                                            |
                  |          No                                            |
                  |           |                                            |
                  |   [deactivate_serialization_request]                   |
                  |   [complete_process / fail_process]                    |
                  |           |                                            |
                  |   [Process released by Process_Manager]                |
                  |           |                                            |
                  |       [Slot freed]                                     |
                  |                                                        |
                  +--------------------------------------------------------+

## 1.5 Multi-Step File I/O Pattern

For large files that cannot be read in a single call, the handler uses
scratch values to track progress:

    void my_chunked_reader(Process *p_proc, Game *p_game) {
        Serialization_Request *p_sr =
            (Serialization_Request*)p_proc->p_process_data;

        Quantity__u32 bytes_per_step = 256;
        Quantity__u32 offset = (Quantity__u32)p_proc->process_valueA__i32;
        Quantity__u32 total = p_sr->quantity_of__file_contents;

        if (offset >= total) {
            deactivate_serialization_request(
                    get_p_PLATFORM_file_system_context_from__game(p_game),
                    p_sr);
            complete_process(p_proc);
            return;
        }

        Quantity__u32 to_read = bytes_per_step;
        if (offset + to_read > total) {
            to_read = total - offset;
        }

        PLATFORM_Read_File_Error err = PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game),
                ((u8*)p_sr->p_data) + offset,
                &to_read,
                1,
                p_sr->p_file_handler);

        if (err == PLATFORM_Read_File_Error__None) {
            p_proc->process_valueA__i32 = (i32)(offset + to_read);
        } else {
            fail_process(p_proc);
        }
    }

## 1.6 Engine Usage

The following engine processes use the filesystem process pattern:

| Process Handler | Purpose |
|-----------------|---------|
| `m_process__save_chunk` | Saves chunk tile data to persistent storage. |
| `m_process__save_collision_node` | Saves collision node state to persistent storage. |
| `m_process__save_local_space_node` | Saves local space node state to persistent storage. |

These handlers are run via `run_process` with appropriate priorities and
use `initialize_process_as__filesystem_process__open_file` for setup.

## 1.7 Important Constraints

### 1.7.1 Critical Flag

Filesystem processes automatically have `PROCESS_FLAG__IS_CRITICAL` set.
This ensures the scheduler does not skip them, preventing data corruption
from partially written files.

### 1.7.2 Serialization Request Pool

The number of available `Serialization_Request` instances is limited by
the platform's pool size. If the pool is exhausted,
`initialize_process_as__filesystem_process__open_file` fails and the
process is marked as failed.

### 1.7.3 File Handle Lifetime

The file handle in `Serialization_Request.p_file_handler` remains open
for the entire lifetime of the process. The handler MUST call
`deactivate_serialization_request` before or during disposal to close
the file and return the serialization request to the pool.

Failing to close the file handle leaks both the file descriptor and the
serialization request slot.

### 1.7.4 Preconditions

- `initialize_process_as__filesystem_process__open_file`:
  - `path` must be a valid file path within `MAX_LENGTH_OF__IO_PATH`.
  - `file_descriptors` must be a valid C file mode string (e.g. "rb", "wb").
  - If `accept_non_existing` is false, the file must exist.
  - The `Game` must have a valid `PLATFORM_File_System_Context`.

### 1.7.5 Postconditions

- After successful initialization: `p_process->p_process_data` points to
  an active `Serialization_Request` with an open file handle.
- After failed initialization: the process is marked as failed. No file
  is open. No serialization request is leaked.
- After `deactivate_serialization_request`: the file is closed and the
  serialization request is returned to the pool.

## 1.8 Relationship to Platform Layer

All file I/O is performed through platform-opaque function calls:

| Concern | Platform Function |
|---------|-------------------|
| Serialization request allocation | `PLATFORM_allocate_serialization_request` |
| File open | `PLATFORM_open_file` |
| File read | `PLATFORM_read_file` |
| File write | `PLATFORM_write_file` |
| File close and request release | `deactivate_serialization_request` |

The `PLATFORM_File_System_Context` type is defined per-platform but
accessed uniformly through these interfaces.

## 1.9 Relationship to Other Process Types

| Concern | Managed By |
|---------|------------|
| File I/O wrapping and initialization | `filesystem_process.h` (this module) |
| Game action wrapping | `game_action_process.h` |
| TCP fragment communication | `tcp_game_action_process.h` |
| Process allocation and scheduling | `Process_Manager` / `Process_Table` |

Filesystem processes are independent of game action processes. They use
`Process_Kind__Serialized` rather than `Process_Kind__Game_Action`, and
they do not interact with the `Game_Action_Manager` or TCP subsystems.
