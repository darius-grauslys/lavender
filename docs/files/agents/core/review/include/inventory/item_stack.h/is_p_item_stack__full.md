is_p_item_stack__full — core/include/inventory/item_stack.h

Returns true if the item stack's current quantity equals its maximum quantity, indicating the stack is at full capacity.

Pre-conditions:
1. p_item_stack must be a non-null pointer to a valid Item_Stack struct.
2. The Item_Stack struct fields quantity_of__items and max_quantity_of__items must be initialized (both are Quantity__u8).

Post-conditions:
1. Returns true if quantity_of__items == max_quantity_of__items, false otherwise.
2. No mutation of the Item_Stack struct occurs; the function is read-only.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to determine whether an item stack is at full capacity. However, the implementation has a semantic bug: it does not check whether the item stack actually contains a valid (non-empty) item before comparing quantities. When an Item_Stack is initialized as empty via initialize_item_stack_as__empty(), both quantity_of__items and max_quantity_of__items are set to 0. In this state, the equality check (0 == 0) returns true, incorrectly reporting an empty stack as "full."

The sibling function is_p_item_stack___full (triple underscore, which checks whether the stack is NOT yet full / can accept more items) correctly guards with !is_p_item__empty(&p_item_stack->item) before performing its comparison. The is_p_item_stack__empty function also correctly checks both quantity == 0 and is_p_item__empty. The absence of this guard in is_p_item_stack__full is inconsistent with these sibling functions and causes a semantic failure: an empty item stack is reported as full.

Implementation Correctness:
Type compatibility — both quantity_of__items and max_quantity_of__items are Quantity__u8, so the equality comparison is type-safe with no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access. The function dereferences p_item_stack without a null check, but this is consistent with the codebase pattern where null validation is the caller's responsibility (see resolve_item_stack__merge_or_swap and merge_p_item_stacks which guard with #ifndef NDEBUG).
The bug is a semantic correctness issue rather than a type or UB issue: the function fails to exclude the empty-stack case from its "full" determination.

Side Effects:
No side effects — the function is pure and only reads from the pointed-to Item_Stack struct.
