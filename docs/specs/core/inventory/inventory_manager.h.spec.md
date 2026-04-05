# Specification: core/include/inventory/inventory_manager.h

## Overview

Provides initialization, allocation, release, and lookup utilities for the
`Inventory_Manager` — a pool-based manager for `Inventory` instances. The
`Inventory_Manager` owns a fixed-size pool of inventories and supports
UUID-based allocation and retrieval, enabling both entity inventories and
spatially-indexed container inventories to be managed from a single pool.

The `Inventory_Manager` is owned by `World` and accessed from `Game` via
`get_p_inventory_manager_from__game` → `get_p_inventory_manager_from__world`.
This means inventories are tied to the currently loaded world — when the
world is deallocated, all inventories are invalidated.

## Dependencies

- `defines.h` (for `Inventory_Manager`, `Inventory`, `Identifier__u32`)
- `defines_weak.h` (forward declarations)
- `game.h` (for `Game` context access)
- `serialization/hashing.h` (for UUID-based pool allocation and lookup)

## Types

### Inventory_Manager (struct)

    typedef struct Inventory_Manager_t {
        Inventory inventories[MAX_QUANTITY_OF__INVENTORY];
    } Inventory_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `inventories` | `Inventory[MAX_QUANTITY_OF__INVENTORY]` | Fixed-size pool of inventory instances, managed via `Serialization_Header` UUID hashing. |

### Limits

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__INVENTORY` | 64 | Maximum number of inventories in the pool. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_inventory_manager` | `(Inventory_Manager*) -> void` | Initializes all inventory slots as empty/deallocated. Each inventory's `Serialization_Header` is set to indicate an unallocated state. |

### Allocation and Release

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_p_inventory_using__this_uuid_in__inventory_manager` | `(Inventory_Manager*, Identifier__u32 uuid) -> Inventory*` | `Inventory*` | Allocates an inventory from the pool with the given UUID. Uses UUID hashing to find an available slot. Returns null if no slots are available. |
| `release_inventory_in__inventory_manager` | `(Inventory_Manager*, Inventory*) -> void` | `void` | Releases an inventory back to the pool, marking its `Serialization_Header` as deallocated. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_inventory_by__uuid_in__inventory_manager` | `(Inventory_Manager*, Identifier__u32) -> Inventory*` | `Inventory*` | Finds and returns the inventory with the matching UUID via hash-based lookup. Returns null if not found. |

## Agentic Workflow

### Inventory_Manager Lifecycle

    [Uninitialized] --> initialize_inventory_manager
                            |
                        [Initialized — all slots empty]
                            |
                    allocate_p_inventory_using__this_uuid_in__inventory_manager
                            |
                        [Inventory Allocated with UUID]
                            |
                    (inventory used: add/remove items, serialize, etc.)
                            |
                    release_inventory_in__inventory_manager
                            |
                        [Slot Deallocated — available for reuse]

### UUID Hashing

The `Inventory_Manager` uses the engine's UUID hashing system (from
`serialization/hashing.h`) to manage its pool. Each `Inventory` has a
`Serialization_Header` containing a UUID and struct size. The hashing
utilities provide:

- **Allocation**: `allocate_serialization_header_with__this_uuid` or
  `get_next_available__allocation_in__contiguous_array` to find a free
  slot for a given UUID.
- **Lookup**: `dehash_identitier_u32_in__contigious_array` to resolve a
  UUID to a pool slot.
- **Collision handling**: `poll_for__uuid_collision` handles hash
  collisions within the contiguous array.

### Allocation Patterns

**Entity inventory allocation:**

    Inventory *p_inv = allocate_p_inventory_using__this_uuid_in__inventory_manager(
        p_inventory_manager,
        entity_uuid);

**Container inventory allocation:**

    Identifier__u32 container_uuid = get_uuid_for__container(tile_position);
    Inventory *p_inv = allocate_p_inventory_using__this_uuid_in__inventory_manager(
        p_inventory_manager,
        container_uuid);

### Lookup Pattern

Inventories are retrieved by UUID, which works for both entity and container
inventories:

    Inventory *p_inv = get_inventory_by__uuid_in__inventory_manager(
        p_inventory_manager,
        uuid);
    if (!p_inv) {
        // inventory not found or not allocated
    }

### ECS Integration

The `Inventory_Manager` is the central pool through which the ECS accesses
inventories:

- **Entity association**: An entity with
  `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` has its inventory
  allocated from this pool using the entity's UUID.
- **Container association**: World containers (tiles with
  `TILE_FLAGS__BIT_IS_CONTAINER`) have inventories allocated using
  `get_uuid_for__container(tile_position)`.
- **Serialized_Field**: The `Serialized_Field` union includes
  `Inventory *p_serialized_field__inventory`, enabling the serialization
  pipeline to reference inventories managed by this pool.
- **World ownership**: Because the `Inventory_Manager` is owned by `World`,
  all inventories are implicitly scoped to the current world. World
  load/unload cycles reset the entire inventory pool.

### Preconditions

- `initialize_inventory_manager`: requires non-null pointer.
- `allocate_p_inventory_using__this_uuid_in__inventory_manager`: requires
  available slots in the pool. UUID should be unique among currently
  allocated inventories (hash collisions are handled, but duplicate UUIDs
  are not).
- `release_inventory_in__inventory_manager`: the inventory must have been
  previously allocated from this manager.
- `get_inventory_by__uuid_in__inventory_manager`: no preconditions beyond
  non-null manager pointer.

### Postconditions

- After `initialize_inventory_manager`: all inventory slots are empty and
  available for allocation.
- After successful allocation: the returned inventory is initialized with
  the given UUID and has empty item stacks.
- After release: the inventory slot is available for reuse. The released
  pointer should not be dereferenced.
- `get_inventory_by__uuid_in__inventory_manager` returns null if no
  inventory with the given UUID is currently allocated.

### Error Handling

- Allocation returns null if the pool is exhausted.
- Lookup returns null if no matching UUID is found.
