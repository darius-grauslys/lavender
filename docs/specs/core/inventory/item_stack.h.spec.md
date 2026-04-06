# 1 Specification: core/include/inventory/item_stack.h

## 1.1 Overview

Provides initialization, serialization, manipulation, and query utilities
for the `Item_Stack` struct — a quantified container for a single `Item`
type. An `Item_Stack` represents "N of item X" with a maximum capacity,
supporting merge, swap, copy, and removal operations. Item stacks are the
fundamental unit stored within `Inventory` slots and are individually
addressable via `Serialization_Header` UUIDs.

## 1.2 Dependencies

- `defines.h` (for `Item_Stack`, `Item`, `Item_Kind`, `Identifier__u16`,
  `Identifier__u32`, `Quantity__u8`, `Quantity__u32`,
  `Serialization_Header`)
- `defines_weak.h` (forward declarations for `PLATFORM_File_System_Context`,
  `Serialization_Request`, `Item_Manager`)
- `inventory/item.h` (for `is_p_item__empty`, `get_item_kind_of__item`)

## 1.3 Types

### 1.3.1 Item_Stack (struct)

    typedef struct Item_Stack_t {
        Serialization_Header        _serialization_header;
        Item                        item;
        Quantity__u8                quantity_of__items;
        Quantity__u8                max_quantity_of__items;
    } Item_Stack;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management, hashing, and serialization. |
| `item` | `Item` | The item type held in this stack. |
| `quantity_of__items` | `Quantity__u8` | Current number of items in the stack. |
| `max_quantity_of__items` | `Quantity__u8` | Maximum capacity of this stack. |

### 1.3.2 Serialization Format

Serialization writes and reads a packed struct:

    struct {
        enum Item_Kind the_kind_of__item;
        Quantity__u8 quantity_of__items;
        Quantity__u8 max_quantity_of__items;
    };

Deserialization resolves the `Item_Kind` back into a full `Item` via the
`Item_Manager`.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_item_stack` | `(Item_Stack*, Item, Identifier__u16, Quantity__u8, Quantity__u8 max) -> void` | Full initialization with item, identifier, quantity, and max quantity. |
| `initialize_item_stack_as__empty` | `(Item_Stack*, Identifier__u32) -> void` | Initializes as an empty stack with the given identifier. |

### 1.4.2 Serialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `serialize_item_stack` | `(PLATFORM_File_System_Context*, Serialization_Request*, Item_Stack*) -> void` | Writes the item stack to persistent storage via the platform file system. |
| `deserialize_item_stack` | `(PLATFORM_File_System_Context*, Item_Manager*, Serialization_Request*, Item_Stack*) -> void` | Reads an item stack from persistent storage, resolving the item kind through the item manager. |

### 1.4.3 Manipulation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_item_stack` | `(Item_Stack*, Item, Quantity__u32, Quantity__u32 max) -> void` | `void` | Overwrites the stack's item, quantity, and max quantity. |
| `copy_item_stack` | `(Item_Stack* src, Item_Stack* dst) -> void` | `void` | Copies source stack contents into destination via `set_item_stack`. (static inline) |
| `resolve_item_stack__merge_or_swap` | `(Item_Stack* src, Item_Stack* dst) -> bool` | `bool` | If same item kind: merges quantities (capped at max). If different: swaps stacks. Returns true only if a swap occurred. |
| `remove_quantity_of_items_from__item_stack` | `(Item_Stack*, Quantity__u8) -> Quantity__u32` | `Quantity__u32` | Removes up to the specified quantity. Returns the number of items that could NOT be removed (underflow remainder). |

### 1.4.4 Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_p_item_stack__empty` | `(Item_Stack*) -> bool` | `bool` | True if quantity is 0 or the item is empty. |
| `is_p_item_stack___full` | `(Item_Stack*) -> bool` | `bool` | True if the item is non-empty and quantity is less than max (i.e., has room). |
| `is_p_item_stack__full` | `(Item_Stack*) -> bool` | `bool` | True if quantity equals max quantity. |
| `is_p_item_stack_of__this_item_kind` | `(Item_Stack*, enum Item_Kind) -> bool` | `bool` | True if the stack's item kind matches the given kind. |
| `is_p_item_stacks_the_same__item_kind` | `(Item_Stack*, Item_Stack*) -> bool` | `bool` | True if both stacks hold the same item kind. |
| `get_quantity_of__items_in__item_stack` | `(Item_Stack*) -> Quantity__u32` | `Quantity__u32` | Returns the current quantity. |
| `get_item_kind_of__item_stack` | `(Item_Stack*) -> Item_Kind` | `Item_Kind` | Returns the item kind via `get_item_kind_of__item`. |

## 1.5 Agentic Workflow

### 1.5.1 Item_Stack Lifecycle

    [Uninitialized] --> initialize_item_stack / initialize_item_stack_as__empty
                            |
                        [Initialized]
                            |
                +-----------+-----------+
                |           |           |
          set_item_stack  merge/swap  remove_items
                |           |           |
                +-----------+-----------+
                            |
                    (stored in Inventory slot)
                            |
                    serialize / deserialize
                            |
                    (persistent storage)

### 1.5.2 Merge vs. Swap Resolution

When two item stacks interact (e.g., player drags one stack onto another
in the UI):

1. **Same item kind**: quantities are merged up to the destination's max.
   Overflow remains in the source.
2. **Different item kinds**: the two stacks are swapped entirely.

        resolve_item_stack__merge_or_swap(p_source, p_destination);
        // Returns true if swapped, false if merged.

### 1.5.3 Serialization Pattern

Item stacks are serialized as part of inventory serialization. The
serialized format stores only the `Item_Kind`, quantity, and max quantity.
On deserialization, the `Item_Manager` resolves the kind back into a full
`Item` struct:

    serialize_item_stack(p_fs_context, p_request, p_item_stack);
    deserialize_item_stack(p_fs_context, p_item_manager, p_request, p_item_stack);

### 1.5.4 ECS Integration

Item stacks are referenced in the ECS serialization system through the
`Serialized_Field` union, which includes:

    Item_Stack *p_serialized_field__item_stack;

This enables the serialization pipeline to handle individual item stacks
as first-class serializable fields alongside entities, inventories, and
chunks.

### 1.5.5 Preconditions

- All functions require non-null `p_item_stack`.
- `deserialize_item_stack` requires a valid `Item_Manager` with registered
  items.
- `resolve_item_stack__merge_or_swap` requires both source and destination
  to be non-null.

### 1.5.6 Postconditions

- After `initialize_item_stack_as__empty`: `is_p_item_stack__empty` returns
  true.
- After `remove_quantity_of_items_from__item_stack` removing all items:
  `is_p_item_stack__empty` returns true.
- After successful merge: source quantity decreases, destination quantity
  increases (capped at max).

### 1.5.7 Error Handling

- No explicit debug assertions in the inline functions. Callers are
  responsible for passing valid pointers.
- `remove_quantity_of_items_from__item_stack` returns the underflow
  remainder rather than failing.
