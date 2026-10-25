add_item_to__inventory — core/source/inventory/inventory.c

Attempts to add a quantity of a given item to an inventory by first searching for an existing non-full stack of the same item kind; if none is found (or all such stacks are full), it falls back to placing the item in the first empty (Item_Kind__None) stack. Aborts if the inventory is full.

Pre-conditions:
1. p_inventory must be a non-null pointer to a valid Inventory object (checked in debug builds via debug_abort).
2. item may be any valid Item; its the_kind_of_item__this_item_is field determines which stacks are searched.
3. quantity_of__items is a Quantity__u8 (uint8_t); any value is accepted (will be clamped to max_quantity_of__items).
4. max_quantity_of__items is a Quantity__u8 (uint8_t); any value is accepted. If adding to an existing non-empty stack, the effective max becomes max(provided, existing_stack.max_quantity_of__items).

Post-conditions:
1. Returns a pointer to the Item_Stack that was mutated, or null (0) if the inventory is full (only in debug builds — debug_abort is called before returning).
2. If an existing non-full stack of the same item kind was found: that stack's item, quantity_of__items, and max_quantity_of__items are updated via set_item_stack. The quantity is clamped to the effective max.
3. If no suitable existing stack was found and an empty stack (Item_Kind__None) was located: that stack is populated with the new item, quantity, and max via set_item_stack.
4. p_inventory->quantity_of__item_stacks is NOT incremented when a new empty stack is occupied — this is a BUG (see Implementation Correctness).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation attempts to fulfill the semantic intent of adding items to an inventory with stack merging. The core logic of finding existing stacks of the same kind, skipping full stacks, falling back to empty stacks, and clamping quantities is sound. However, there is a critical omission: the function does not maintain the inventory's quantity_of__item_stacks counter. When the function places an item into a previously empty stack (Item_Kind__None), it should increment p_inventory->quantity_of__item_stacks to reflect that a new stack is now occupied. This is consistent with how copy_p_item_stack_to__inventory (which delegates to get_next_available_item_stack_in__inventory) and remove_p_item_stack_from__inventory handle this counter. The existing count is used by does_inventory_have__available_item_stacks() and by deserialize_inventory, so leaving it stale causes those systems to report incorrect state.

The docstring is also inaccurate: it states "Calls initialize_item_stack to an empty spot" but the function actually calls set_item_stack, and it states "Does nothing if the inventory is already full" but the function actually calls debug_abort and returns null.

Implementation Correctness:
Type compatibility — The parameters quantity_of__items and max_quantity_of__items are Quantity__u8 (uint8_t), which are widened to Quantity__u32 (uint32_t) when passed to set_item_stack. This is a safe widening conversion with no truncation. The max__u8 and clamp__u8 calls operate on u8 values consistently.

Undefined behavior — No null pointer dereference, out-of-bounds access, or type punning within the function itself. The null check for p_inventory is present in debug builds.

Validation — The null check for p_inventory is appropriate for a debug build. The inventory-full case calls debug_abort, which is consistent with the codebase's pattern for unrecoverable errors.

BUG: Missing increment of p_inventory->quantity_of__item_stacks. When add_item_to__inventory finds an empty stack (Item_Kind__None) and populates it with a new item kind, p_inventory->quantity_of__item_stacks is not incremented. This causes the inventory's occupied-stack count to remain stale, which breaks does_inventory_have__available_item_stacks() (it will continue to report available slots even when stacks are occupied) and any serialization/deserialization logic that relies on this count. The fix is to add p_inventory->quantity_of__item_stacks++ after successfully locating an empty stack in the fallback path (the if (!p_item_stack) block), consistent with how get_next_available_item_stack_in__inventory handles it.

Side Effects:
Mutates the Item_Stack pointed to by the return value (via set_item_stack, which writes item, quantity_of__items, and max_quantity_of__items). Does not mutate p_inventory->quantity_of__item_stacks (this is the bug). May call debug_abort, which terminates the program, if p_inventory is null (debug builds only) or if the inventory is full (all builds).
