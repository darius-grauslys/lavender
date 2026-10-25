# remove_quantity_of_items_from__item_stack

**File of origin:** `core/source/inventory/item_stack.c`

## Semantic

Removes a specified quantity of items from an `Item_Stack`, clamping to zero if the
requested removal exceeds the available quantity. If the stack is emptied, the item
is reset to the empty item. Returns the quantity of items that could not be removed
(the shortfall).

## Pre-conditions

1. `p_item_stack` must be non-null. (In debug builds, a null pointer triggers
   `debug_abort` and the function returns early with the full requested quantity as
   the shortfall. In release builds, the caller is responsible for ensuring non-null.)
2. `quantity_of__items_to__remove` is a `Quantity__u8` (u8), so its valid range is
   0–255. No upper-bound validation against `max_quantity_of__items` is performed;
   the caller is responsible for any such constraint.
3. The `Item_Stack` must have been previously initialized (i.e., its fields are in a
   consistent state).

## Post-conditions

1. `p_item_stack->quantity_of__items` is reduced by `quantity_of__items_to__remove`,
   clamped to a minimum of 0 via `subtract_u8__no_overflow`. If the original quantity
   was less than the requested removal, the result is 0.
2. If `p_item_stack->quantity_of__items` becomes 0, `p_item_stack->item` is set to
   `get_item__empty()` (the empty item template).
3. The return value (`Quantity__u32`) is the number of items that could not be removed
   — i.e., `quantity_of__items_to__remove - original_quantity` when the original
   quantity was less than the requested removal, or 0 otherwise.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent described by the doc comment
("Returns the amount of items not removed"). The return value represents the shortfall
— the quantity that was requested for removal but could not be removed because the stack
did not contain enough items. This is consistent with the inline variable name
`quantity_of__items_remaining_to__remove`.

The mutation logic is sound:
- `subtract_u8__no_overflow` safely handles the case where more items are requested
  than available (returns 0 instead of underflowing).
- The empty-item reset on zero quantity is consistent with `initialize_item_stack_as__empty`
  and the `is_p_item_stack__empty` inline helper.

## Implementation Correctness

- **Type compatibility:** `p_item_stack->quantity_of__items` is `Quantity__u8` (u8),
  and `quantity_of__items_to__remove` is `Quantity__u8` (u8). The call to
  `subtract_u8__no_overflow(u8, u8)` matches the field type exactly — no implicit
  truncation or conversion. The return type `Quantity__u32` (u32) is consistent with
  the `get_quantity_of__items_in__item_stack` return type and the doc comment.
- **Comparison safety:** In the ternary condition,
  `get_quantity_of__items_in__item_stack(p_item_stack)` (u32) is compared with
  `quantity_of__items_to__remove` (u8). The u8 is promoted to u32, which is safe.
- **Subtraction safety:** In the ternary's true branch,
  `quantity_of__items_to__remove - quantity_of__items_in__item_stack` is computed in
  u32 arithmetic. Since the condition guarantees `quantity_of__items_to__remove >
  quantity_of__items_in__item_stack`, no underflow occurs.
- **Undefined behavior:** No null dereference (debug-checked), no out-of-bounds access,
  no type punning.
- **Validation:** The null-pointer check is appropriate and consistent with the
  codebase-wide pattern (debug-only guard via `#ifndef NDEBUG`).
- **Minor code-quality note:** The ternary condition redundantly calls
  `get_quantity_of__items_in__item_stack(p_item_stack)` instead of reusing the
  already-computed local variable `quantity_of__items_in__item_stack`. This is
  harmless (the value is unchanged between calls) but is a redundant invocation.

## Side Effects

- Mutates `p_item_stack->quantity_of__items` (decreased by the requested removal,
  clamped to 0).
- If the resulting quantity is 0, mutates `p_item_stack->item` to the empty item
  (via `get_item__empty()`).
- Does not modify `_serialization_header` or `max_quantity_of__items`.
