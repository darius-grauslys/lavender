# 1 System Overview: World Processes

## 1.1 Purpose

The world process subsystem declares cooperative process handlers for
persisting world data. These handlers follow the engine's cooperative
process model — they are polled once per frame, perform incremental work,
and yield promptly to avoid blocking the main loop. Each handler is
responsible for serializing a specific unit of world data to the filesystem.

## 1.2 Architecture

### 1.2.1 Process Handlers

| Handler | Declared In | Serializes | Data Source |
|---------|-------------|------------|-------------|
| `m_process__save_chunk` | `process__save_chunk.h` | Chunk tile data | `p_process->p_process_data` (Chunk/Global_Space) |
| `m_process__save_collision_node` | `process__save_collision_node.h` | Collision node spatial index | `p_process->p_process_data` (Collision_Node) |
| `m_process__save_local_space_node` | `process__save_local_space_node.h` | Local space node data | `p_process->p_process_data` (Local_Space) |

### 1.2.2 Related Handlers (declared elsewhere)

| Handler | Declared In | Purpose |
|---------|-------------|---------|
| `m_process__serialize_chunk` | `chunk.h` | Chunk serialization (may overlap with save_chunk). |
| `m_process__deserialize_chunk` | `chunk.h` | Chunk deserialization. |
| `m_process__serialize_region` | `region.h` | Region bitmap serialization. |
| `m_process__deserialize_region` | `region.h` | Region bitmap deserialization. |
| `m_process__serialize_global_space` | `global_space.h` | Global space serialization orchestrator. |

### 1.2.3 Note: process__load_chunk.h

The `process__load_chunk.h` header is currently a placeholder with no
function declarations. Chunk deserialization is handled by
`m_process__deserialize_chunk` declared in `chunk.h`.

## 1.3 Cooperative Process Model

All process handlers conform to the `m_Process` function pointer signature:

    typedef void (*m_Process)(Process *p_this_process, Game *p_game);

### 1.3.1 Conventions

1. **Data access**: The world data to serialize is accessed via
   `p_process->p_process_data`.
2. **Yielding**: Handlers perform incremental work per poll cycle and
   return promptly. They must not block on filesystem I/O within a
   single invocation.
3. **Completion**: Handlers signal completion through the process
   lifecycle (see `process.h` spec).
4. **Dispatch**: These handlers are not called directly by game code.
   They are dispatched by the global space serialization system
   (e.g., `dispatch_process__serialize_global_space`).

## 1.4 Dispatch Flow

    World save triggered (leaving world)
        |
        v
    For each dirty Global_Space:
        dispatch_process__serialize_global_space(p_game, p_global_space)
            |
            +-> m_process__serialize_global_space (orchestrator)
                |
                +-> m_process__save_chunk (tile data)
                +-> m_process__save_collision_node (spatial index)
                +-> m_process__save_local_space_node (viewport node)

    For each Region needing save:
        m_process__serialize_region (bitmap data)

## 1.5 Integration Points

| System | Integration |
|--------|-------------|
| `Global_Space` | Dispatches serialization/deserialization processes. Holds `p_generation_process`. |
| `Chunk` | Declares its own serialize/deserialize process handlers. |
| `Region` | Declares its own serialize/deserialize process handlers. |
| `PLATFORM_File_System_Context` | Provides filesystem operations for all process handlers. |
| `Serialization_Request` | Used by process handlers to perform platform filesystem I/O. |
