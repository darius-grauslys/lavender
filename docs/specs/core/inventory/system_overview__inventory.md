# System Overview: Inventory System

## Purpose

The inventory system provides item definition, quantified item storage,
inventory management, and serialization for the engine. It enables entities
(players, NPCs) and world containers (chests, crates) to hold collections
of items, supports data-driven item stack creation through factory
functions, and provides persistent storage through serialization. The
system is a core ECS component: entities and world tiles reference
inventories by UUID through the `Inventory_Manager` pool.

The system is split across three managers — `Item_Manager` (item
templates), `Item_Stack_Manager` (item stack factories), and
`Inventory_Manager` (inventory pool). The `Item_Manager` and
`Inventory_Manager` are owned by `World`; the `Item_Stack_Manager` is
standalone.

## Architecture

### Ownership Hierarchy

    Game
    └── World* (pM_world)
        ├── Item_Manager                          (item template registry)
        │   └── Item item_templates[Item_Kind__Unknown]
        │       ├── Item_Kind the_kind_of_item__this_item_is
        │       └── Item_Data item_data           (platform-defined)
        │
        ├── Inventory_Manager                     (inventory pool)
        │   └── Inventory[MAX_QUANTITY_OF__INVENTORY = 64]
        │       ├── Serialization_Header _serialization_header
        │       ├── Item_Stack items[INVENTORY_ITEM_MAXIMUM_QUANTITY_OF = 27]
        │       │   ├── Serialization_Header _serialization_header
        │       │   ├── Item item
        │       │   │   ├── Item_Kind the_kind_of_item__this_item_is
        │       │   │   └── Item_Data item_data
        │       │   ├── Quantity__u8 quantity_of__items
        │       │   └── Quantity__u8 max_quantity_of__items
        │       └── Quantity__u8 quantity_of__item_stacks
        │
        └── Entity_Manager                        (entities reference inventories)
            └── Entity[]
                └── ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION

    Item_Stack_Manager                            (standalone, factory registry)
    └── Item_Stack_Allocation_Specifier[ITEM_STACK_RECORD_MAX_QUANTITY_OF = 256]
        ├── enum Item_Kind the_kind_of_item :15
        ├── bool is_allocated :1
        └── f_Item_Stack__Create f_item_stack__create

### Why Three Managers?

- **Item_Manager** (owned by `World`): A read-only template registry. Maps
  each `Item_Kind` to a pre-configured `Item` archetype. This allows items
  to be defined once and instantiated by kind throughout the engine.
  Populated at initialization and never modified at runtime. Critical
  dependency for deserialization — the `Item_Manager` must be fully
  populated before any inventory or item stack deserialization occurs.

- **Item_Stack_Manager** (standalone): A factory registry. Maps each
  `Item_Kind` to a factory function (`f_Item_Stack__Create`) that knows
  how to create a properly configured `Item_Stack` with kind-specific
  defaults (e.g., different max stack sizes for different items). This
  separates item stack creation policy from the inventory storage mechanism.

- **Inventory_Manager** (owned by `World`): A pool allocator for
  `Inventory` instances. Inventories are allocated with UUIDs that encode
  ownership (entity vs. container) and spatial coordinates (for
  containers), enabling both entity-based and world-position-based lookup
  from a single pool. Uses the engine's UUID hashing system
  (`serialization/hashing.h`) for O(1) average-case allocation and lookup.

### World Ownership

Because `Inventory_Manager` and `Item_Manager` are owned by `World`, all
inventories and item templates are scoped to the currently loaded world.
When the world is deallocated, the entire inventory pool is invalidated.
This is consistent with the engine's design where world-specific state
(entities, chunks, collision nodes) is owned by `World` while global
concerns (hitbox type registration, process management) are owned by
`Game`.

## Item Type System

### Item Definition

An `Item` is a lightweight value type containing an `Item_Kind`
discriminator and a platform-defined `Item_Data` payload:

    Item
    ├── Item_Kind the_kind_of_item__this_item_is
    └── Item_Data item_data

Items carry no heap-allocated pointers and are freely copyable. The
`Item_Data` struct is defined via `types/implemented/item_data.h` and
defaults to an empty struct if the platform does not provide one.

### Item_Kind Enum

The `Item_Kind` enum is extensible via the `DEFINE_ITEM_KIND` pattern:

    typedef enum Item_Kind {
        Item_Kind__None = 0,    // empty sentinel
        // ... platform-defined kinds ...
        Item_Kind__Unknown      // upper-bound sentinel
    } Item_Kind;

`Item_Kind__Unknown` serves as the array size for `Item_Manager` templates
and as a bounds-checking sentinel.

### Item Registration

Items are registered in two phases during initialization:

1. **Core registration**: `register_core_items_into__item_manager`
   registers engine-level items common to all platforms.
2. **Platform/game registration**: `register_items` (declared in
   `implemented/item_registrar.h`) registers platform-specific or
   game-specific items.

        initialize_item_manager(&item_manager)
            → register_core_items_into__item_manager(&item_manager)
            → register_items(&item_manager)

After registration, items are retrieved by kind as value copies:

    Item item = get_item_from__item_manager(&item_manager, Item_Kind__Sword);

### Item Stack Creation

The `Item_Stack_Manager` provides data-driven item stack creation. Each
`Item_Kind` can register a factory function through an
`Item_Stack_Allocation_Specifier`:

    Item_Stack_Allocation_Specifier *p_spec =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &item_stack_manager, Item_Kind__Potion);
    initialize_item_stack_allocation_specifier(
        p_spec, Item_Kind__Potion, f_create_potion_stack);

Item stacks are then created through the manager:

    initalize_item_stack_with__item_stack_manager(
        &item_stack_manager, Item_Kind__Potion, 5, &item_stack);

This invokes the registered factory function, which configures the item
stack with kind-specific defaults (e.g., max stack size of 99 for potions
vs. 1 for weapons).

## Inventory Management

### Inventory Pool

The `Inventory_Manager` maintains a fixed-size pool of 64 `Inventory`
instances. Inventories are allocated with a UUID and retrieved by UUID
using the engine's hash-based pool management (`hashing.h`):

    Inventory *p_inv = allocate_p_inventory_using__this_uuid_in__inventory_manager(
        &inventory_manager, uuid);

    Inventory *p_found = get_inventory_by__uuid_in__inventory_manager(
        &inventory_manager, uuid);

### UUID Encoding

Inventory UUIDs encode ownership and spatial information in a single
`Identifier__u32`:

    Bit Layout:
       [31 .. 26] [25]       [24 .. 22] [21 .. 11] [10 ..  0]
       Item Stack  Entity/    Z Axis     X Axis     Y Axis
       Index       Container

- **Entity inventories**: Bit 25 is set. The lower 25 bits encode the
  entity UUID. Used for players, NPCs, and other entities.
- **Container inventories**: Bit 25 is clear. Bits 24-0 encode the tile
  coordinates (X, Y, Z) of the container in the world.

Container UUIDs are constructed from tile positions:

    Identifier__u32 uuid = get_uuid_for__container(tile_position);

### Item Stack Slots

Each `Inventory` contains a fixed array of 27 `Item_Stack` slots
(`INVENTORY_ITEM_MAXIMUM_QUANTITY_OF`), plus 3 reserved consumable slots
(`INVENTORY_CONSUMABLES_QUANTITY_OF`). Each `Item_Stack` has its own
`Serialization_Header` for individual addressability and holds:

- An `Item` (the item type with kind and platform data).
- A quantity and max quantity.

### Item Operations

Items are added, removed, and queried through the `Inventory` API:

**Adding items:**

    Item_Stack *p_stack = add_item_to__inventory(
        p_inventory, item, quantity, max_quantity);

**Removing items by kind and quantity (spans multiple stacks):**

    remove_this_many_item_kinds_from__inventory(
        p_inventory, Item_Kind__Potion, 3);

**Searching for items (iterator pattern):**

    Item_Stack *p_stack = get_first_p_item_stack_of__this_item_kind_from__inventory(
        p_inventory, Item_Kind__Potion);
    while (p_stack) {
        // process stack
        p_stack = get_next_p_item_stack_of__this_item_kind_from__inventory(
            p_inventory, p_stack, Item_Kind__Potion);
    }

**Checking item availability:**

    if (does_inventory_have_this_many_of__item_kind(
            p_inventory, Item_Kind__Arrow, 10)) {
        // player has enough arrows
    }

### Merge and Swap

When item stacks interact (e.g., drag-and-drop in a UI):

    bool was_swapped = resolve_item_stack__merge_or_swap(
        p_source_stack, p_destination_stack);

- **Same item kind**: quantities merge. Overflow remains in the source.
- **Different item kinds**: the two stacks swap entirely.

## ECS Integration

### Entity-Inventory Association

In the engine's ECS design, entities do not embed inventories directly.
Instead, the association is by UUID:

1. An entity with `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` has an
   inventory allocated from the `Inventory_Manager` pool using the
   entity's UUID (with the entity bit set).
2. The entity's serialization handler saves/loads the inventory UUID.
3. At runtime, the inventory is looked up via
   `get_inventory_by__uuid_in__inventory_manager`.

### Container-Inventory Association

World containers (tiles with `TILE_FLAGS__BIT_IS_CONTAINER`) have
inventories allocated using spatially-encoded UUIDs:

    Identifier__u32 uuid = get_uuid_for__container(tile_position);
    Inventory *p_inv = allocate_p_inventory_using__this_uuid_in__inventory_manager(
        p_inventory_manager, uuid);

This enables O(1) lookup of a container's inventory given its tile
position.

### Serialized_Field Integration

The `Serialized_Field` union (used throughout the ECS serialization
pipeline) includes direct pointers for inventory types:

    union {
        Inventory *p_serialized_field__inventory;
        Item_Stack *p_serialized_field__item_stack;
        Entity *p_serialized_field__entity;
        Chunk *p_serialized_field__chunk;
    };

This enables the serialization system to treat inventories and item stacks
as first-class serializable components alongside entities and chunks.

### UUID Hashing

The `Inventory_Manager` uses the engine's UUID hashing utilities from
`serialization/hashing.h`:

- **Allocation**: `get_next_available__allocation_in__contiguous_array`
  finds a free slot for a given UUID, handling hash collisions via
  `poll_for__uuid_collision`.
- **Lookup**: `dehash_identitier_u32_in__contigious_array` resolves a UUID
  to a pool slot in O(1) average case.
- **Collision handling**: The hashing system handles UUID collisions
  (congruent UUIDs after modulo) by probing adjacent slots.

## Serialization

### Inventory Serialization

Inventories support full serialization to and from persistent storage:

    PLATFORM_Write_File_Error err = serialize_inventory(
        p_fs_context, p_request, p_inventory);

    PLATFORM_Read_File_Error err = deserialize_inventory(
        p_fs_context, p_item_manager, p_request, p_inventory);

Serialization writes each item stack in the inventory. Deserialization
requires the `Item_Manager` to resolve serialized `Item_Kind` values back
into fully initialized `Item` structs.

### Item Stack Serialization

Individual item stacks are serialized as a packed struct:

    struct {
        enum Item_Kind the_kind_of__item;
        Quantity__u8 quantity_of__items;
        Quantity__u8 max_quantity_of__items;
    };

The `Item_Kind` is the key that bridges serialization and runtime: it is
written to disk as an enum value and resolved back through the
`Item_Manager` on load.

## Lifecycle

### Initialization

    initialize_item_manager(&world.item_manager)
        → All item template slots set to default/empty.

    register_core_items_into__item_manager(&world.item_manager)
        → Core engine items registered.

    register_items(&world.item_manager)
        → Platform/game-specific items registered.

    initialize_item_stack_manager(&item_stack_manager)
        → All specifier slots set to empty/deallocated.

    (Register item stack allocation specifiers for each item kind)

    initialize_inventory_manager(&world.inventory_manager)
        → All inventory slots set to empty/deallocated.

### Inventory Allocation

    allocate_p_inventory_using__this_uuid_in__inventory_manager(
        &inventory_manager, uuid)
        → Hashes UUID to find an available slot in the pool.
        → Handles hash collisions via probing.
        → Initializes the inventory with the given UUID.
        → Returns pointer to the allocated inventory.

### Item Addition

    add_item_to__inventory(p_inventory, item, quantity, max_quantity)
        → Finds the first empty item stack slot.
        → Initializes the slot with the given item and quantities.
        → Increments quantity_of__item_stacks.
        → Returns pointer to the populated item stack.

### Inventory Release

    release_inventory_in__inventory_manager(
        &inventory_manager, p_inventory)
        → Marks the inventory's Serialization_Header as deallocated.
        → The slot becomes available for reuse.
        → The released pointer should not be dereferenced.

### World Unload

When the world is deallocated, the entire `Inventory_Manager` pool is
invalidated. All inventory pointers held by external systems become
dangling. Systems must release their inventory references before world
unload.

## Capacity Constraints

| Resource | Pool Size | Determined By |
|----------|-----------|---------------|
| `Inventory` | `MAX_QUANTITY_OF__INVENTORY` (64) | Maximum concurrent inventories (entities + containers). |
| `Item_Stack` (per inventory) | `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` (27) | Maximum item slots per inventory. |
| `Item` template | `Item_Kind__Unknown` | Number of distinct item kinds (platform-defined). |
| `Item_Stack_Allocation_Specifier` | `ITEM_STACK_RECORD_MAX_QUANTITY_OF` (256) | Maximum registered item stack factories. |

## Relationship Summary

| Concern | Managed By |
|---------|------------|
| Item type definition and templates | `Item_Manager` (owned by `World`) |
| Item template registration (core) | `register_core_items_into__item_manager` |
| Item template registration (platform/game) | `register_items` (Item_Registrar, implemented by platform) |
| Item stack factory registration | `Item_Stack_Manager` (standalone) |
| Item stack creation with defaults | `Item_Stack_Manager` via `f_Item_Stack__Create` |
| Inventory pool allocation/deallocation | `Inventory_Manager` (owned by `World`) |
| Inventory UUID-based lookup | `Inventory_Manager` via `hashing.h` utilities |
| Entity-inventory association | Entity UUID → `Inventory_Manager` lookup |
| Container-inventory association | Tile position → `get_uuid_for__container` → `Inventory_Manager` lookup |
| Item storage within inventories | `Inventory` (fixed `Item_Stack` array) |
| Item stack merge/swap resolution | `Item_Stack` (`resolve_item_stack__merge_or_swap`) |
| Inventory serialization | `Inventory` + `PLATFORM_File_System_Context` |
| Item stack serialization | `Item_Stack` + `PLATFORM_File_System_Context` |
| Item kind resolution during deserialization | `Item_Manager` |
| ECS serialization field references | `Serialized_Field` union (inventory and item_stack pointers) |

The `Item_Kind` enum is the central bridge between all components: the
`Item_Manager` indexes templates by kind, the `Item_Stack_Manager` indexes
factories by kind, `Inventory` search/query operations filter by kind, and
serialization persists/restores kinds across save/load cycles.
