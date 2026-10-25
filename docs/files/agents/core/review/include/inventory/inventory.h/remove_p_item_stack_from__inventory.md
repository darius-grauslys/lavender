remove_p_item_stack_from__inventory — core/source/inventory/inventory.c

Removes a specific item stack from the inventory by resetting it to an empty state and decrementing the inventory's item stack count.

Pre-conditions:
1. p_inventory must be a non-null pointer to a valid Inventory object (checked in debug builds via debug_abort).
2. p_item_stack must be a non-null pointer to a valid Item_Stack object (checked in debug builds via debug_abort).
3. p_item_stack must point to an element within the p_inventory->items array, i.e. it must be one of the item stacks owned by this inventory (checked in debug builds via pointer arithmetic against INVENTORY_ITEM_MAXIMUM_QUANTITY_OF).
4. p_item_stack should be a currently-occupied (non-empty) item stack slot; the caller is responsible for ensuring this, as the function does not verify emptiness before decrementing quantity_of__item_stacks.

Post-conditions:
1. The Item_Stack at p_item_stack is reset to its initial/empty state via initialize_item_stack_as__empty, preserving the existing UUID. Under Lavender semantics, "initialization" here means cleaning the struct to default conditions (not RAII resource acquisition).
2. p_inventory->quantity_of__item_stacks is decremented by exactly 1.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of removing an item stack from the inventory. The function delegates to initialize_item_stack_as__empty, which is the Lavender-style initialization (pool cleanup / reset to default state) rather than RAII. The UUID of the item stack is preserved during the reset, which is the correct behavior for maintaining identity within the inventory's serialization scheme. The quantity_of__item_stacks counter is decremented to reflect the removal, keeping it in sync with the actual number of occupied item stack slots.

Implementation Correctness:
Type compatibility — p_item_stack - p_inventory->items yields a ptrdiff_t (signed), and the comparison >= INVENTORY_ITEM_MAXIMUM_QUANTITY_OF (an int literal, 27) is well-defined. The debug check correctly catches pointers that are at or beyond the end of the items array (index >= 27). No implicit conversions or truncation occur in the core logic.
Undefined behavior — no undefined behavior in the release build. In debug builds, the pointer arithmetic check only validates that p_item_stack is not beyond the end of the array; it does not guard against p_item_stack pointing before the start of the array (a negative ptrdiff_t would pass the >= check). This is a minor debug-only validation gap, not a release-build correctness issue. The actual pointer dereference and call to initialize_item_stack_as__empty rely on the caller's contract.
Validation — the debug-mode null checks and pointer containment check are appropriate for this function's role as a low-level inventory mutation primitive. The decision not to check for underflow of quantity_of__item_stacks (e.g., when it is already 0) is acceptable as this is the caller's responsibility; the function is only called when removing a previously-counted item stack.

Side Effects:
1. Mutates the Item_Stack struct at p_item_stack, resetting it to an empty state (item set to empty, quantity_of__items and max_quantity_of__items set to 0, serialization header reinitialized with the preserved UUID).
2. Mutates p_inventory->quantity_of__item_stacks by decrementing it by 1.
