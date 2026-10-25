# is_chunk_vectors_3i32__equal

**File of origin:** `core/include/vectors.h`

## Semantic

Compares two `Chunk_Vector__3i32` values for equality by delegating to `is_vectors_3i32__equal`, which performs a component-wise comparison of the x, y, and z fields. Returns `true` if all three components match, `false` otherwise.

## Pre-conditions

1. `vector_1` and `vector_2` are valid `Chunk_Vector__3i32` values. Both are passed by value, so no null-pointer constraint applies.
2. The `Chunk_Vector__3i32` and `Vector__3i32` types are both typedefs for the same underlying struct `Vector__3i32_t` (defined in `core/include/defines_weak.h`, lines 107 and 118–122). Therefore passing `Chunk_Vector__3i32` arguments to `is_vectors_3i32__equal` (which expects `Vector__3i32`) is type-safe with no implicit conversion, truncation, or type mismatch.

## Post-conditions

1. Returns `bool`: `true` if `vector_1.x__i32 == vector_2.x__i32`, `vector_1.y__i32 == vector_2.y__i32`, and `vector_1.z__i32 == vector_2.z__i32`; `false` otherwise.
2. Neither input is modified (both are passed by value).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. The function correctly delegates to `is_vectors_3i32__equal`, which compares all three components (x, y, z) of the vectors. Since `Chunk_Vector__3i32` and `Vector__3i32` are the same underlying type, the delegation is semantically and type-correct. No fields are omitted, no reordering occurs, and the comparison logic is sound.

## Implementation Correctness

1. **Type compatibility:** `Chunk_Vector__3i32` and `Vector__3i32` are both typedefs for `struct Vector__3i32_t`. Passing `Chunk_Vector__3i32` values to a function expecting `Vector__3i32` involves no implicit conversion, truncation, or type mismatch.
2. **Undefined behavior:** No pointer arithmetic, no null dereference (parameters are by value), no type punning, no out-of-bounds access.
3. **Validation:** No validation is needed — the function receives values by value and performs a straightforward equality comparison. Validation of vector contents (if any) is the caller's responsibility.

## Side Effects

No side effects. The function is a pure function: it reads its arguments (passed by value) and returns a `bool` result without modifying any state.
