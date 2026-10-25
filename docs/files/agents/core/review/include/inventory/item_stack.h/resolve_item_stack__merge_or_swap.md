resolve_item_stack__merge_or_swap — core/source/inventory/item_stack.c, lines 231-276

Conditionally merges or swaps two Item_Stacks based on whether they hold the same Item_Kind. If the item kinds match, the source stack's items are merged into the destination stack (delegating to merge_p_item_stacks). If the item kinds differ, the data contents of the two stacks are swapped while each stack retains its own UUID. Returns true only if a swap occurred; returns false if a merge occurred (or if a null pointer was detected in debug builds).

Pre-conditions:
1. p_item_stack__source must be a non-null pointer to a valid, initialized Item_Stack. (Null is only checked in debug builds via #ifndef NDEBUG; in release builds the caller is responsible.)
2. p_item_stack__destination must be a non-null pointer to a valid, initialized Item_Stack. (Same debug-only null check as above.)
3. Both Item_Stacks must have been initialized via initialize_item_stack or initialize_item_stack_as__empty (or equivalent), so that their _serialization_header, item, quantity_of__items, and max_quantity_of__items fields are in a consistent state.
4. The caller must ensure that p_item_stack__source and p_item_stack__destination do not alias the same Item_Stack (self-reference is undefined; if they point to the same struct, the merge path would double-count items).

Post-conditions:
1. If both stacks share the same Item_Kind (is_p_item_stacks_the_same__item_kind returns true):
   a. p_item_stack__destination->quantity_of__items is set to add_u8__clamped(dest_qty, source_qty, dest_max), i.e., the destination is filled up to its max capacity.
   b. p_item_stack__source->quantity_of__items is reduced by the amount that overflowed past the destination's max; if the source reaches 0, it is reinitialized as empty via initialize_item_stack_as__empty, preserving its original UUID.
   c. The return value is false (no swap occurred).
2. If the stacks have different Item_Kinds:
   a. p_item_stack__source receives the item, quantity_of__items, and max_quantity_of__items from p_item_stack__destination, but retains its own original UUID.
   b. p_item_stack__destination receives the item, quantity_of__items, and max_quantity_of__items from p_item_stack__source, but retains its own original UUID.
   c. The return value is true (a swap occurred).
3. In all cases, both stacks' _serialization_header.uuid fields are preserved (unchanged from their pre-call values).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its documented semantic intent: "If the Item_Stacks are for the same Item_Kind then merge. Otherwise swap." The merge path delegates to merge_p_item_stacks, which correctly handles overflow by clamping the destination and leaving the remainder in the source. The swap path exchanges the item data (Item, quantity_of__items, max_quantity_of__items, and size_of__struct) between the two stacks while preserving each stack's UUID.

The swap logic, traced step-by-step:
1. tmp = *source (saves source's full state including uuid=S)
2. *source = *destination (source now has destination's data including uuid=D)
3. source->uuid = tmp.uuid (restores source's uuid to S; source now has destination's data + source's uuid)
4. tmp.uuid = destination->uuid (destination is unmodified at this point, so uuid=D; tmp now has source's data + destination's uuid)
5. *destination = tmp (destination now has source's data + destination's uuid)
6. destination->uuid = destination->uuid (redundant no-op; uuid is already correct)

The final line (step 6) is a self-assignment that has no effect — it assigns a value to itself. This is dead code, likely a leftover from a refactoring or a mistaken attempt to "fix" the uuid. It does not cause any incorrect behavior.

Implementation Correctness:
Type compatibility — all field accesses use the correct types. Item_Stack p_item_stack__tmp is a stack copy of the correct type. The uuid field is Identifier__u32, and the assignments are between Identifier__u32 values with no implicit conversions or truncation.
Undefined behavior — no null dereference (checked in debug), no broken pointer arithmetic, no type punning, no out-of-bounds access. The struct copy via *p_item_stack__source = *p_item_stack__destination is safe for non-aliasing pointers.
Validation — null checks are debug-only (#ifndef NDEBUG), consistent with the codebase pattern. The function does not validate that the stacks are non-empty or that quantities are within bounds; this is the caller's responsibility, consistent with the low-level nature of the function.
Note: The delegated merge_p_item_stacks function has a minor theoretical concern where quantity_of__items_overflowed (a u8) could truncate if max_quantity_of__items is 0 while the destination has a non-zero quantity (an inconsistent state). In normal operation where quantity_of__items <= max_quantity_of__items, the overflow value is always <= source_qty (max 255) and fits in u8. This is not a bug in resolve_item_stack__merge_or_swap itself.

Side Effects:
Mutates both p_item_stack__source and p_item_stack__destination in place. In the swap path, all data fields (item, quantity_of__items, max_quantity_of__items, _serialization_header.size_of__struct) are exchanged while UUIDs are preserved. In the merge path, the destination's quantity is increased (clamped to max) and the source's quantity is decreased (potentially to 0, triggering reinitialization as empty). The function also calls merge_p_item_stacks and initialize_item_stack_as__empty as internal implementation details.
