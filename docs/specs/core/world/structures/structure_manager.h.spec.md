# Specification: core/include/world/structures/structure_manager.h

## Overview

Manages pools of `Room` and `Structure` instances. Provides allocation,
deallocation, and quantity queries for both types.

## Dependencies

- `defines.h` (for `Structure_Manager`, `Room`, `Structure`)

## Types

### Structure_Manager (struct)

    typedef struct Structure_Manager_t {
        Room rooms[ROOM_MAX_QUANTITY_OF];
        Structure structures[STRUCTURE_MAX_QUANTITY_OF];
        Room *ptr_array_of__allocated_rooms[ROOM_MAX_QUANTITY_OF];
        Structure *ptr_array_of__allocated_structures[STRUCTURE_MAX_QUANTITY_OF];
        Quantity__u32 quantity_of__allocated_rooms;
        Quantity__u32 quantity_of__allocated_structures;
    } Structure_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `rooms` | `Room[ROOM_MAX_QUANTITY_OF]` | Room pool. |
| `structures` | `Structure[STRUCTURE_MAX_QUANTITY_OF]` | Structure pool. |
| `ptr_array_of__allocated_rooms` | `Room*[]` | Pointer array of allocated rooms. |
| `ptr_array_of__allocated_structures` | `Structure*[]` | Pointer array of allocated structures. |
| `quantity_of__allocated_rooms` | `Quantity__u32` | Current allocated room count. |
| `quantity_of__allocated_structures` | `Quantity__u32` | Current allocated structure count. |

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_structure_manager` | `(Structure_Manager*) -> void` | `void` | Initializes all pools as empty. |
| `allocate_room_in__structure_manager` | `(Structure_Manager*) -> Room*` | `Room*` | Allocates a room. Returns null if pool exhausted. |
| `allocate_structure_in__structure_manager` | `(Structure_Manager*) -> Structure*` | `Structure*` | Allocates a structure. Returns null if pool exhausted. |
| `release_room_in__structure_manager` | `(Structure_Manager*, Room*) -> void` | `void` | Returns a room to the pool. |
| `release_structure_in__structure_manager` | `(Structure_Manager*, Structure*) -> void` | `void` | Returns a structure to the pool. |
| `get_quantity_of__rooms_allocated_in__structure_manager` | `(Structure_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns allocated room count. (static inline) |
| `get_quantity_of__structures_allocated_in__structure_manager` | `(Structure_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns allocated structure count. (static inline) |

## Agentic Workflow

### Ownership

Owned by `World` (at `world.structure_manager`).

### Preconditions

- `release_room_in__structure_manager`: room must belong to this manager.
- `release_structure_in__structure_manager`: structure must belong to this manager.

## Header Guard

`STRUCTURE_MANAGER_H`
