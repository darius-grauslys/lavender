# Specification: core/include/inventory/item_stack_allocation_specifier.h

## Overview

Provides initialization and allocation-state management for the
`Item_Stack_Allocation_Specifier` struct — a record that associates an
`Item_Kind` with a factory function (`f_Item_Stack__Create`) for creating
pre-configured item stacks. These specifiers are managed by the
`Item_Stack_Manager` and enable data-driven item stack creation where each
item kind can define its own default stack configuration (e.g., max stack
size, initial properties).

## Dependencies

- `defines.h` (for `Item_Stack_Allocation_Specifier`, `Item_Kind`,
  `f_Item_Stack__Create`)

## Types

### Item_Stack_Allocation_Specifier (struct)

    typedef struct Item_Stack_Allocation_Specifier_t {
        enum Item_Kind the_kind_of_item__this_specifier_is_for  :15;
        bool is_item_stack_allocation_specifier__allocated       :1;
        f_Item_Stack__Create f_item_stack__create;
    } Item_Stack_Allocation_Specifier;

| Field | Type | Description |
|-------|------|-------------|
| `the_kind_of_item__this_specifier_is_for` | `enum Item_Kind` (15 bits) | The item kind this specifier is registered for. |
| `is_item_stack_allocation_specifier__allocated` | `bool` (1 bit) | Whether this specifier slot is currently in use. |
| `f_item_stack__create` | `f_Item_Stack__Create` | Factory function pointer for creating item stacks of this kind. May be null. |

### f_Item_Stack__Create (function pointer)

    typedef void (*f_Item_Stack__Create)(Item_Stack *p_item_stack);

Factory function type for creating item stacks with kind-specific defaults.
Receives a pointer to an item stack to initialize in-place.

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_item_stack_allocation_specifier` | `(Item_Stack_Allocation_Specifier*, enum Item_Kind, f_Item_Stack__Create) -> void` | Initializes the specifier with the given item kind and factory function. |
| `initialize_item_stack_allocation_specifier_as__empty` | `(Item_Stack_Allocation_Specifier*) -> void` | Initializes as empty (`Item_Kind__None`, null factory, deallocated). Calls `initialize_item_stack_allocation_specifier` then clears the allocated flag. (static inline) |

### Allocation State Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_item_stack_allocation_specifier__allocated` | `(Item_Stack_Allocation_Specifier*) -> bool` | `bool` | True if the specifier slot is allocated. |
| `set_item_stack_allocation_specifier_as__allocated` | `(Item_Stack_Allocation_Specifier*) -> void` | `void` | Marks the specifier as allocated. |
| `set_item_stack_allocation_specifier_as__deallocated` | `(Item_Stack_Allocation_Specifier*) -> void` | `void` | Marks the specifier as deallocated. |

## Agentic Workflow

### Specifier Lifecycle

    [Uninitialized] --> initialize_item_stack_allocation_specifier_as__empty
                            |
                        [Empty / Deallocated]
                            |
                    allocate (via Item_Stack_Manager)
                            |
                    initialize_item_stack_allocation_specifier
                            |
                    set_item_stack_allocation_specifier_as__allocated
                            |
                        [Allocated]
                            |
                    (used to create Item_Stacks via f_item_stack__create)
                            |
                    release (via Item_Stack_Manager)
                            |
                    set_item_stack_allocation_specifier_as__deallocated
                            |
                        [Deallocated]

### Factory Pattern

Each `Item_Kind` can register a custom factory function that knows how to
create a properly configured `Item_Stack` for that kind. This allows
different items to have different default max stack sizes, initial
quantities, or other kind-specific setup:

    // Registration
    initialize_item_stack_allocation_specifier(
        p_specifier,
        Item_Kind__Potion,
        f_create_potion_stack);

    // Usage (via Item_Stack_Manager)
    initalize_item_stack_with__item_stack_manager(
        p_item_stack_manager,
        Item_Kind__Potion,
        quantity,
        p_item_stack);

### Preconditions

- All functions require a non-null `p_item_stack_allocation_specifier`.
- `initialize_item_stack_allocation_specifier`: `f_item_stack__create` may
  be null (specifier will exist but cannot create stacks via factory).

### Postconditions

- After `initialize_item_stack_allocation_specifier_as__empty`:
  `is_item_stack_allocation_specifier__allocated` returns false,
  item kind is `Item_Kind__None`, factory is null.
- After `set_item_stack_allocation_specifier_as__allocated`:
  `is_item_stack_allocation_specifier__allocated` returns true.
- After `set_item_stack_allocation_specifier_as__deallocated`:
  `is_item_stack_allocation_specifier__allocated` returns false.

### Error Handling

- No debug assertions in the current implementation. Callers are responsible
  for passing valid pointers.
