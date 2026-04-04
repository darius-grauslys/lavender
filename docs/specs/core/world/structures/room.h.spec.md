# Specification: core/include/world/structures/room.h

## Overview

Defines operations on `Room` — a bounded region within a structure that has
a bounding box, entrance points, a type, and allocation state. Rooms are
the building blocks of structures.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Room`, `Hitbox_AABB`, `Room_Type__u16`, `Room_Flags__u8`)
- `vectors.h` (for `Vector__3i32F4`, `VECTOR__3i32F4__OUT_OF_BOUNDS`)

## Types

### Room (struct)

    typedef struct Room_t {
        Serialization_Header _serialization_header;
        Hitbox_AABB bounding_box_of__room;
        Vector__3i32F4 entrances__3i32F4[ROOM_ENTRANCE_MAX_QUANTITY_OF];
        Room_Type__u16 the_type_of__room;
        Quantity__u8 quantity_of__room_entrances;
        Room_Flags__u8 room_flags;
    } Room;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for serialization. |
| `bounding_box_of__room` | `Hitbox_AABB` | Spatial bounds of the room. |
| `entrances__3i32F4` | `Vector__3i32F4[4]` | Up to 4 entrance positions. |
| `the_type_of__room` | `Room_Type__u16` | Game-defined room type. |
| `quantity_of__room_entrances` | `Quantity__u8` | Number of active entrances. |
| `room_flags` | `Room_Flags__u8` | Allocation flags. |

### Room_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `ROOM_FLAG__IS_ALLOCATED` | 0 | Room is allocated. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `ROOM_ENTRANCE_MAX_QUANTITY_OF` | `4` | Maximum entrances per room. |
| `ROOM_MAX_QUANTITY_OF` | `128` | Maximum rooms in the structure manager. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_room` | `(Room*) -> void` | Initializes to empty deallocated state. |

### Entrance Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_entrance_to__room` | `(Room*, Vector__3i32F4) -> void` | `void` | Adds an entrance position. |
| `get_closest_entrance_to__room` | `(Room*, Vector__3i32F4) -> Vector__3i32F4` | `Vector__3i32F4` | Returns the closest entrance. Returns `VECTOR__3i32F4__OUT_OF_BOUNDS` on failure. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__entrances_in__room` | `(Room*) -> Quantity__u32` | `Quantity__u32` | Returns entrance count. |
| `get_width_of__room` | `(Room*) -> Quantity__u32` | `Quantity__u32` | Returns bounding box width. |
| `get_height_of__room` | `(Room*) -> Quantity__u32` | `Quantity__u32` | Returns bounding box height. |
| `get_the_type_of__room` | `(Room*) -> Room_Type__u16` | `Room_Type__u16` | Returns room type. |
| `set_the_type_of__room` | `(Room*, Room_Type__u16) -> Room_Type__u16` | `Room_Type__u16` | Sets room type. **Note:** returns the type (likely unintentional). |

### Allocation State (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_room__allocated` | `(Room*) -> bool` | `bool` | True if allocated flag set. |
| `set_room_as__allocated` | `(Room*) -> void` | `void` | Sets allocated flag. |
| `set_room_as__deallocated` | `(Room*) -> void` | `void` | Clears allocated flag. |

## Agentic Workflow

### Ownership

Managed by `Structure_Manager` (see `structure_manager.h`).

### Preconditions

- All functions require non-null `p_room`.
- `add_entrance_to__room`: silently fails if `ROOM_ENTRANCE_MAX_QUANTITY_OF` reached.

## Header Guard

`ROOM_H`
