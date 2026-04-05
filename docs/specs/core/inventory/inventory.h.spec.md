# Specification: core/include/inventory/inventory.h

## Overview

Provides initialization, serialization, item management, and query utilities
for the `Inventory` struct — a fixed-size container of `Item_Stack` slots
identified by a UUID. Inventories are the primary storage abstraction for
items in the engine, used by both entities (players, NPCs) and world
containers (chests, crates). The UUID encoding scheme distinguishes entity
inventories from container inventories and encodes spatial coordinates for
containers.

In the engine's ECS design, entities do not embed inventories directly.
Instead, entities reference inventories by UUID through the serialization
system (`ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION`), and the
`Serialized_Field` union provides `p_serialized_field__inventory` for
ECS-level inventory references.

## Dependencies

- `defines.h` (for `Inventory`, `Item_Stack`, `Item`, `Item_Kind`,
  `Identifier__u32`, `Identifier__u16`, `Index__u8`, `Quantity__u8`,
  `Quantity__u32`, `Tile_Vector__3i32`, `Serialization_Header`,
  `PLATFORM_Write_File_Error`, `PLATFORM_Read_File_Error`)
- `defines_weak.h` (forward declarations for `PLATFORM_File_System_Context`,
  `Serialization_Request`, `Item_Manager`)

## Types

### Inventory (struct)

    typedef struct Inventory_t {
        Serialization_Header    _serialization_header;
        Item_Stack items[INVENTORY_ITEM_MAXIMUM_QUANTITY_OF];
        Quantity__u8 quantity_of__item_stacks;
    } Inventory;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management, hashing, and serialization. |
| `items` | `Item_Stack[INVENTORY_ITEM_MAXIMUM_QUANTITY_OF]` | Fixed-size array of item stack slots. |
| `quantity_of__item_stacks` | `Quantity__u8` | Current number of occupied item stack slots. |

### UUID Encoding

Inventory UUIDs encode ownership and spatial information in a single
`Identifier__u32`:

    Bit Layout:
       [31 .. 26] [25]       [24 .. 22] [21 .. 11] [10 ..  0]
       Item Stack  Entity/    Z Axis     X Axis     Y Axis
       Index       Container

| Bit Field | Constant | Description |
|-----------|----------|-------------|
| Bit 25 | `UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER` | If set: entity inventory. If clear: container inventory. |
| Bits 31-26 | `UUID_MASK__INVENTORY__ITEM_STACK` | Item stack index within the inventory. |
| Bits 24-22 | `UUID_MASK__INVENTORY__CONTAINER__Z_AXIS` | Z coordinate for container inventories. |
| Bits 21-11 | `UUID_MASK__INVENTORY__CONTAINER__X_AXIS` | X coordinate for container inventories. |
| Bits 10-0 | `UUID_MASK__INVENTORY__CONTAINER__Y_AXIS` | Y coordinate for container inventories. |
| Bits 24-0 (entity) | `UUID_MASK__INVENTORY__ENTITY` | Entity UUID portion. |

### Limits

| Macro | Value | Description |
|-------|-------|-------------|
| `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` | 27 | Maximum number of item stack slots per inventory. |
| `INVENTORY_CONSUMABLES_QUANTITY_OF` | 3 | Reserved consumable slots. |
| `MAX_QUANTITY_OF__INVENTORY` | 64 | Maximum number of inventories in the `Inventory_Manager` pool. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_inventory` | `(Inventory*, Identifier__u32 uuid) -> void` | Initializes the inventory with the given UUID and empty item stacks. |
| `initialize_inventory_as__empty` | `(Inventory*) -> void` | Initializes as a fully empty inventory with no UUID. |

### Serialization

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `serialize_inventory` | `(PLATFORM_File_System_Context*, Serialization_Request*, Inventory*) -> PLATFORM_Write_File_Error` | `PLATFORM_Write_File_Error` | Serializes the entire inventory (all item stacks) to persistent storage. |
| `deserialize_inventory` | `(PLATFORM_File_System_Context*, Item_Manager*, Serialization_Request*, Inventory*) -> PLATFORM_Read_File_Error` | `PLATFORM_Read_File_Error` | Deserializes an inventory from persistent storage, resolving items through the item manager. |

### Item Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_item_to__inventory` | `(Inventory*, Item, Quantity__u8, Quantity__u8 max) -> Item_Stack*` | `Item_Stack*` | Adds an item to the first available slot. Returns the item stack used, or null if inventory is full. |
| `copy_p_item_stack_to__inventory` | `(Inventory*, Item_Stack* src) -> void` | `void` | Copies an item stack into the first available inventory slot. |
| `move_p_item_stack_to__inventory` | `(Inventory*, Item_Stack* src) -> void` | `void` | Moves an item stack into the inventory, clearing the source. |
| `remove_p_item_stack_from__inventory` | `(Inventory*, Item_Stack*) -> void` | `void` | Removes a specific item stack from the inventory by pointer. |
| `remove_item_stack_from__inventory_using__identifier_for__item_stack` | `(Inventory*, Identifier__u16) -> void` | `void` | Removes an item stack by its identifier. |
| `remove_this_many_item_kinds_from__inventory` | `(Inventory*, enum Item_Kind, Quantity__u32) -> void` | `void` | Removes a specified quantity of items of the given kind, spanning multiple stacks if necessary. |
| `remove_all_item_stacks_from__inventory` | `(Inventory*) -> void` | `void` | Clears all item stacks from the inventory. |

### Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_inventory__empty` | `(Inventory*) -> bool` | `bool` | True if all item stacks are empty. |
| `get_first_p_item_stack_of__this_item_kind_from__inventory` | `(Inventory*, enum Item_Kind) -> Item_Stack*` | `Item_Stack*` | Returns the first stack matching the kind, or null. |
| `get_next_p_item_stack_of__this_item_kind_from__inventory` | `(Inventory*, Item_Stack* start, enum Item_Kind) -> Item_Stack*` | `Item_Stack*` | Returns the next matching stack after `start`, or null. Iterator pattern. |
| `get_p_item_stack_from__inventory_by__index` | `(Inventory*, Index__u8) -> Item_Stack*` | `Item_Stack*` | Returns the item stack at the given slot index. |
| `get_p_item_stack_from__inventory` | `(Inventory*, Identifier__u32) -> Item_Stack*` | `Item_Stack*` | Returns the item stack matching the given identifier. |
| `does_inventory_have_this_many_of__item_kind` | `(Inventory*, enum Item_Kind, Quantity__u32) -> bool` | `bool` | True if the inventory contains at least the specified quantity of the given kind across all stacks. |
| `does_inventory_have__available_item_stacks` | `(Inventory*) -> bool` | `bool` | True if there is at least one empty slot. |
| `does_inventory_have_this__item_kind` | `(Inventory*, enum Item_Kind) -> bool` | `bool` | True if any stack holds the given kind. (static inline, delegates to `get_first_p_item_stack_of__this_item_kind_from__inventory`) |

### UUID Utilities (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_inventory_uuid_for__entity_or__container` | `(Identifier__u32) -> bool` | `bool` | True if the UUID's entity/container bit is set (entity). |
| `get_inventory_container__z_from__uuid` | `(Identifier__u32) -> u16` | `u16` | Extracts the Z coordinate from a container UUID. |
| `get_inventory_container__x_from__uuid` | `(Identifier__u32) -> u16` | `u16` | Extracts the X coordinate from a container UUID. |
| `get_inventory_container__y_from__uuid` | `(Identifier__u32) -> u16` | `u16` | Extracts the Y coordinate from a container UUID. |
| `set_inventory_uuid_flag_for__entity` | `(Identifier__u32*) -> void` | `void` | Sets the entity flag in the UUID. |
| `set_inventory_uuid_flag_for__container` | `(Identifier__u32*) -> void` | `void` | Clears the entity flag (marks as container). |
| `set_inventory_container__z_in__uuid` | `(Identifier__u32*, u16) -> void` | `void` | Encodes Z coordinate into the UUID. |
| `set_inventory_container__x_in__uuid` | `(Identifier__u32*, u16) -> void` | `void` | Encodes X coordinate into the UUID. |
| `set_inventory_container__y_in__uuid` | `(Identifier__u32*, u16) -> void` | `void` | Encodes Y coordinate into the UUID. |
| `set_inventory_uuid__item_stack_index` | `(Identifier__u32*, Index__u8) -> void` | `void` | Encodes an item stack index into the UUID. |
| `get_uuid_for__container` | `(Tile_Vector__3i32) -> Identifier__u32` | `Identifier__u32` | Constructs a container UUID from a tile position vector. |

## Agentic Workflow

### Inventory Lifecycle

    [Uninitialized] --> initialize_inventory / initialize_inventory_as__empty
                            |
                        [Initialized — empty slots]
                            |
            +-----------+---+---+-----------+
            |           |       |           |
        add_item    copy_stack  move_stack  deserialize
            |           |       |           |
            +-----------+---+---+-----------+
                            |
                    [Populated with items]
                            |
            +-----------+---+---+-----------+
            |           |       |           |
        remove_item  remove_all  serialize  query
            |           |       |           |
            +-----------+---+---+-----------+
                            |
                    (release via Inventory_Manager)

### Entity vs. Container Inventories

The UUID encoding distinguishes two inventory ownership models:

1. **Entity inventories**: UUID has the entity bit set. Used for players,
   NPCs, and other entities. The entity references the inventory by UUID
   through the ECS serialization system
   (`ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION`).

2. **Container inventories**: UUID has the entity bit clear. The UUID
   encodes the tile coordinates (X, Y, Z) of the container in the world,
   enabling spatial lookup:

       Identifier__u32 uuid = get_uuid_for__container(tile_position);
       Inventory *p_inv = get_inventory_by__uuid_in__inventory_manager(
           p_inventory_manager, uuid);

### ECS Integration

Inventories participate in the ECS through several mechanisms:

- **Entity flags**: `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` marks
  entities that have an associated inventory for serialization purposes.
- **Serialized_Field union**: The `Serialized_Field` type includes
  `Inventory *p_serialized_field__inventory` and
  `Item_Stack *p_serialized_field__item_stack`, enabling the serialization
  pipeline to reference inventories and item stacks as first-class
  serializable components.
- **UUID hashing**: Inventories use `Serialization_Header` UUIDs and are
  stored in the `Inventory_Manager` pool, which supports UUID-based
  hashing via the `hashing.h` utilities.

### Item Search Iteration

To iterate all stacks of a given kind:

    Item_Stack *p_stack = get_first_p_item_stack_of__this_item_kind_from__inventory(
        p_inventory, Item_Kind__Potion);
    while (p_stack) {
        // process p_stack
        p_stack = get_next_p_item_stack_of__this_item_kind_from__inventory(
            p_inventory, p_stack, Item_Kind__Potion);
    }

### Serialization Pattern

Inventories are serialized as a whole, which internally serializes each
item stack:

    PLATFORM_Write_File_Error err = serialize_inventory(
        p_fs_context, p_request, p_inventory);

Deserialization requires the `Item_Manager` to resolve item kinds:

    PLATFORM_Read_File_Error err = deserialize_inventory(
        p_fs_context, p_item_manager, p_request, p_inventory);

### Preconditions

- All functions require a non-null `p_inventory`.
- `deserialize_inventory`: requires a valid, fully populated `Item_Manager`.
- `add_item_to__inventory`: inventory must have available slots (check with
  `does_inventory_have__available_item_stacks`).
- UUID utility functions: callers must ensure UUIDs are properly constructed
  for the intended ownership model.

### Postconditions

- After `initialize_inventory_as__empty`: `is_inventory__empty` returns
  true.
- After `add_item_to__inventory` succeeds: the returned `Item_Stack*` is
  non-null and populated.
- After `remove_all_item_stacks_from__inventory`: `is_inventory__empty`
  returns true.

### Error Handling

- `serialize_inventory` returns `PLATFORM_Write_File_Error` on I/O failure.
- `deserialize_inventory` returns `PLATFORM_Read_File_Error` on I/O failure.
- `add_item_to__inventory` returns null if the inventory is full.
- Search functions return null if no matching item stack is found.
