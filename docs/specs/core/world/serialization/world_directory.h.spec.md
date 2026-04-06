# 1 Specification: core/include/world/serialization/world_directory.h

## 1.1 Overview

Provides filesystem path construction and stat functions for world
serialization. Builds paths to chunk directories, chunk tile files, world
header files, world directories, and client files. Used by serialization
processes to locate save data on disk.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `World`, `Global_Space`, `PLATFORM_File_System_Context`, `IO_path`, `Identifier__u32`)

## 1.3 Functions

### 1.3.1 Path Construction / Stat Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `stat_chunk_directory` | `(PLATFORM_File_System_Context*, World*, Global_Space*, char*) -> Index__u32` | `Index__u32` | Builds path to chunk directory. Returns path length. |
| `stat_chunk_file__tiles` | `(PLATFORM_File_System_Context*, World*, Global_Space*, char*) -> Index__u32` | `Index__u32` | Builds path to chunk tile file. Returns path length. |
| `stat_world_header_file` | `(PLATFORM_File_System_Context*, World*, char*) -> Index__u32` | `Index__u32` | Builds path to world header file (seed, player data). Returns path length. |
| `stat_world_directory` | `(PLATFORM_File_System_Context*, World*, IO_path) -> Index__u32` | `Index__u32` | Builds path to world directory. Returns path length. |
| `open_client_file` | `(PLATFORM_File_System_Context*, World*, IO_path, Identifier__u32, Index__u32*) -> Index__u32` | `Index__u32` | Creates client file if not present. Returns path length. Out-param receives base directory index. |
| `stat_client_file` | `(PLATFORM_File_System_Context*, World*, IO_path, Identifier__u32, Index__u32*) -> Index__u32` | `Index__u32` | Checks if client file exists. Returns path length. Out-param receives base directory index. |

### 1.3.2 Path Helpers (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `append_chunk_file__tiles_to__path` | `(char*, Quantity__u16 length, Quantity__u16 max) -> bool` | `bool` | Appends `"/t"` to the path buffer. Returns false if buffer too small. |

## 1.4 Agentic Workflow

### 1.4.1 Path Convention

World data is stored in a directory hierarchy:
- `<base>/<world_name>/` — world directory
- `<base>/<world_name>/h` — world header file
- `<base>/<world_name>/<chunk_dir>/` — chunk directory
- `<base>/<world_name>/<chunk_dir>/t` — chunk tile data

### 1.4.2 Preconditions

- All functions require valid non-null pointers.
- `char *buffer` must have sufficient space (typically `MAX_LENGTH_OF__IO_PATH`).

## 1.5 Header Guard

`WORLD_DIRECTORY_H`
