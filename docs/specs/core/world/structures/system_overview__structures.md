# 1 System Overview: Structures

## 1.1 Purpose

The structures subsystem provides pooled management of procedurally generated
spatial groupings within the world. It defines three levels of spatial
hierarchy — `Room`, `Structure`, and `Site` — each with bounding boxes,
allocation state, and type metadata. These types are used during world
generation to place multi-room buildings, dungeons, and other composed
spatial features.

## 1.2 Architecture

### 1.2.1 Data Hierarchy

    World
    +-- Structure_Manager
        +-- Room[0..ROOM_MAX_QUANTITY_OF-1]           (pool)
        |   +-- Serialization_Header
        |   +-- Hitbox_AABB bounding_box_of__room
        |   +-- Vector__3i32F4 entrances__3i32F4[0..3]
        |   +-- Room_Type__u16
        |   +-- Room_Flags__u8 (IS_ALLOCATED)
        |
        +-- Structure[0..STRUCTURE_MAX_QUANTITY_OF-1]  (pool)
        |   +-- Serialization_Header
        |   +-- Room *ptr_array_of__rooms[0..ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF-1]
        |   +-- Hitbox_AABB bounding_box_of__structure
        |   +-- Structure_Type__u16
        |   +-- Structure_Flags__u8 (IS_ALLOCATED)
        |
        +-- Room *ptr_array_of__allocated_rooms[]      (tracking)
        +-- Structure *ptr_array_of__allocated_structures[] (tracking)

    Site (managed separately, referenced by Region bitmaps)
        +-- Serialization_Header
        +-- Structure *ptr_array_of__structures_in__site[0..STRUCTURES_IN_SITE__MAX_QUANTITY_OF-1]
        +-- Hitbox_AABB bounding_box_of__site
        +-- Quantity__u8 quantity_of__structures_in__site

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Structure_Manager` | Top-level owner. Lives in `World`. Holds room and structure pools with pointer-array tracking. |
| `Room` | A bounded region with up to 4 entrance points. The atomic building block of structures. |
| `Structure` | A collection of up to 8 rooms with a bounding box and game-defined type. |
| `Site` | A large spatial grouping (512×512 tiles) containing multiple structures. Tracked by `Region` bitmaps. |
| `Structure_Tile` | Helper struct used during generation to describe wall/stair/window features at a tile position. |

### 1.2.3 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `ROOM_MAX_QUANTITY_OF` | `128` | Maximum rooms in the pool. |
| `ROOM_ENTRANCE_MAX_QUANTITY_OF` | `4` | Maximum entrances per room. |
| `ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF` | `8` | Maximum rooms per structure. |
| `STRUCTURE_MAX_QUANTITY_OF` | `ROOM_MAX_QUANTITY_OF / ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF` (16) | Maximum structures in the pool. |
| `STRUCTURES_IN_SITE__MAX_QUANTITY_OF` | `STRUCTURE_MAX_QUANTITY_OF / 4` | Maximum structures per site. |
| `SITE_MAX_QUANTITY_OF` | `STRUCTURE_MAX_QUANTITY_OF / STRUCTURES_IN_SITE__MAX_QUANTITY_OF` | Maximum sites. |
| `SITE__WIDTH_IN__TILES` | `512` | Site width in tiles. |
| `SITE__HEIGHT_IN__TILES` | `512` | Site height in tiles. |

## 1.3 Lifecycle

### 1.3.1 Initialization

    initialize_structure_manager(&world.structure_manager)
        -> All Room slots: deallocated, empty.
        -> All Structure slots: deallocated, empty.
        -> Pointer arrays: empty.
        -> Counts: zero.

### 1.3.2 Room Allocation

    Room *p_room = allocate_room_in__structure_manager(&structure_manager)
        -> Finds an unallocated Room in the pool.
        -> Sets ROOM_FLAG__IS_ALLOCATED.
        -> Adds to ptr_array_of__allocated_rooms.
        -> Increments quantity_of__allocated_rooms.
        -> Returns null if pool exhausted.

### 1.3.3 Room Configuration

    // Set room type
    set_the_type_of__room(p_room, room_type);

    // Add entrance points (up to 4)
    add_entrance_to__room(p_room, entrance_position__3i32F4);
        -> Silently fails if ROOM_ENTRANCE_MAX_QUANTITY_OF reached.

    // Query closest entrance
    Vector__3i32F4 entrance = get_closest_entrance_to__room(p_room, query_pos);
        -> Returns VECTOR__3i32F4__OUT_OF_BOUNDS on failure.

### 1.3.4 Structure Allocation and Assembly

    Structure *p_structure = allocate_structure_in__structure_manager(&structure_manager)
        -> Finds an unallocated Structure in the pool.
        -> Sets STRUCTURE_FLAG__IS_ALLOCATED.
        -> Returns null if pool exhausted.

    // Add rooms to structure (up to 8)
    add_p_room_to__structure(p_structure, p_room);

    // Set structure type
    set_the_kind_of__structure(p_structure, structure_type);

### 1.3.5 Site Assembly

    initialize_site(&site)
        -> Empty state, no structures.

    // Sites reference structures via pointer array.
    // Sites are tracked by Region bitmaps for serialization.

### 1.3.6 Deallocation

    release_room_in__structure_manager(&structure_manager, p_room)
        -> Clears ROOM_FLAG__IS_ALLOCATED.
        -> Removes from ptr_array_of__allocated_rooms.
        -> Decrements quantity_of__allocated_rooms.

    release_structure_in__structure_manager(&structure_manager, p_structure)
        -> Clears STRUCTURE_FLAG__IS_ALLOCATED.
        -> Removes from ptr_array_of__allocated_structures.
        -> Decrements quantity_of__allocated_structures.

## 1.4 Spatial Hierarchy

The structures subsystem defines three levels of spatial containment:

    Site (512×512 tiles)
    +-- Structure (variable size, bounded by Hitbox_AABB)
        +-- Room (variable size, bounded by Hitbox_AABB)
            +-- Entrance points (up to 4 per room)

### 1.4.1 Bounding Boxes

Both `Room` and `Structure` use `Hitbox_AABB` for their bounding boxes.
`Site` also uses `Hitbox_AABB`. These bounding boxes are used for:
- Spatial queries (e.g., `is_structure_within__region`)
- Overlap detection during generation
- Size queries (`get_width_of__room`, `get_height_of__room`)

### 1.4.2 Entrance System

Rooms have up to 4 entrance points stored as `Vector__3i32F4` positions.
The `get_closest_entrance_to__room` function enables pathfinding and
connectivity queries between rooms within a structure.

## 1.5 Integration with Region System

Sites are tracked by `Region` bitmaps (`bitmap_of__sites`). The
`is_structure_within__region` function checks whether a structure's
bounding box overlaps a given region, enabling region-scoped structure
queries during serialization and generation.

## 1.6 Structure_Tile Helper

The `Structure_Tile` struct is a lightweight helper used during procedural
generation to describe what features a tile position should have:

    Structure_Tile {
        bool has_walls;
        bool has_stairs;
        bool has_windows;
    }

This is not stored persistently — it is used transiently during the
generation process to determine which `Tile_Kind` to place.

## 1.7 Capacity Constraints

| Resource | Pool Size | Notes |
|----------|-----------|-------|
| Rooms | 128 | Shared across all structures. |
| Structures | 16 | Derived from room budget (128 / 8). |
| Sites | Derived | `STRUCTURE_MAX_QUANTITY_OF / STRUCTURES_IN_SITE__MAX_QUANTITY_OF`. |
| Entrances per room | 4 | Fixed maximum. |
| Rooms per structure | 8 | Fixed maximum. |
