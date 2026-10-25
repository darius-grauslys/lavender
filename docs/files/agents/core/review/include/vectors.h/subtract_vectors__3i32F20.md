# Function Review: subtract_vectors__3i32F20

## 1. Header
- **Function name:** `subtract_vectors__3i32F20`
- **File of origin:** `core/include/vectors.h`

## 2. Semantic
Subtracts `vector_two` from `vector_one` component-wise, returning a new `Vector__3i32F20` whose `x`, `y`, and `z` fields are the respective differences of the input vectors' fields.

## 3. Pre-conditions
1. Both `vector_one` and `vector_two` are valid `Vector__3i32F20` values passed by value (no null-pointer or validity concerns).
2. Each field (`x__i32F20`, `y__i32F20`, `z__i32F20`) is of type `i32F20` (i.e., `int32_t`); no range constraints are imposed by the function.

## 4. Post-conditions
1. Returns a new `Vector__3i32F20` struct where:
   - `.x__i32F20 = vector_one.x__i32F20 - vector_two.x__i32F20`
   - `.y__i32F20 = vector_one.y__i32F20 - vector_two.y__i32F20`
   - `.z__i32F20 = vector_one.z__i32F20 - vector_two.z__i32F20`
2. The input vectors (`vector_one` and `vector_two`) are not modified, as they are passed by value.

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation fulfills the semantic intent of vector subtraction. All three components (x, y, z) are computed as the difference between corresponding fields of `vector_one` and `vector_two`. The struct initializer lists all three fields in the correct order matching the `Vector__3i32F20` struct definition (`x__i32F20`, `y__i32F20`, `z__i32F20`). No fields are omitted or reordered.

## 7. Implementation Correctness
- **Type compatibility:** Parameters are `Vector__3i32F20` structs whose fields are `i32F20` (`int32_t`). The subtraction `i32F20 - i32F20` yields `int32_t`, which matches the field type exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** None. There is no pointer arithmetic, no null dereference (parameters are passed by value, not by pointer), no type punning, and no out-of-bounds access.
- **Validation:** No validation is needed. The function operates on plain value-type structs and performs straightforward arithmetic. Validation is not the responsibility of this helper.

## 8. Side Effects
No side effects. The function takes both parameters by value, performs pure arithmetic, and returns a new `Vector__3i32F20` without modifying any input or external state.
