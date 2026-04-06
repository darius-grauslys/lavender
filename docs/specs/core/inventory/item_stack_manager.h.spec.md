# 1 Specification: core/include/inventory/item_stack_manager.h

## 1.1 Overview

Provides initialization, allocation, release, and lookup utilities for the
`Item_Stack_Manager` — a pool-based manager for
`Item_Stack_Allocation_Specifier` records. The `Item_Stack_Manager` serves
as a registry that maps `Item_Kind` values to factory functions, enabling
data-driven creation of `Item_Stack` instances with kind-specific defaults.

The `Item_Stack_Manager` is a standalone manager not owned by `World` or
`Game` in the core struct hierarchy. It is used at initialization time to
register item stack creation policies.

## 1.2 Dependencies

- `defines.h` (for `Item_Stack_Manager`, `Item_Stack_Allocation_Specifier`,
  `Item_Kind`, `Item_Stack`, `Quantity__u32`, `Index__u32`)
- `defines_weak.h` (forward declarations)
- `debug/debug.h` (for `debug_abort` in debug builds)

## 1.3 Types

### 1.3.1 Item_Stack_Manager (struct)

    typedef struct Item_Stack_Manager_t {
        Item_Stack_Allocation_Specifier item_stack_allocation_specifiers
            [ITEM_STACK_RECORD_MAX_QUANTITY_OF];
        Quantity__u32 quantity_of__item_stack_allocation_specifier;
    } Item_Stack_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `item_stack_allocation_specifiers` | `Item_Stack_Allocation_Specifier[ITEM_STACK_RECORD_MAX_QUANTITY_OF]` | Fixed-size pool of allocation specifier slots. |
| `quantity_of__item_stack_allocation_specifier` | `Quantity__u32` | Current count of allocated specifiers. |

### 1.3.2 Limits

| Macro | Value | Description |
|-------|-------|-------------|
| `ITEM_STACK_RECORD_MAX_QUANTITY_OF` | 256 | Maximum number of item stack allocation specifiers in the pool. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_item_stack_manager` | `(Item_Stack_Manager*) -> void` | Initializes all specifier slots as empty/deallocated and resets the count. |

### 1.4.2 Allocation and Release

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_item_stack_allocation_specification_in__item_stack_manager` | `(Item_Stack_Manager*, enum Item_Kind) -> Item_Stack_Allocation_Specifier*` | `Item_Stack_Allocation_Specifier*` | Allocates a specifier slot for the given item kind. Returns null on failure (pool exhausted). |
| `release_item_stack_allocation_specification_in__item_stack_manager` | `(Item_Stack_Manager*, Item_Stack_Allocation_Specifier*) -> void` | `void` | Releases a specifier slot back to the pool. |

### 1.4.3 Item Stack Creation

| Function | Signature | Description |
|----------|-----------|-------------|
| `initalize_item_stack_with__item_stack_manager` | `(Item_Stack_Manager*, enum Item_Kind, Quantity__u32, Item_Stack*) -> void` | Creates/initializes an `Item_Stack` using the registered factory function for the given item kind with the specified quantity. |

### 1.4.4 Lookup (static inline, defined in header)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_item_stack_alloc_spec_by__index_from__item_stack_manager` | `(Item_Stack_Manager*, Index__u32) -> Item_Stack_Allocation_Specifier*` | `Item_Stack_Allocation_Specifier*` | Returns the specifier at the given index. Calls `debug_abort` and returns 0 in debug builds if index is out of bounds (`>= ITEM_STACK_RECORD_MAX_QUANTITY_OF`). |

## 1.5 Agentic Workflow

### 1.5.1 Item_Stack_Manager Lifecycle

    [Uninitialized] --> initialize_item_stack_manager
                            |
                        [Initialized — all slots empty, count = 0]
                            |
                    allocate_item_stack_allocation_specification_in__item_stack_manager
                            |
                        [Specifier Allocated — count incremented]
                            |
                    initalize_item_stack_with__item_stack_manager
                            |
                    (Item_Stack created with kind-specific defaults)
                            |
                    release_item_stack_allocation_specification_in__item_stack_manager
                            |
                        [Specifier Deallocated — slot available]

### 1.5.2 Registration Pattern

During game initialization, each item kind registers its factory function
through the `Item_Stack_Manager`:

    Item_Stack_Allocation_Specifier *p_spec =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            p_item_stack_manager,
            Item_Kind__Potion);
    initialize_item_stack_allocation_specifier(
        p_spec,
        Item_Kind__Potion,
        f_create_potion_stack);

### 1.5.3 Item Stack Creation Pattern

Once registered, item stacks are created through the manager:

    initalize_item_stack_with__item_stack_manager(
        p_item_stack_manager,
        Item_Kind__Potion,
        5,          // quantity
        p_item_stack);

The manager looks up the specifier for `Item_Kind__Potion` and invokes its
`f_item_stack__create` factory function, then sets the quantity.

### 1.5.4 Preconditions

- `initialize_item_stack_manager`: requires non-null pointer.
- `allocate_item_stack_allocation_specification_in__item_stack_manager`:
  requires available slots in the pool.
- `initalize_item_stack_with__item_stack_manager`: requires a registered
  specifier for the given item kind.
- `get_p_item_stack_alloc_spec_by__index_from__item_stack_manager`: index
  must be less than `ITEM_STACK_RECORD_MAX_QUANTITY_OF`. Debug builds call
  `debug_abort` on out-of-bounds access.

### 1.5.5 Postconditions

- After `initialize_item_stack_manager`: all specifier slots report
  `is_item_stack_allocation_specifier__allocated` as false.
- After successful allocation: the returned specifier is ready for
  initialization with `initialize_item_stack_allocation_specifier`.
- After release: the specifier slot is marked as deallocated and available
  for reuse.

### 1.5.6 Error Handling

- `get_p_item_stack_alloc_spec_by__index_from__item_stack_manager`: calls
  `debug_abort` and returns 0 on out-of-bounds index in debug builds.
- Allocation returns null if no slots are available.
