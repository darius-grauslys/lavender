# 1 Specification: core/include/world/global_space_manager.h

## 1.1 Overview

Manages a pool of `Global_Space` instances. Provides allocation, deallocation,
lookup by chunk vector, tile access, and reference-counted hold/drop
operations. Also provides the UUID generation function for global spaces
based on chunk coordinates.

## 1.2 Dependencies

- `defines.h` (for `Global_Space_Manager`, `Global_Space`, `Chunk_Vector__3i32`, `Tile_Vector__3i32`)
- `defines_weak.h` (forward declarations)
- `numerics.h` (for `ARITHMETRIC_L_SHIFT__u64`)

## 1.3 Types

### 1.3.1 Global_Space_Manager (struct)

    typedef struct Global_Space_Manager_t {
        Global_Space global_spaces[QUANTITY_OF__GLOBAL_SPACE];
        f_Global_Space__Dispose_Handler f_global_space__dispose_handler;
    } Global_Space_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `global_spaces` | `Global_Space[QUANTITY_OF__GLOBAL_SPACE]` | Fixed pool of global space instances. |
| `f_global_space__dispose_handler` | `f_Global_Space__Dispose_Handler` | Callback invoked when a global space is released. |

### 1.3.2 f_Global_Space__Dispose_Handler (function pointer)

    typedef void (*f_Global_Space__Dispose_Handler)(
            Game *p_game,
            Global_Space *p_global_space);

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_global_space_manager` | `(Global_Space_Manager*) -> void` | Initializes all global spaces as deallocated. |

### 1.4.2 Allocation and Release

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_global_space_in__global_space_manager` | `(Global_Space_Manager*, Chunk_Vector__3i32) -> Global_Space*` | `Global_Space*` | Allocates a global space for the given chunk position. Returns null if pool exhausted. |
| `release_global_space` | `(World*, Global_Space*) -> void` | `void` | Releases a global space and its associated chunk/collision node via the World. |
| `release_global_space_in__global_space_manager` | `(Global_Space_Manager*, Global_Space*) -> void` | `void` | Releases a global space within the manager only. |

### 1.4.3 Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_global_space_from__global_space_manager` | `(Global_Space_Manager*, Chunk_Vector__3i32) -> Global_Space*` | `Global_Space*` | Finds a global space by chunk vector. Returns null if not found. |
| `get_p_tile_from__global_space_manager` | `(Global_Space_Manager*, Tile_Vector__3i32) -> Tile*` | `Tile*` | Finds a tile by global tile vector. Returns null if not found. |

### 1.4.4 Reference Counting

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `hold_global_space_within__global_space_manager` | `(Game*, Chunk_Vector__3i32) -> Global_Space*` | `Global_Space*` | Finds or allocates a global space and increments its reference count. |
| `drop_global_space_within__global_space_manager` | `(Game*, Chunk_Vector__3i32) -> void` | `void` | Decrements the reference count. Releases if count drops to threshold. |

### 1.4.5 UUID Generation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_uuid_for__global_space` | `(Chunk_Vector__3i32) -> Identifier__u64` | `Identifier__u64` | Generates a deterministic 64-bit UUID from chunk coordinates by interleaving X/Y/Z bits. |

## 1.5 Agentic Workflow

### 1.5.1 UUID Bit Interleaving

The UUID is constructed by interleaving the bits of X, Y, and Z chunk
coordinates using alternating bit masks. This produces a spatially-coherent
hash suitable for lookup.

### 1.5.2 Ownership

Owned by `World` (at `world.global_space_manager`). Accessed via
`get_p_global_space_manager_from__world`.

### 1.5.3 Preconditions

- `allocate_global_space_in__global_space_manager`: the chunk vector should not already have an allocated global space.
- `release_global_space`: the global space must belong to this manager.

## 1.6 Header Guard

`GLOBAL_SPACE_MANAGER_H`
