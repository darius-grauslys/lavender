set_item_stack_allocation_specifier_as__allocated — core/include/inventory/item_stack_allocation_specifier.h, lines 34-40

## 1. Header
- **Function name:** `set_item_stack_allocation_specifier_as__allocated`
- **File of origin:** `core/include/inventory/item_stack_allocation_specifier.h`

## 2. Semantic
Sets the `is_item_stack_allocation_specifier__allocated` bitfield member of an `Item_Stack_Allocation_Specifier` struct to `true`, marking the specifier as allocated.

## 3. Pre-conditions
- `p_item_stack_allocation_specifier` must be a non-null pointer to a valid `Item_Stack_Allocation_Specifier` struct instance.
- The struct must be in a valid memory state (properly initialized or at least allocated in memory).

## 4. Post-conditions
- After the function returns, the `is_item_stack_allocation_specifier__allocated` member of the struct pointed to by `p_item_stack_allocation_specifier` is guaranteed to be `true`.
- No other members of the struct are modified.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The implementation fulfills its semantic intent. The function name clearly indicates it sets the allocation specifier as allocated, and the implementation sets the `is_item_stack_allocation_specifier__allocated` field to `true`. This aligns with the Lavender engine's pattern where "allocated" means the specifier is in use (as opposed to "deallocated" or "empty" which means it is cleared/reset to default state for pool reuse).

## 7. Implementation Correctness
- **Type compatibility:** The parameter `p_item_stack_allocation_specifier` is of type `Item_Stack_Allocation_Specifier *`, and the struct field `is_item_stack_allocation_specifier__allocated` is of type `bool` (1-bit bitfield). The assignment `= true` is type-compatible.
- **Undefined behavior:** No undefined behavior is present. The pointer is dereferenced and a single bitfield member is assigned. There is no out-of-bounds access, no null dereference (caller's responsibility to provide valid pointer), and no type punning.
- **Validation:** No validation is performed within the function. This is consistent with the Lavender engine's approach for simple inline setters — validation (or the assumption of valid input) is the caller's responsibility.

## 8. Side Effects
- Mutates the `is_item_stack_allocation_specifier__allocated` member of the struct pointed to by `p_item_stack_allocation_specifier`, setting it to `true`.
- No other side effects.
