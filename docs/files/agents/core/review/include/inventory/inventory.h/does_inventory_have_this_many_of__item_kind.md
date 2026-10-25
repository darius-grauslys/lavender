# does_inventory_have_this_many_of__item_kind

**File of origin:** `core/source/inventory/inventory.c`

## Semantic

Queries whether the inventory contains at least `quantity_of__items` worth of the specified `Item_Kind` by accumulating the `quantity_of__items` field across all matching `Item_Stack` entries. Returns `true` if the accumulated total meets or exceeds the requested quantity; otherwise returns `false`.

## Pre-conditions

1. `p_inventory` must be a non-null pointer to a valid, initialized `Inventory` struct. (No null check is performed inside the function; this is consistent with the codebase convention for inventory query functions such as `is_inventory__empty` and `does_inventory_have__available_item_stacks`.)
2. `the_kind_of__item` must be a valid `enum Item_Kind` value.
3. `quantity_of__items` is a `Quantity__u32` (uint32_t); any value in range is acceptable, including 0.

## Post-conditions

1. Returns `true` if the sum of `quantity_of__items` across all `Item_Stack` entries of the specified `Item_Kind` is greater than or equal to `quantity_of__items`.
2. Returns `false` if no matching `Item_Stack` entries exist or the accumulated total is less than `quantity_of__items`.
3. If no `Item_Stack` of the specified kind is found, returns `true` only when `quantity_of__items == 0` (i.e., the inventory "has" zero items of that kind trivially).
4. The `Inventory` and all `Item_Stack` entries remain unmodified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills the semantic intent of querying whether the inventory has a sufficient quantity of a given item kind. The function iterates through all item stacks matching the specified `Item_Kind` (using `get_first_p_item_stack_of__this_item_kind_from__inventory` and `get_next_p_item_stack_of__this_item_kind_from__inventory`), accumulating `quantity_of__items` from each stack into a `Quantity__u32` accumulator. The early-exit check (`total_quantity >= quantity_of__items`) correctly short-circuits as soon as the threshold is met. The early return when no matching stack exists (`return quantity_of__items == 0`) correctly handles the edge case where the requested quantity is zero.

## Implementation Correctness

- **Type compatibility:** `Item_Stack.quantity_of__items` is `Quantity__u8` (uint8_t), while `total_quantity` is `Quantity__u32` (uint32_t). The accumulation `total_quantity += p_item_stack->quantity_of__items` is safe — the uint8_t value is implicitly promoted to uint32_t before addition. The comparison `total_quantity >= quantity_of__items` compares two `Quantity__u32` values, which is correct.
- **Undefined behavior:** No undefined behavior is present. No null dereference (beyond the documented pre-condition), no out-of-bounds array access, no type punning.
- **Loop structure:** The `do-while` loop is appropriate here. `get_first_p_item_stack_of__this_item_kind_from__inventory` is called first and its result is checked for null before entering the loop, so the do-while body is guaranteed to execute at least once with a valid `p_item_stack`. The loop then calls `get_next_p_item_stack_of__this_item_kind_from__inventory` to advance to the next matching stack, terminating when that function returns null.
- **Validation:** No input validation is performed beyond the early null check on `p_item_stack`. This is consistent with the function's role as a query function — validation of `p_inventory` is the caller's responsibility, matching the pattern used by other inventory query functions.

## Side Effects

No side effects. This is a pure query function — it does not modify the `Inventory`, any `Item_Stack`, or any global state.
