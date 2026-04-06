# 1 Specification: core/include/world/structures/structure_manager.h

## 1.1 Overview

Manages pools of `Room` and `Structure` instances. Provides allocation,
deallocation, and quantity queries for both types.

## 1.2 Dependencies

- `defines.h` (for `Structure_Manager`, `Room`, `Structure`)

## 1.3 Types

### 1.3.1 Structure_Manager (struct)

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

## 1.4 Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_structure_manager` | `(Structure_Manager*) -> void` | `void` | Initializes all pools as empty. |
| `allocate_room_in__structure_manager` | `(Structure_Manager*) -> Room*` | `Room*` | Allocates a room. Returns null if pool exhausted. |
| `allocate_structure_in__structure_manager` | `(Structure_Manager*) -> Structure*` | `Structure*` | Allocates a structure. Returns null if pool exhausted. |
| `release_room_in__structure_manager` | `(Structure_Manager*, Room*) -> void` | `void` | Returns a room to the pool. |
| `release_structure_in__structure_manager` | `(Structure_Manager*, Structure*) -> void` | `void` | Returns a structure to the pool. |
| `get_quantity_of__rooms_allocated_in__structure_manager` | `(Structure_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns allocated room count. (static inline) |
| `get_quantity_of__structures_allocated_in__structure_manager` | `(Structure_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns allocated structure count. (static inline) |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `World` (at `world.structure_manager`).

### 1.5.2 Preconditions

- `release_room_in__structure_manager`: room must belong to this manager.
- `release_structure_in__structure_manager`: structure must belong to this manager.

## 1.6 Header Guard

`STRUCTURE_MANAGER_H`
