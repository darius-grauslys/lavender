# is_vectors_3i32F4__equal

**File of origin:** `core/include/vectors.h`

## Semantic

Compares two `Vector__3i32F4` values component-wise (x, y, z) and returns `true` if all three components are equal, `false` otherwise.

## Pre-conditions

1. Both `vector_1` and `vector_2` are valid `Vector__3i32F4` structs passed by value. Since they are passed by value (not by pointer), no null-check is required.
2. No other constraints — the struct contains three `i32F4` fields with no internal pointers or external resources to validate.

## Post-conditions

1. Returns `true` if and only if `vector_1.x__i32F4 == vector_2.x__i32F4`, `vector_1.y__i32F4 == vector_2.y__i32F4`, and `vector_1.z__i32F4 == vector_2.z__i32F4`.
2. Returns `false` if any single component differs.
3. Neither input vector is modified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of equality comparison between two `Vector__3i32F4` values. It checks all three components (x, y, z) for exact equality using the `==` operator, which is appropriate for `i32F4` (a typedef for `int32_t`) — a fixed-width signed integer type. The logic is consistent with the sibling functions `is_vectors_3i32__equal`, `is_vectors_3i16F8__equal`, and `is_vectors_3i32F20__equal` in the same file, all of which follow the same pattern of comparing each component independently.

## Implementation Correctness

- **Type compatibility:** The parameters are `Vector__3i32F4` structs passed by value, matching the type definition in `defines_weak.h`. The fields `x__i32F4`, `y__i32F4`, and `z__i32F4` are of type `i32F4` (typedef for `int32_t`). The `==` operator is well-defined for `int32_t`. No implicit conversions or truncation occur.
- **Undefined behavior:** None. No pointer dereference, no array indexing, no type punning, no arithmetic overflow risk. The function operates entirely on value parameters and direct field access.
- **Validation:** No validation is needed for this function's role. It is a pure comparison utility with no external dependencies or resource handling. Validation of input validity is the caller's responsibility, if needed.

## Side Effects

No side effects. This is a pure function — it reads only its value parameters and returns a boolean result without modifying any state.
