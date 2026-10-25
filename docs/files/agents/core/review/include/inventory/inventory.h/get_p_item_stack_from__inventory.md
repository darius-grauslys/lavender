# get_p_item_stack_from__inventory

**File of origin:** `core/source/inventory/inventory.c`

## Semantic

Extracts the item-stack index from the bit-packed UUID identifier, then returns a pointer to the corresponding `Item_Stack` element within the inventory's fixed-size `items` array.

## Pre-conditions

1. `p_inventory` must be a non-null pointer to a valid, initialized `Inventory` struct.
2. `identifier_for__item_stack` must be a valid UUID whose bits 26–31 encode a valid item-stack index (0 through `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF - 1`, i.e. 0–26). The caller is responsible for ensuring the identifier was produced by `set_inventory_uuid__item_stack_index` or equivalent encoding.
3. No null-check is performed on `p_inventory`; this is a low-level accessor and the caller must guarantee validity.

## Post-conditions

1. Returns a non-null pointer to `p_inventory->items[index]` where `index` is the 6-bit value extracted from bits 26–31 of `identifier_for__item_stack`.
2. The inventory itself is not modified (read-only access).
3. The returned pointer points directly into the `items` array of the provided inventory; the lifetime of the pointer is tied to the lifetime of the `Inventory` struct.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills the semantic intent. The function:

1. Masks `identifier_for__item_stack` with `UUID_MASK__INVENTORY__ITEM_STACK` (`MASK(6) << 26`), which isolates bits 26–31 — the 6-bit field reserved for the item-stack index.
2. Right-shifts the masked value by `UUID_BIT_SHIFT__INVENTORY__ITEM_STACK` (26), producing the raw index.
3. Returns `&p_inventory->items[index]`, giving direct access to the item stack at that index.

This is the inverse of `set_inventory_uuid__item_stack_index` (defined in `inventory.h`), which stores a 6-bit index into bits 26–31 of a UUID. The encoding and decoding are symmetric and correct.

## Implementation Correctness

- **Type compatibility:** `identifier_for__item_stack` is `Identifier__u32` (`uint32_t`). The mask and shift operations are performed on `uint32_t` values, and the result is used as an array index for `items[]` (typed as `Item_Stack[]`). No implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic, no null dereference (the function dereferences `p_inventory` only after the caller guarantees it is non-null), no type punning, and no out-of-bounds access (assuming the caller provides a valid identifier). The function does not perform bounds checking, but this is consistent with the codebase's pattern for low-level accessors (e.g., `get_p_item_stack_from__inventory_by__index`).
- **Validation:** No validation is performed, which is appropriate for this low-level accessor function. The caller is responsible for providing a valid `p_inventory` pointer and a well-formed `identifier_for__item_stack`. Higher-level functions (e.g., `add_item_to__inventory`, `remove_p_item_stack_from__inventory`) perform debug-mode null and bounds checks before reaching this accessor.

## Side Effects

No side effects. The function is pure: it reads the `identifier_for__item_stack` parameter (a local copy), reads the `items` array pointer from `p_inventory`, and returns a pointer into that array. No memory is written, no state is mutated.
