# Specification: core/include/world/local_space_manager.h

## Overview

Manages a fixed-size grid of `Local_Space` instances that forms the
scrollable viewport of the world. Handles initialization, centering,
directional scrolling, spatial lookup, and tile access by position.

## Dependencies

- `defines.h` (for `Local_Space_Manager`, `Local_Space`, `Global_Space_Manager`, `Chunk_Vector__3i32`)
- `defines_weak.h` (forward declarations)
- `vectors.h` (for `Vector__3i32F4`, `VECTOR__3i32__OUT_OF_BOUNDS`)
- `world/chunk_vectors.h` (for `vector_3i32F4_to__chunk_vector_3i32`)

## Types

### Local_Space_Manager (struct)

    typedef struct Local_Space_Manager_t {
        Local_Space local_spaces[VOLUME_OF__LOCAL_SPACE_MANAGER];
        Vector__3i32 center_of__local_space_manager__3i32;
        Local_Space *p_local_space__north_west;
        Local_Space *p_local_space__north_east;
        Local_Space *p_local_space__south_west;
        Local_Space *p_local_space__south_east;
        Local_Space *p_local_space__north_west__top;
        Local_Space *p_local_space__north_east__top;
        Local_Space *p_local_space__south_west__top;
        Local_Space *p_local_space__south_east__top;
    } Local_Space_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `local_spaces` | `Local_Space[VOLUME_OF__LOCAL_SPACE_MANAGER]` | Flat array of local space nodes. |
| `center_of__local_space_manager__3i32` | `Vector__3i32` | Current center chunk coordinate. |
| `p_local_space__north_west` etc. | `Local_Space*` | Corner pointers for the bottom layer. |
| `p_local_space__north_west__top` etc. | `Local_Space*` | Corner pointers for the top layer. |

### Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `LOCAL_SPACE_MANAGER__WIDTH` | `8` | Grid width in chunks. |
| `LOCAL_SPACE_MANAGER__HEIGHT` | `8` | Grid height in chunks. |
| `LOCAL_SPACE_MANAGER__DEPTH` | `1` | Grid depth in chunk layers. |
| `VOLUME_OF__LOCAL_SPACE_MANAGER` | `64` | Total local spaces. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_local_space_manager` | `(Local_Space_Manager*, Global_Space_Vector__3i32) -> void` | Initializes the grid centered at the given position. |

### Centering and Scrolling

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_center_of__local_space_manager` | `(Local_Space_Manager*, Game*, Chunk_Vector__3i32) -> void` | Sets the center, re-linking all local spaces. |
| `move_local_space_manager` | `(Local_Space_Manager*, Game*, Direction__u8) -> void` | Scrolls the grid one chunk in the given direction. |
| `poll_local_space_for__scrolling` | `(Local_Space_Manager*, Game*, Global_Space_Manager*, Global_Space_Vector__3i32) -> void` | Checks if scrolling is needed and performs it. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_local_space_from__local_space_manager` | `(Local_Space_Manager*, Chunk_Vector__3i32) -> Local_Space*` | `Local_Space*` | Finds a local space by chunk vector. |
| `get_p_local_space_by__3i32F4_from__local_space_manager` | `(Local_Space_Manager*, Vector__3i32F4) -> Local_Space*` | `Local_Space*` | Finds a local space by pixel position. (static inline) |
| `get_p_local_space_by__index_from__local_space_manager` | `(Local_Space_Manager*, Index__u32) -> Local_Space*` | `Local_Space*` | Direct index access. Debug bounds-checked. (static inline) |
| `get_p_tile_by__3i32F4_from__local_space_manager` | `(Local_Space_Manager*, Vector__3i32F4) -> Tile*` | `Tile*` | Finds a tile by pixel position. |

### State Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_local_space_manager__loaded_except_with__this_many_spaces` | `(Game*, Local_Space_Manager*, Quantity__u32) -> bool` | `bool` | True if all spaces are loaded except up to the given count. |
| `is_local_space_manager__loaded` | `(Game*, Local_Space_Manager*) -> bool` | `bool` | True if fully loaded (with tolerance for edge spaces). (static inline) |
| `is_vector_3i32F4_within__local_space_manager` | `(Local_Space_Manager*, Vector__3i32F4) -> bool` | `bool` | True if the position is within the managed area. |

### Convenience (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_local_space_manager_at__global_space_vector__3i32` | `(Local_Space_Manager*, Game*, Global_Space_Vector__3i32) -> void` | Forces a full reload at the given position by setting center to out-of-bounds first. |
| `get_center_of__local_space_manager` | `(Local_Space_Manager*) -> Chunk_Vector__3i32` | Returns the current center. |

## Agentic Workflow

### Scrolling Model

The local space manager implements a toroidal (wrap-around) grid. When
scrolling, edge spaces are recycled to the opposite side and re-linked
with new global spaces. This avoids copying the entire grid.

### Loading Check

`is_local_space_manager__loaded` uses a tolerance value that accounts for
edge/corner spaces that may still be loading. The tolerance formula is:
`((W-1)*(D-1)*2) + ((H-1)*(D-1)*2) + ((W-1)*(H-1)*2) + 2`.

### Preconditions

- `get_p_local_space_by__index_from__local_space_manager`: debug builds abort if index exceeds `VOLUME_OF__LOCAL_SPACE_MANAGER`.

## Header Guard

`LOCAL_SPACE_MANAGER_H`
