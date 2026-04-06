# 1 Specification: core/include/inventory/item_manager.h

## 1.1 Overview

Provides initialization, registration, and lookup utilities for the
`Item_Manager` — a template registry that maps each `Item_Kind` to a
pre-configured `Item` instance. The `Item_Manager` acts as a read-only
dictionary of item archetypes: once registered, item templates are looked
up by kind to produce `Item` values for use in item stacks and inventories.

The `Item_Manager` is owned by `World` and accessed from `Game` via
`get_p_item_manager_from__game` → `get_p_item_manager_from__world`.

## 1.2 Dependencies

- `defines.h` (for `Item_Manager`, `Item`, `Item_Kind`)
- `debug/debug.h` (for `debug_error` in debug builds)

## 1.3 Types

### 1.3.1 Item_Manager (struct)

    typedef struct Item_Manager_t {
        Item item_templates[(u16)Item_Kind__Unknown];
    } Item_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `item_templates` | `Item[Item_Kind__Unknown]` | Array of item templates indexed by `Item_Kind`. Each slot holds the archetype `Item` for that kind. |

The array size is `(u16)Item_Kind__Unknown`, which serves as the
upper-bound sentinel of the `Item_Kind` enum.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_item_manager` | `(Item_Manager*) -> void` | Initializes all item template slots to empty/default state. |

### 1.4.2 Registration (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_item_in__item_manager` | `(Item_Manager*, enum Item_Kind, Item) -> void` | Registers an item template at the slot corresponding to the given kind. In debug builds, calls `debug_error` and returns early if the kind is out of bounds (`>= Item_Kind__Unknown`). |

### 1.4.3 Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_item_from__item_manager` | `(Item_Manager*, enum Item_Kind) -> Item` | `Item` | Returns a value copy of the registered item template for the given kind. |

### 1.4.4 Core Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_core_items_into__item_manager` | `(Item_Manager*) -> void` | Registers all engine-level (core) item templates. Called during initialization before platform-specific registration. |

## 1.5 Agentic Workflow

### 1.5.1 Item_Manager Lifecycle

    [Uninitialized] --> initialize_item_manager
                            |
                        [Initialized — all slots empty]
                            |
                    register_core_items_into__item_manager
                            |
                        [Core items registered]
                            |
                    register_items (platform/game-specific, via item_registrar.h)
                            |
                        [All items registered — ready for lookup]
                            |
                    get_item_from__item_manager (repeated, read-only)
                            |
                        (Item values returned for use in Item_Stacks)

### 1.5.2 Registration Pattern

Items are registered in two phases:

1. **Core registration**: `register_core_items_into__item_manager` registers
   engine-level items common to all platforms.
2. **Platform/game registration**: `register_items` (from
   `implemented/item_registrar.h`) registers platform-specific or
   game-specific items.

Each registration call stores an `Item` value at the index corresponding
to its `Item_Kind`:

    Item sword_item;
    initialize_item(&sword_item, Item_Kind__Sword);
    register_item_in__item_manager(p_item_manager, Item_Kind__Sword, sword_item);

### 1.5.3 Lookup Pattern

After registration, items are retrieved by kind as value copies:

    Item item = get_item_from__item_manager(p_item_manager, Item_Kind__Sword);

### 1.5.4 Deserialization Dependency

The `Item_Manager` is a critical dependency during deserialization. When
item stacks or inventories are deserialized from persistent storage, the
serialized `Item_Kind` is resolved back into a full `Item` struct through
the `Item_Manager`:

    deserialize_item_stack(p_fs_context, p_item_manager, p_request, p_item_stack);
    deserialize_inventory(p_fs_context, p_item_manager, p_request, p_inventory);

This means the `Item_Manager` must be fully populated before any
deserialization occurs.

### 1.5.5 Preconditions

- `register_item_in__item_manager`: `the_kind_of__item` must be less than
  `Item_Kind__Unknown`. Debug builds emit `debug_error` on out-of-bounds.
- `get_item_from__item_manager`: the item kind should have been previously
  registered. Behavior for unregistered kinds depends on the default
  initialization state (empty item).

### 1.5.6 Postconditions

- After `initialize_item_manager`: all template slots are in their default
  (empty) state.
- After `register_item_in__item_manager`: `get_item_from__item_manager`
  with the same kind returns the registered item.

### 1.5.7 Error Handling

- `register_item_in__item_manager`: calls `debug_error` and returns early
  on out-of-bounds kind in debug builds. In release builds, the write is
  unchecked (undefined behavior if out of bounds).
