# 1 Specification: core/include/inventory/item.h

## 1.1 Overview

Provides initialization and query utilities for the `Item` struct — the
engine's representation of a single item type. An `Item` is a lightweight
value type that identifies what kind of item it represents and carries an
opaque `Item_Data` payload defined by the platform. Items are stored inside
`Item_Stack` structs, which add quantity tracking on top of the base item
identity.

## 1.2 Dependencies

- `defines.h` (for `Item`, `Item_Kind`, `Item_Data`)
- `defines_weak.h` (forward declarations)

## 1.3 Types

### 1.3.1 Item (struct)

    typedef struct Item_t {
        enum Item_Kind      the_kind_of_item__this_item_is;
        Item_Data           item_data;
    } Item;

| Field | Type | Description |
|-------|------|-------------|
| `the_kind_of_item__this_item_is` | `enum Item_Kind` | Discriminator identifying the kind of item. `Item_Kind__None` indicates an empty/invalid item. |
| `item_data` | `Item_Data` | Platform-defined payload. Declared via `DEFINE_ITEM_DATA` or defaults to an empty struct. |

### 1.3.2 Item_Data (struct, platform-defined)

Declared via `types/implemented/item_data.h`. If `DEFINE_ITEM_DATA` is not
provided by the platform, defaults to an empty struct:

    typedef struct Item_Data_t {
    } Item_Data;

### 1.3.3 Item_Kind (enum)

Defined externally via `DEFINE_ITEM_KIND` or defaults to:

    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Unknown
    } Item_Kind;

| Value | Description |
|-------|-------------|
| `Item_Kind__None` | Empty/invalid item sentinel. |
| `Item_Kind__Unknown` | Upper-bound sentinel for array sizing and bounds checking. |

Platform or game implementations extend this enum with concrete item kinds
between `None` and `Unknown`.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_item` | `(Item*, enum Item_Kind) -> void` | Initializes the item with the given kind. |
| `initialize_item_as__empty` | `(Item*) -> void` | Initializes the item as `Item_Kind__None`. |
| `get_item__empty` | `(void) -> Item` | Returns a value-type empty item (`Item_Kind__None`). |

### 1.4.2 Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_item_kind_of__item` | `(Item*) -> Item_Kind` | `Item_Kind` | Returns the item's kind discriminator. |
| `is_p_item__empty` | `(Item*) -> bool` | `bool` | True if the item's kind is `Item_Kind__None`. |

## 1.5 Agentic Workflow

### 1.5.1 Item as a Value Type

`Item` is a small value type (an enum plus platform-defined data). It is
designed to be copied freely and embedded inside `Item_Stack`. It carries
no heap-allocated pointers, so no lifecycle management is needed beyond
initialization.

### 1.5.2 Item Lifecycle

    [Uninitialized] --> initialize_item / initialize_item_as__empty --> [Initialized]
                                                                            |
                                                                    (embedded in Item_Stack)
                                                                            |
                                                                    (copied / queried freely)

### 1.5.3 Relationship to Item_Manager

Items are not typically constructed in isolation. They are created via the
`Item_Manager` template system and embedded into `Item_Stack` structs:

    Item item = get_item_from__item_manager(p_item_manager, Item_Kind__Sword);
    add_item_to__inventory(p_inventory, item, quantity, max_quantity);

The `Item_Manager` stores one `Item` template per `Item_Kind`. Calling
`get_item_from__item_manager` returns a value copy of the template.

### 1.5.4 Relationship to ECS

In the engine's ECS design, items do not exist as standalone entities.
They exist only as data within `Item_Stack` slots inside `Inventory`
instances. Entities reference inventories by UUID (via
`ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION`), and the `Serialized_Field`
union provides `p_serialized_field__item_stack` for serialization of
individual item stacks within the ECS serialization pipeline.

### 1.5.5 Preconditions

- `get_item_kind_of__item`: requires non-null `p_item`.
- `is_p_item__empty`: requires non-null `p_item`.

### 1.5.6 Postconditions

- After `initialize_item_as__empty`: `is_p_item__empty` returns true.
- After `initialize_item` with a non-`None` kind: `is_p_item__empty`
  returns false.

### 1.5.7 Error Handling

- No debug assertions in the current implementation. Callers are responsible
  for passing valid pointers.
