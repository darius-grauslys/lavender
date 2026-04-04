# Specification: core/include/process/filesystem_process.h

## Overview

Provides initialization utilities for processes that perform file system
I/O operations. A filesystem process wraps a `Serialization_Request` as
its `p_process_data`, enabling cooperative file reading and writing over
multiple poll cycles.

## Dependencies

- `defines.h` (for `Process`, `Serialization_Request`, `IO_path`, `Game`)

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process_as__filesystem_process` | `(Process*, Serialization_Request*, void* data) -> void` | Sets the process's `p_process_data` to the serialization request and stores `data` in `Serialization_Request.p_data`. Marks the process kind as `Process_Kind__Serialized`. |
| `initialize_process_as__filesystem_process__open_file` | `(Game*, Process*, IO_path path, const char* file_descriptors, void* data, bool accept_non_existing) -> bool` | Higher-level initializer that allocates a `Serialization_Request`, opens the file at `path` with the given descriptors (e.g. "rb", "wb"), and initializes the process. Returns true on success. If the file does not exist and `accept_non_existing` is false, the process is failed. |

## Agentic Workflow

### Filesystem Process Lifecycle

1. Call `initialize_process_as__filesystem_process__open_file` to set up
   the process with an open file handle.
2. The process handler reads or writes data incrementally each poll cycle
   using `PLATFORM_read_file` / `PLATFORM_write_file` via the
   `Serialization_Request.p_file_handler`.
3. On completion, call `complete_process`. The dispose handler (or the
   handler itself) should call `deactivate_serialization_request` to
   close the file and release the serialization request.

### File I/O Pattern

    void my_file_handler(Process *p_proc, Game *p_game) {
        Serialization_Request *p_sr =
            (Serialization_Request*)p_proc->p_process_data;

        switch (p_proc->process_sub_state__u8) {
            case 0: // Read
            {
                Quantity__u32 bytes_to_read = sizeof(MyData);
                PLATFORM_Read_File_Error err = PLATFORM_read_file(
                        get_p_PLATFORM_file_system_context_from__game(p_game),
                        (u8*)p_sr->p_data,
                        &bytes_to_read,
                        1,
                        p_sr->p_file_handler);
                if (err == PLATFORM_Read_File_Error__None) {
                    complete_process(p_proc);
                } else {
                    fail_process(p_proc);
                }
                break;
            }
        }
    }

### Data Pointer Chain (Filesystem mode)

    Process.p_process_data
        --> Serialization_Request
            .p_data --> user data (e.g. struct to read into)
            .p_file_handler --> platform file handle
            .quantity_of__file_contents --> file size tracking

### Preconditions

- `initialize_process_as__filesystem_process__open_file`:
  - `path` must be a valid file path within `MAX_LENGTH_OF__IO_PATH`.
  - `file_descriptors` must be a valid C file mode string (e.g. "rb", "wb").
  - If `accept_non_existing` is false, the file must exist.
- The `Game` must have a valid `PLATFORM_File_System_Context`.

### Postconditions

- After `initialize_process_as__filesystem_process__open_file` returns true:
  - The process's `p_process_data` points to an active `Serialization_Request`.
  - The file is open and ready for I/O.
- After `initialize_process_as__filesystem_process__open_file` returns false:
  - The process is marked as failed.
  - No file is open.

### Error Handling

- Returns false if `PLATFORM_allocate_serialization_request` fails.
- Returns false if `PLATFORM_open_file` returns an error.
- If `accept_non_existing` is false and the file is not found, the process
  is failed and false is returned.
