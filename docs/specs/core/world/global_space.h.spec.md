# Specification: core/include/world/global_space.h

## Overview

Defines operations on `Global_Space` — the engine's representation of a
single chunk-sized region of the world that tracks its chunk data, collision
node, generation process, reference count, and lifecycle state. Global spaces
use reference counting and a multi-phase construction/deconstruction state
machine.

## Dependencies

- `defines.h` (for `Global_Space`, `Chunk`, `Collision_Node`, `Process`, `Identifier__u64`)
- `defines_weak.h` (forward declarations)
- `serialization/serialization_header.h` (for `is_serialized_struct__deallocated__uuid_64`)

## Types

### Global_Space (struct)

    typedef struct Global_Space_t {
        Serialization_Header__UUID_64 _serialization_header;
        Chunk_Vector__3i32 chunk_vector__3i32;
        Chunk *p_chunk;
        Collision_Node *p_collision_node;
        Process *p_generation_process;
        Quantity__u16 quantity_of__references;
        Global_Space_Flags__u8 global_space_flags__u8;
    } Global_Space;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header__UUID_64` | 64-bit UUID derived from position. |
| `chunk_vector__3i32` | `Chunk_Vector__3i32` | The chunk coordinate this space represents. |
| `p_chunk` | `Chunk*` | Pointer to the chunk data. |
| `p_collision_node` | `Collision_Node*` | Pointer to the collision node for this space. |
| `p_generation_process` | `Process*` | Active generation/serialization process, if any. |
| `quantity_of__references` | `Quantity__u16` | Reference count. 0=deallocated, 1=awaiting, 2+=active. |
| `global_space_flags__u8` | `Global_Space_Flags__u8` | Lifecycle state flags. |

### Global_Space_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `GLOBAL_SPACE_FLAG__IS_CONSTRUCTING` | 0 | Currently being constructed (generating/deserializing). |
| `GLOBAL_SPACE_FLAG__IS_DECONSTRUCTING` | 1 | Currently being deconstructed (serializing). |
| `GLOBAL_SPACE_FLAG__IS_AWAITING__CONSTRUCTION` | 2 | Queued for construction. |
| `GLOBAL_SPACE_FLAG__IS_AWAITING__DECONSTRUCTION` | 3 | Queued for deconstruction. |
| `GLOBAL_SPACE_FLAG__IS_DIRTY` | 4 | Data has been modified. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_global_space` | `(Global_Space*) -> void` | Initializes to deallocated empty state. |
| `initialize_global_space_as__allocated` | `(Global_Space*, Identifier__u64) -> void` | Initializes as allocated with the given UUID. |

### Serialization Process Dispatchers

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `m_process__serialize_global_space` | `(Process*, Game*) -> void` | `void` | Process handler for serialization. |
| `dispatch_process__deserialize_global_space` | `(Game*, Global_Space*) -> Process*` | `Process*` | Dispatches a deserialization process. |
| `dispatch_process__serialize_global_space` | `(Game*, Global_Space*) -> Process*` | `Process*` | Dispatches a serialization process. |

### Reference Counting (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `hold_global_space` | `(Global_Space*) -> void` | `void` | Increments reference count. |
| `drop_global_space` | `(Global_Space*) -> bool` | `bool` | Decrements reference count. Returns true if all references dropped (count reaches 1). Clamps to minimum of 1. |

### Allocation Query (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_global_space__allocated` | `(Global_Space*) -> bool` | `bool` | True if non-null, not deallocated, and has references. |

### Lifecycle State Queries (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `is_global_space__awaiting_construction` | `bool` | True if queued for construction. |
| `is_global_space__awaiting_deconstruction` | `bool` | True if queued for deconstruction. |
| `is_global_space__constructing` | `bool` | True if actively constructing. |
| `is_global_space__deconstructing` | `bool` | True if actively deconstructing. |
| `is_global_space__dirty` | `bool` | True if data modified. Null-safe. |
| `is_global_space__active` | `bool` | True if allocated and NOT in any construction/deconstruction state. |

### Lifecycle State Mutations (static inline)

| Function | Description |
|----------|-------------|
| `set_global_space_as__awaiting_construction` | Sets awaiting construction flag. |
| `set_global_space_as__NOT_awaiting_construction` | Clears awaiting construction flag. |
| `set_global_space_as__awaiting_deconstruction` | Sets awaiting deconstruction flag. |
| `set_global_space_as__NOT_awaiting_deconstruction` | Clears awaiting deconstruction flag. |
| `set_global_space_as__constructing` | Sets constructing, clears awaiting construction. |
| `set_global_space_as__NOT_constructing` | Clears constructing and awaiting construction. |
| `set_global_space_as__deconstructing` | Sets deconstructing, clears awaiting deconstruction. |
| `set_global_space_as__NOT_deconstructing` | Clears deconstructing and awaiting deconstruction. |
| `set_global_space_as__dirty` | Sets dirty flag. |
| `set_global_space_as__NOT_dirty` | Clears dirty flag. |

### Sub-Component Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_chunk_from__global_space` | `(Global_Space*) -> Chunk*` | `Chunk*` | Returns chunk pointer. Null-safe. |
| `set_chunk_for__global_space` | `(Global_Space*, Chunk*) -> void` | `void` | Sets the chunk pointer. |
| `get_p_collision_node_from__global_space` | `(Global_Space*) -> Collision_Node*` | `Collision_Node*` | Returns collision node pointer. |
| `set_collision_node_for__global_space` | `(Global_Space*, Collision_Node*) -> void` | `void` | Sets the collision node pointer. |

## Agentic Workflow

### Lifecycle State Machine

    [deallocated] → initialize_global_space_as__allocated → [allocated, awaiting_construction]
        → set_global_space_as__constructing → [constructing]
        → set_global_space_as__NOT_constructing → [active]
        → set_global_space_as__awaiting_deconstruction → [awaiting_deconstruction]
        → set_global_space_as__deconstructing → [deconstructing]
        → set_global_space_as__NOT_deconstructing → [deallocated]

### Reference Count Convention

| Count | Meaning |
|-------|---------|
| `0` | Deallocated. |
| `1` | Awaiting usage or deallocation. |
| `2+` | Actively referenced. |

### Preconditions

- All functions require non-null `p_global_space` unless noted as null-safe.
- `is_global_space__allocated` and `is_global_space__dirty` are null-safe.

## Header Guard

`GLOBAL_SPACE_H`
