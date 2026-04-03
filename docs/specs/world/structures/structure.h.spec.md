# Specification: core/include/world/structures/structure.h

## Overview

Defines operations on `Structure` — a collection of rooms with a bounding
box, type, and allocation state. Structures group related rooms together
for procedural generation and spatial queries.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Structure`, `Room`, `Structure_Ptr_Array_Of__Rooms`, `Hitbox_AABB`)

## Types

### Structure (struct)

    typedef struct Structure_t {
        Serialization_Header _serialization_header;
        Structure_Ptr_Array_Of__Rooms ptr_array_of__rooms;
        Hitbox_AABB bounding_box_of__structure;
        Structure_Type__u16 the_kind_of__structure;
        Quantity__u8 quantity_of__rooms_in__structure;
        Structure_Flags__u8 structure_flags;
    } Structure;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for serialization. |
| `ptr_array_of__rooms` | `Room*[ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF]` | Array of room pointers. |
| `bounding_box_of__structure` | `Hitbox_AABB` | Spatial bounds of the structure. |
| `the_kind_of__structure` | `Structure_Type__u16` | Game-defined structure type. |
| `quantity_of__rooms_in__structure` | `Quantity__u8` | Number of rooms. |
| `structure_flags` | `Structure_Flags__u8` | Allocation flags. |

### Structure_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `STRUCTURE_FLAG__IS_ALLOCATED` | 0 | Structure is allocated. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF` | `8` | Maximum rooms per structure. |
| `STRUCTURE_MAX_QUANTITY_OF` | `ROOM_MAX_QUANTITY_OF / ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF` | Maximum structures. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_structure` | `(Structure*) -> void` | Initializes to empty deallocated state. |

### Room Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `add_p_room_to__structure` | `(Structure*, Room*) -> void` | Adds a room to the structure. |
| `get_rooms_in__structure` | `(Structure*, Structure_Ptr_Array_Of__Rooms) -> void` | Fills the array with room pointers. Index after last room is null; subsequent indices are undefined. |

### Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__rooms_in__structure` | `(Structure*) -> Quantity__u32` | `Quantity__u32` | Returns room count. |
| `get_the_kind_of__structure` | `(Structure*) -> Structure_Type__u16` | `Structure_Type__u16` | Returns structure type. |
| `set_the_kind_of__structure` | `(Structure*, Structure_Type__u16) -> void` | `void` | Sets structure type. |

### Allocation State (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_structure__allocated` | `(Structure*) -> bool` | `bool` | True if allocated flag set. |
| `set_structure_as__allocated` | `(Structure*) -> void` | `void` | Sets allocated flag. |
| `set_structure_as__deallocated` | `(Structure*) -> void` | `void` | Clears allocated flag. |

## Agentic Workflow

### Ownership

Managed by `Structure_Manager` (see `structure_manager.h`).

### Preconditions

- All functions require non-null `p_structure`.

## Header Guard

`STRUCTURE_H`
