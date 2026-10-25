initialize_item_stack_as__empty — core/source/inventory/item_stack.c

Resets an Item_Stack to its empty/default state by clearing all fields, including the serialization header, item, quantity, and max quantity.

Pre-conditions:
1. p_item_stack must be a non-null pointer to a writable Item_Stack object (checked in debug builds via debug_abort; in release builds this is the caller's responsibility).
2. identifier_for__item_stack__u32 is any Identifier__u32 value (u32); no range constraint is imposed.

Post-conditions:
1. p_item_stack is mutated such that _serialization_header.uuid is set to identifier_for__item_stack__u32 and _serialization_header.size_of__struct is set to sizeof(Item_Stack).
2. p_item_stack->item is set to the empty item (all fields zeroed, Item_Kind == Item_Kind__None) via get_item__empty().
3. p_item_stack->quantity_of__items is set to 0.
4. p_item_stack->max_quantity_of__items is set to 0.

Correctness Verdict: Correct

Semantic Alignment:
This function performs Lavender-style initialization (pool cleanup), not RAII. It does not acquire any resources — it clears the struct to its initial conditions so it can be returned to a free pool or reused. This is confirmed by its usage in merge_p_item_stacks, where it is called to reset a source stack after its items are exhausted.

All four struct fields of Item_Stack are assigned — _serialization_header, item, quantity_of__items, and max_quantity_of__items. No member is omitted, no reordering occurs. The semantic intent of "empty" is fully realized: the item is set to the empty item template, and both quantity fields are zeroed.

Implementation Correctness:
Type compatibility — identifier_for__item_stack__u32 (Identifier__u32 / u32) matches the parameter type of initialize_serialization_header exactly. sizeof(Item_Stack) (size_t) is passed as Quantity__u32 (u32); this is safe as sizeof results fit within u32 on all supported platforms. get_item__empty() returns Item, assigned to the item field of type Item — exact match. The integer literal 0 assigned to Quantity__u8 fields fits without truncation.

Undefined behavior — no pointer arithmetic, no null dereference (null is checked in debug), no type punning, no out-of-bounds access. The null check uses debug_abort which may not halt in all configurations, but the return after the abort prevents further dereference in debug mode.

Validation — the null pointer check is appropriate for this low-level struct initialization function. The caller is responsible for ensuring the pointer is valid in release builds, consistent with the Lavender engine's pattern for similar initialization functions.

Side Effects:
Mutates the Item_Stack struct pointed to by p_item_stack. Calls initialize_serialization_header (writes to the serialization header sub-struct) and get_item__empty() (a pure function returning a static const Item with all-zero fields). No I/O, no global state mutation, no memory allocation.

Note: The debug error message string says "initialize_item_stack__as_allocated" rather than "initialize_item_stack_as__empty", which is a minor naming inconsistency in the diagnostic message but does not affect functional correctness.
