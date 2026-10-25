# Function Review: `copy_item_stack`

- **File of origin**: `core/include/inventory/item_stack.h`

## Semantic

Copies the item data fields (`item`, `quantity_of__items`, `max_quantity_of__items`) from a source `Item_Stack` to a destination `Item_Stack` by delegating to `set_item_stack`. The `_serialization_header` field of the destination is intentionally left untouched.

## Pre-conditions

1. `p_item_stack__source` must be non-null. It is dereferenced directly (`p_item_stack__source->item`, etc.) with no null check.
2. `p_item_stack__destination` must be non-null. This is validated in debug builds by `set_item_stack`, which calls `debug_abort` if the pointer is null.
3. Both pointers must refer to valid, initialized `Item_Stack` structs.

## Post-conditions

1. The destination's `item` field is set to the source's `item`.
2. The destination's `quantity_of__items` field is set to the source's `quantity_of__items`.
3. The destination's `max_quantity_of__items` field is set to the source's `max_quantity_of__items`.
4. The destination's `_serialization_header` (containing `uuid` and `size_of__struct`) is **not** modified — the destination retains its own identity.

## Correctness Verdict

**Correct**

The function correctly copies the item data from source to destination. The omission of `_serialization_header` is intentional and correct: the serialization header contains identity information (UUID) that belongs to the destination slot. This is confirmed by the sole caller, `copy_p_item_stack_to__inventory` in `core/source/inventory/inventory.c`, which copies item data into a destination slot that was previously initialized via `initialize_item_stack_as__empty` (which sets up the serialization header with the correct UUID for that inventory slot).

## Semantic Alignment

The implementation fulfills the semantic intent of copying item stack data. By delegating to `set_item_stack`, only the data fields (`item`, `quantity_of__items`, `max_quantity_of__items`) are transferred, while the destination's identity (`_serialization_header`) is preserved. This aligns with the Lavender engine's pattern where initialization/serialization headers are managed separately from item data.

## Implementation Correctness

- **Type compatibility**: `copy_item_stack` reads `quantity_of__items` and `max_quantity_of__items` as `Quantity__u8` (uint8_t) from the source struct and passes them to `set_item_stack`, which expects `Quantity__u32` (uint32_t). This is a safe implicit widening conversion with no data loss. Inside `set_item_stack`, the values are assigned back to `Quantity__u8` fields, which is also safe since the values originated from uint8_t fields.
- **Undefined behavior**: No broken pointer arithmetic, null dereference (source is not validated but this follows the codebase convention for `static inline` functions), no type punning, and no out-of-bounds access.
- **Validation**: `set_item_stack` performs a debug-mode null check on the destination pointer. The source pointer is not validated, consistent with the codebase convention for inline functions where callers are responsible for pointer validity.

## Side Effects

Mutates the destination `Item_Stack`: the `item`, `quantity_of__items`, and `max_quantity_of__items` fields are overwritten with values from the source. The source `Item_Stack` is read-only and is not modified. The destination's `_serialization_header` is preserved. No other side effects.
