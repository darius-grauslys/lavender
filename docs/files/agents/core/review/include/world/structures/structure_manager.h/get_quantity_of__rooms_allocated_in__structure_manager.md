# get_quantity_of__rooms_allocated_in__structure_manager

**File of origin:** `core/include/world/structures/structure_manager.h`

## Semantic

Returns the current count of rooms that have been allocated within the given `Structure_Manager`.

## Pre-conditions

1. `p_structure_manager` must be a non-null pointer to a valid `Structure_Manager` instance.
2. The `Structure_Manager` must have been initialized (via `initialize_structure_manager`) before this function is called.

## Post-conditions

1. Returns a `Quantity__u32` value representing the number of rooms currently allocated in the `Structure_Manager`.
2. The returned value is a copy; the original `quantity_of__allocated_rooms` field is not modified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation directly returns the `quantity_of__allocated_rooms` field of the `Structure_Manager` struct. This aligns with the semantic intent of the function name, which is to retrieve the count of allocated rooms. There is no computation or transformation involved, so the implementation matches its intent.

## Implementation Correctness

- **Type compatibility:** The parameter `p_structure_manager` is of type `Structure_Manager *`, which matches the struct definition. The field `quantity_of__allocated_rooms` is of type `Quantity__u32`, and the return type is also `Quantity__u32`, so no implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic, null dereference, or out-of-bounds access occurs. The function dereferences `p_structure_manager` to access a struct field, which is safe as long as the pre-condition (non-null pointer) is met.
- **Validation:** This is a simple inline accessor function. Validation of the pointer is the caller's responsibility, consistent with typical performance-sensitive inline getter patterns.

## Side Effects

No side effects. This is a pure accessor function that reads and returns the value of `quantity_of__allocated_rooms`.