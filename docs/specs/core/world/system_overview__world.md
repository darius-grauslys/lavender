# 1 System Overview: World

## 1.1 Purpose

The world system is the top-level container for all spatial, entity, and
environmental state in the engine. It manages the lifecycle of chunks,
global spaces, local spaces, tiles, regions, structures, collision nodes,
cameras, and tile logic. The `World` struct aggregates all of these
sub-systems and provides the primary interface for world initialization,
per-frame management, entity placement, scrolling, and save/load.

## 1.2 Architecture

### 1.2.1 Data Hierarchy

    Game
    +-- World (heap-allocated, owned via pM_world)
        +-- Region_Manager
        |   +-- Region[0..REGION_MAX_QUANTITY_OF-1]
        |       +-- bitmap_of__serialized_chunks[]
        |       +-- bitmap_of__sites[]
        |
        +-- Global_Space_Manager
        |   +-- Global_Space[0..QUANTITY_OF__GLOBAL_SPACE-1]
        |       +-- Chunk *p_chunk  ---------> Chunk_Pool.chunks[i]
        |       +-- Collision_Node *p_collision_node --> Collision_Node_Pool
        |       +-- Process *p_generation_process
        |       +-- quantity_of__references (ref count)
        |       +-- Global_Space_Flags__u8 (lifecycle state)
        |
        +-- Local_Space_Manager (viewport grid)
        |   +-- Local_Space[0..VOLUME_OF__LOCAL_SPACE_MANAGER-1]
        |       +-- Global_Space *p_global_space --> Global_Space_Manager
        |       +-- 6 neighbor pointers (north/east/south/west/above/below)
        |
        +-- Chunk_Pool
        |   +-- Chunk[0..QUANTITY_OF__GLOBAL_SPACE-1]
        |       +-- Tile[0..CHUNK__QUANTITY_OF__TILES-1]
        |       +-- Chunk_Flags
        |
        +-- Collision_Node_Pool  (see collision system overview)
        |
        +-- Structure_Manager
        |   +-- Room[0..ROOM_MAX_QUANTITY_OF-1]
        |   +-- Structure[0..STRUCTURE_MAX_QUANTITY_OF-1]
        |       +-- Room *ptr_array_of__rooms[0..ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF-1]
        |
        +-- Tile_Logic_Table
        |   +-- Tile_Logic_Record[] (indexed by Tile_Kind)
        |
        +-- Chunk_Generator_Table
        |   +-- m_Process[] (indexed by Chunk_Generator_Kind)
        |
        +-- Camera
        |   +-- position, fulcrum, z_near/z_far, follow target UUID
        |
        +-- Inventory_Manager
        +-- Item_Manager
        +-- Entity_Manager
        +-- Repeatable_Psuedo_Random
        +-- Graphics_Window *p_graphics_window_for__world

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `World` | Top-level container. Owned by `Game`. Holds all world sub-systems. |
| `Region_Manager` | Manages a small pool of `Region` instances for serialization tracking. |
| `Region` | Large-scale spatial partition. Tracks which chunks/sites are serialized via bitmaps. |
| `Global_Space_Manager` | Pool of `Global_Space` instances. Handles allocation, lookup, and reference counting. |
| `Global_Space` | Represents a loaded chunk-sized region. Links to `Chunk`, `Collision_Node`, and generation `Process`. |
| `Local_Space_Manager` | Fixed-size toroidal grid of `Local_Space` nodes forming the scrollable viewport. |
| `Local_Space` | Node in the viewport grid. Wraps a `Global_Space` pointer with 6-directional neighbor links. |
| `Chunk_Pool` | Fixed pool of `Chunk` instances identified by 64-bit UUIDs. |
| `Chunk` | Fixed-size 3D grid of `Tile` instances. The atomic unit of world storage. |
| `Tile` | Atomic world-building unit. Identified by `Tile_Kind`. |
| `Tile_Logic_Table` | Maps `Tile_Kind` to `Tile_Logic_Record` for passability, sight blocking, height queries. |
| `Tile_Logic_Record` | Per-tile-kind logic properties (flags + height). |
| `Chunk_Generator_Table` | Maps `Chunk_Generator_Kind` to `m_Process` handlers for procedural generation. |
| `Structure_Manager` | Manages pools of `Room` and `Structure` instances for procedural structures. |
| `Camera` | Viewport controller with position, fulcrum dimensions, and optional entity follow target. |

### 1.2.3 Coordinate Spaces

The world system uses three primary coordinate spaces:

| Space | Type | Unit | Description |
|-------|------|------|-------------|
| Pixel | `Vector__3i32`, `Vector__3i32F4`, `Vector__3i32F20` | 1 pixel | Absolute world positions. |
| Tile | `Tile_Vector__3i32`, `Local_Tile_Vector__3u8` | 8 pixels | Tile indices. Local variant is chunk-relative (0-7). |
| Chunk | `Chunk_Vector__3i32` | 64 pixels (8 tiles) | Chunk indices. Used for global space lookup. |

Conversion functions are provided by `tile_vectors.h` and `chunk_vectors.h`.
All handle negative coordinates correctly via arithmetic shift/mask operations.

### 1.2.4 Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `8` | Pixels per tile edge. |
| `CHUNK__WIDTH` / `CHUNK__HEIGHT` | `8` | Tiles per chunk edge. |
| `CHUNK__DEPTH` | `2` | Tile layers per chunk. |
| `CHUNK__QUANTITY_OF__TILES` | `128` | Total tiles per chunk. |
| `LOCAL_SPACE_MANAGER__WIDTH` / `__HEIGHT` | `8` | Viewport grid dimensions in chunks. |
| `VOLUME_OF__LOCAL_SPACE_MANAGER` | `64` | Total local spaces in viewport. |
| `REGION_MAX_QUANTITY_OF` | `4` | Maximum concurrent regions. |
| `CAMERA_FULCRUM__WIDTH` | `256` | Default viewport width in pixels. |
| `CAMERA_FULCRUM__HEIGHT` | `196` | Default viewport height in pixels. |

## 1.3 Lifecycle

### 1.3.1 World Initialization

    initialize_world(p_game, p_world)
        -> Initializes all sub-components:
           - Region_Manager
           - Entity_Manager
           - Global_Space_Manager
           - Collision_Node_Pool
           - Chunk_Pool
           - Structure_Manager
           - Tile_Logic_Table
           - Chunk_Generator_Table
           - Inventory_Manager
           - Item_Manager
           - Camera (as inactive)

### 1.3.2 World Loading

    load_world(p_game) -> Process*
        -> Only called from main menu.
        -> Returns a cooperative Process that:
           1. Deserializes the world header (seed, player data).
           2. Sets the region manager center.
           3. Loads the local space manager at the spawn point.
        -> World is not usable until the process completes.

### 1.3.3 Per-Frame Management

    manage_world(p_game)
        -> Polls local space manager for scrolling.
        -> Manages chunk generation/serialization processes.
        -> Updates region manager as needed.

    manage_world__entities(p_game)
        -> Updates all active entities.
        -> Drives collision resolution (via Collision_Node_Pool).

### 1.3.4 Scrolling

    poll_world_for__scrolling(p_game, p_world, p_graphics_window) -> bool
        -> Checks camera position against local space manager center.
        -> If camera has moved to a new chunk:
           1. Local_Space_Manager scrolls (toroidal wrap).
           2. Edge local spaces are recycled and re-linked.
           3. New global spaces are allocated/held for incoming chunks.
           4. Old global spaces are dropped (ref count decremented).
           5. Chunk generation/deserialization processes are dispatched.

### 1.3.5 Entity Placement

    allocate_entity_into__world(p_game, entity_kind, position) -> Entity*
        -> Allocates an entity in the Entity_Manager.
        -> Initializes at the given position.
        -> Adds a collision node entry for the entity's chunk.

### 1.3.6 Collision Node Migration

    poll_for_collision_node_update(p_game, old_pos, new_pos, uuid) -> bool
        -> Called when an entity moves.
        -> If the entity crossed a chunk boundary:
           1. Removes entry from old chunk's Collision_Node.
           2. Adds entry to new chunk's Collision_Node.

### 1.3.7 World Saving

    save_world(p_file_system_context, p_world)
        -> Only called when leaving the world (returning to main menu).
        -> Serializes world header.
        -> Serializes all dirty chunks via cooperative processes.

## 1.4 Global Space Lifecycle

Global spaces are the central coordination point between chunks, collision
nodes, and the viewport grid. They follow a reference-counted lifecycle
with a multi-phase state machine:

    [deallocated] (ref_count=0)
        -> allocate / hold (ref_count incremented)
    [awaiting_construction] (ref_count>=1)
        -> dispatch deserialization or generation process
    [constructing] (process running)
        -> process completes
    [active] (ref_count>=2, no construction/deconstruction flags)
        -> entity/tile modifications set dirty flag
        -> drop (ref_count decremented)
    [awaiting_deconstruction] (ref_count dropped to threshold)
        -> dispatch serialization process (if dirty)
    [deconstructing] (process running)
        -> process completes
    [deallocated] (ref_count=0, chunk/collision_node released)

### 1.4.1 Reference Count Convention

| Count | Meaning |
|-------|---------|
| `0` | Deallocated. |
| `1` | Awaiting usage or pending deallocation. |
| `2+` | Actively referenced by one or more local spaces. |

## 1.5 Viewport Scrolling Model

The `Local_Space_Manager` implements a toroidal (wrap-around) grid of
`Local_Space` nodes. Each node wraps a `Global_Space` pointer and maintains
6-directional neighbor links.

    +----+----+----+----+----+----+----+----+
    | LS | LS | LS | LS | LS | LS | LS | LS |  <- row 0
    +----+----+----+----+----+----+----+----+
    | LS | LS | LS | LS | LS | LS | LS | LS |  <- row 1
    +----+----+----+----+----+----+----+----+
    |              ...  (8x8 grid)           |
    +----+----+----+----+----+----+----+----+
    | LS | LS | LS | LS | LS | LS | LS | LS |  <- row 7
    +----+----+----+----+----+----+----+----+

When the camera moves one chunk in a direction:
1. The edge row/column on the trailing side is recycled.
2. Those local spaces are re-assigned to new global spaces on the leading side.
3. Neighbor pointers are re-linked to maintain the toroidal topology.
4. New global spaces are held (ref count incremented); old ones are dropped.

This avoids copying the entire grid on each scroll step.

## 1.6 Tile Logic System

Tile logic properties are decoupled from the `Tile` struct itself. Instead,
a `Tile_Logic_Table` maps each `Tile_Kind` to a `Tile_Logic_Record`:

    Tile -> Tile_Kind -> Tile_Logic_Table -> Tile_Logic_Record
                                              +-- flags (unpassable, sight blocking, no ground)
                                              +-- height (i32F4)

This design allows the same tile data to have different logic properties
depending on game configuration, and keeps the `Tile` struct minimal for
serialization efficiency.

### 1.6.1 Registration

The `Tile_Logic_Table` is populated at initialization by the game-implemented
`register_tile_logic_tables` function (see `implemented/` subfolder).

## 1.7 Chunk Generation System

Chunk generation is driven by the `Chunk_Generator_Table`, which maps
`Chunk_Generator_Kind` values to cooperative `m_Process` handlers:

    Chunk_Generator_Kind -> Chunk_Generator_Table -> m_Process handler
                                                      |
                                                      v
                                                  Global_Space (p_process_data)
                                                      |
                                                      v
                                                  Chunk (tiles populated)

### 1.7.1 Registration

The `Chunk_Generator_Table` is populated at initialization by the
game-implemented `register_chunk_generators` function (see `implemented/`
subfolder).

## 1.8 Serialization Architecture

World data is persisted through a hierarchical directory structure managed
by the serialization subsystem:

    <base_directory>/<world_name>/
        h                           <- world header (seed, player data)
        <chunk_dir>/
            t                       <- chunk tile data

### 1.8.1 Serialization Units

| Unit | Scope | Process Handler |
|------|-------|-----------------|
| World header | Seed, spawn, player data | `load_world` / `save_world` |
| Region | Chunk/site bitmaps | `m_process__serialize_region` / `m_process__deserialize_region` |
| Chunk | Tile data | `m_process__serialize_chunk` / `m_process__deserialize_chunk` |
| Collision Node | Spatial index data | `m_process__save_collision_node` |
| Local Space Node | Viewport node data | `m_process__save_local_space_node` |

All serialization processes follow the cooperative process model — they
yield after each poll cycle and must not block.

## 1.9 Integration with Collision System

The world system integrates with the collision system (see
`system_overview__collision_node.md`) through:

1. **Global_Space → Collision_Node**: Each `Global_Space` holds a pointer
   to its associated `Collision_Node` in the `Collision_Node_Pool`.
2. **Collision node allocation**: When a global space is allocated, a
   collision node is allocated from the pool and linked.
3. **Collision node release**: When a global space is released, its
   collision node is released back to the pool.
4. **Entity migration**: `poll_for_collision_node_update` handles moving
   collision node entries when entities cross chunk boundaries.

## 1.10 Integration with Graphics System

The world connects to the graphics system through:

1. **Camera**: Drives viewport positioning. Can follow an entity by UUID
   via `m_camera_handler__follow__default`.
2. **Graphics_Window**: The world holds a pointer to its rendering window
   (`p_graphics_window_for__world`). The camera can be attached to a
   `Graphics_Window` via `set_p_camera_of__graphics_window`.
3. **Tile Render Kernel**: `f_tile_render_kernel` is a function pointer
   set by the game to control how tiles are rendered.

## 1.11 Capacity Constraints

| Resource | Pool Size | Determined By |
|----------|-----------|---------------|
| Global Spaces | `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS` |
| Chunks | `QUANTITY_OF__GLOBAL_SPACE` | Matches global space pool (1:1). |
| Local Spaces | `VOLUME_OF__LOCAL_SPACE_MANAGER` (64) | Fixed viewport grid size. |
| Regions | `REGION_MAX_QUANTITY_OF` (4) | Small active set around player. |
| Rooms | `ROOM_MAX_QUANTITY_OF` (128) | Structure system budget. |
| Structures | `STRUCTURE_MAX_QUANTITY_OF` (16) | Derived from room budget. |

## 1.12 Relationship to Other Systems

| Concern | Managed By |
|---------|------------|
| World state and lifecycle | `World` |
| Chunk storage and tile access | `Chunk_Pool`, `Chunk` |
| Loaded chunk tracking and ref counting | `Global_Space_Manager`, `Global_Space` |
| Viewport grid and scrolling | `Local_Space_Manager`, `Local_Space` |
| Spatial collision indexing | `Collision_Node_Pool` (see collision system) |
| Tile physics properties | `Tile_Logic_Table` |
| Procedural chunk generation | `Chunk_Generator_Table` |
| Procedural structure generation | `Structure_Manager`, `Structure`, `Room` |
| Serialization region tracking | `Region_Manager`, `Region` |
| Viewport control and entity tracking | `Camera` |
| Filesystem path construction | `world_directory.h` (serialization subfolder) |
