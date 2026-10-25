move_p_item_stack_to__inventory — core/source/inventory/inventory.c, lines 311-320

Routes parameters to struct internals.

Pre-conditions:
1. p_inventory must be a non-null pointer to a writable Inventory object that has been previously initialized (via initialize_inventory or initialize_inventory_as__empty).
2. p_item_stack__move_origin must be a non-null pointer to a writable Item_Stack object. The origin is presumed to reside outside the inventory's items[] array (i.e., it is not one of the inventory's own slots). If it is inside the inventory, the quantity_of__item_stacks counter will be corrupted.
3. p_item_stack__move_origin must contain valid data (a non-empty item stack) to be meaningfully "moved." An empty origin is a no-op in terms of game state but still clears the origin.

Post-conditions:
1. On success: the item stack data (item, quantity_of__items, max_quantity_of__items) is copied into the first available (empty) slot in p_inventory->items[], and p_inventory->quantity_of__item_stacks is incremented by 1.
2. On success: p_item_stack__move_origin is reset to its initial/empty state (item set to get_item__empty(), quantity_of__items = 0, max_quantity_of__items = 0), with its original uuid preserved.
3. On failure (inventory full): NO post-conditions are guaranteed — see Correctness Verdict.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to perform a "move" operation: transfer an item stack from an external origin into the inventory, leaving the origin empty. The implementation attempts this by composing two sub-operations: a copy (copy_p_item_stack_to__inventory) followed by an initialization to empty (initialize_item_stack_as__empty).

The copy step correctly copies only the item, quantity, and max_quantity fields (via copy_item_stack → set_item_stack), leaving the destination's uuid intact (the destination slot already has its own uuid set during inventory initialization). The origin is then correctly cleared with its uuid preserved.

However, the implementation does NOT fulfill the semantic intent in the failure case. When the inventory is full, copy_p_item_stack_to__inventory silently returns without copying (after issuing a debug_warning), but move_p_item_stack_to__inventory unconditionally proceeds to clear the origin. This violates the move semantic: the origin is destroyed without the data being successfully relocated, resulting in permanent item loss.

Implementation Correctness:
- Type compatibility: All parameter types match exactly. p_inventory is Inventory*, p_item_stack__move_origin is Item_Stack*, and the uuid field is Identifier__u32, matching the parameter type of initialize_item_stack_as__empty. No implicit conversions or truncation.
- Undefined behavior: No pointer arithmetic, no type punning, no out-of-bounds access within the function itself. However, if p_item_stack__move_origin is null and the inventory has an available slot, copy_p_item_stack_to__inventory → copy_item_stack → set_item_stack dereferences the null source pointer when reading p_item_stack__source->item, quantity_of__items, and max_quantity_of__items. set_item_stack only validates the destination pointer (p_item_stack), not the source fields being read.
- Validation: No null validation is performed on either p_inventory or p_item_stack__move_origin. This is inconsistent with sibling functions add_item_to__inventory (lines 253-259) and remove_p_item_stack_from__inventory (lines 322-333), which both include #ifndef NDEBUG null checks. The lack of validation is a defensive programming gap.
- Critical bug: copy_p_item_stack_to__inventory is void and provides no success/failure signal to the caller. move_p_item_stack_to__inventory cannot determine whether the copy succeeded before clearing the origin. When the inventory is full, the item is irretrievably lost.

Side Effects:
1. Mutates p_inventory: increments p_inventory->quantity_of__item_stacks by 1 and copies item stack data into the first available empty slot in p_inventory->items[].
2. Mutates p_item_stack__move_origin: resets it to an empty state (item = get_item__empty(), quantity_of__items = 0, max_quantity_of__items = 0), preserving its original uuid via initialize_serialization_header.
3. If the inventory is full: the origin is still cleared (side effect #2 occurs) but no data is added to the inventory (side effect #1 does not occur), resulting in item loss.
