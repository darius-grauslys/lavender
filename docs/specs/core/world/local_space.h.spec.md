# 1 Specification: core/include/world/local_space.h

## 1.1 Overview

Defines operations on `Local_Space` — a node in the local space grid that
wraps a `Global_Space` pointer and maintains 6-directional neighbor links
(north, east, south, west, above, below). Local spaces form the scrollable
viewport grid managed by `Local_Space_Manager`.

## 1.2 Dependencies

- `defines.h` (for `Local_Space`, `Global_Space`, `Chunk`, `Collision_Node`)
- `defines_weak.h` (forward declarations)
- `world/global_space.h` (for `Global_Space` accessors and state queries)

## 1.3 Types

### 1.3.1 Local_Space (struct)

    typedef struct Local_Space_t {
        Global_Space_Vector__3i32 global_space__vector__3i32;
        Global_Space *p_global_space;
        struct Local_Space_t *p_local_space__north;
        struct Local_Space_t *p_local_space__east;
        struct Local_Space_t *p_local_space__south;
        struct Local_Space_t *p_local_space__west;
        struct Local_Space_t *p_local_space__above;
        struct Local_Space_t *p_local_space__below;
    } Local_Space;

| Field | Type | Description |
|-------|------|-------------|
| `global_space__vector__3i32` | `Global_Space_Vector__3i32` | The chunk coordinate this local space represents. |
| `p_global_space` | `Global_Space*` | Pointer to the associated global space. |
| `p_local_space__north` through `__below` | `Local_Space*` | 6-directional neighbor pointers. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_local_space` | `(Local_Space*) -> void` | Initializes to empty state with null neighbors and global space. |

### 1.4.2 Neighbor Setup (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_neighbors_of__local_space` | `(Local_Space*, Local_Space* north, east, south, west, above, below) -> void` | Sets all 6 neighbor pointers. |

### 1.4.3 Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_global_space_from__local_space` | `(Local_Space*) -> Global_Space*` | `Global_Space*` | Returns the global space pointer. Null-safe. |
| `get_p_collision_node_from__local_space` | `(Local_Space*) -> Collision_Node*` | `Collision_Node*` | Returns the collision node via the global space. Null-safe. |
| `get_p_chunk_from__local_space` | `(Local_Space*) -> Chunk*` | `Chunk*` | Returns the chunk via the global space. Null-safe. |

### 1.4.4 State Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_local_space__allocated` | `(Local_Space*) -> bool` | `bool` | True if local space is non-null, has a global space, and that global space is allocated. |
| `is_local_space__active` | `(Local_Space*) -> bool` | `bool` | True if allocated AND the global space is active (not constructing/deconstructing). |

## 1.5 Agentic Workflow

### 1.5.1 Null Safety

All accessor and query functions are null-safe — they return null/false if
`p_local_space` is null or if the underlying `p_global_space` is null.

### 1.5.2 Relationship to Local_Space_Manager

Local spaces are stored in a flat array within `Local_Space_Manager` and
linked via neighbor pointers. The manager handles scrolling by re-linking
neighbors and reassigning global spaces.

### 1.5.3 Preconditions

- `set_neighbors_of__local_space` requires a non-null `p_local_space`. Neighbor pointers may be null.

## 1.6 Header Guard

`LOCAL_SPACE_H`
