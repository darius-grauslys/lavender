# 1 System Overview: World Serialization

## 1.1 Purpose

The world serialization subsystem handles persistence of world data to and
from the filesystem. It provides path construction for the world's directory
hierarchy and blocking queries for region existence. Serialization is
coordinated through cooperative processes that serialize/deserialize chunks,
collision nodes, local space nodes, and regions.

## 1.2 Architecture

### 1.2.1 Filesystem Hierarchy

    <base_directory>/
    +-- <world_name>/
        +-- h                              <- world header file (seed, spawn, player data)
        +-- <chunk_dir>/                   <- chunk directory (named by position)
            +-- t                          <- chunk tile data file

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `World` | Provides the world name and sub-component access for path construction. |
| `PLATFORM_File_System_Context` | Platform-specific filesystem context. Provides base directory path. |
| `Global_Space` | Represents a loaded chunk. Used to derive chunk directory paths. |
| `Region_Vector__3i32` | Region coordinate for region-level filesystem queries. |

### 1.2.3 Path Construction Functions

| Function | Builds Path To | Returns |
|----------|---------------|---------|
| `stat_world_directory` | `<base>/<world_name>/` | Path length. |
| `stat_world_header_file` | `<base>/<world_name>/h` | Path length. |
| `stat_chunk_directory` | `<base>/<world_name>/<chunk_dir>/` | Path length. |
| `stat_chunk_file__tiles` | `<base>/<world_name>/<chunk_dir>/t` | Path length. |
| `stat_client_file` | Client-specific file path | Path length + base dir index. |
| `open_client_file` | Client-specific file path (creates if absent) | Path length + base dir index. |

### 1.2.4 Path Helper

`append_chunk_file__tiles_to__path` appends `"/t"` to a buffer, used
internally by `stat_chunk_file__tiles`.

## 1.3 Lifecycle

### 1.3.1 World Save

    save_world(p_file_system_context, p_world)
        -> Only called when leaving the world (returning to main menu).
        -> Constructs paths via stat_world_directory / stat_world_header_file.
        -> Serializes world header.
        -> Dispatches cooperative processes for dirty chunks:
           - m_process__serialize_chunk (via chunk.h)
           - m_process__save_collision_node (via process subfolder)
           - m_process__save_local_space_node (via process subfolder)
        -> Region serialization via m_process__serialize_region.

### 1.3.2 World Load

    load_world(p_game) -> Process*
        -> Only called from main menu.
        -> Constructs paths via stat_world_directory / stat_world_header_file.
        -> Deserializes world header.
        -> Dispatches cooperative processes for chunks:
           - m_process__deserialize_chunk (via chunk.h)
        -> Region deserialization via m_process__deserialize_region.

### 1.3.3 Region Existence Check

    is_region_in__directory(p_world, region_vector) -> bool
        -> **WARNING: Blocking filesystem I/O.**
        -> Checks if a region's save data exists on disk.
        -> Should only be called during initialization or from
           contexts where blocking is acceptable.
        -> Must NOT be called from cooperative process handlers.

### 1.3.4 Client File Management

    open_client_file(p_fs_context, p_world, path, uuid, &index) -> Index__u32
        -> Creates client file if not present.
        -> Returns path length and base directory index.

    stat_client_file(p_fs_context, p_world, path, uuid, &index) -> Index__u32
        -> Checks if client file exists (does not create).

## 1.4 Serialization Process Coordination

All chunk and region serialization uses the cooperative process model.
Processes are dispatched and polled once per frame, yielding between
poll cycles to avoid blocking the main loop.

### 1.4.1 Process Dispatch Chain

    Global_Space (dirty, awaiting deconstruction)
        -> dispatch_process__serialize_global_space
            -> m_process__serialize_global_space
                -> m_process__serialize_chunk (tile data)
                -> m_process__save_collision_node
                -> m_process__save_local_space_node

    Global_Space (awaiting construction)
        -> dispatch_process__deserialize_global_space
            -> m_process__deserialize_chunk (tile data)
            OR
            -> chunk generator process (from Chunk_Generator_Table)

### 1.4.2 Region Serialization

    Region (needs save)
        -> m_process__serialize_region
            -> Writes bitmap_of__serialized_chunks
            -> Writes bitmap_of__sites

    Region (needs load)
        -> m_process__deserialize_region
            -> Reads bitmap_of__serialized_chunks
            -> Reads bitmap_of__sites

## 1.5 Platform Integration

The serialization subsystem depends on `PLATFORM_File_System_Context` for
all filesystem operations. This context provides:
- Base directory path
- File open/read/write/close operations
- Serialization request management

The specific implementation is platform-defined. The serialization subsystem
interacts with it only through the `PLATFORM_File_System_Context` pointer
and `Serialization_Request` structures.

## 1.6 Preconditions

- All path construction functions require valid non-null pointers.
- Path buffers must have sufficient space (typically `MAX_LENGTH_OF__IO_PATH`).
- `is_region_in__directory` requires a world with a valid name set.
- `save_world` should only be called when leaving the world.
- `load_world` should only be called from the main menu.
