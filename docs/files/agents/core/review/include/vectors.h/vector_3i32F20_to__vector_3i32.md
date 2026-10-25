# Function Review: vector_3i32F20_to__vector_3i32

## File of Origin
`core/include/vectors.h` (lines 296–304)

## Semantic
Converts a 3-component fixed-point vector with 20 fractional bits (`Vector__3i32F20`) to a 3-component plain integer vector (`Vector__3i32`) by applying the `i32F20_to__i32` arithmetic right-shift conversion to each component (x, y, z).

## Pre-conditions
1. The parameter `vector` is passed by value, so no null-pointer dereference risk applies.
2. Each field of `vector` (`x__i32F20`, `y__i32F20`, `z__i32F20`) is of type `i32F20` (i.e., `int32_t`), which is the expected input type for `i32F20_to__i32`.

## Post-conditions
1. Returns a `Vector__3i32` value where:
   - `result.x__i32` = `i32F20_to__i32(vector.x__i32F20)`
   - `result.y__i32` = `i32F20_to__i32(vector.y__i32F20)`
   - `result.z__i32` = `i32F20_to__i32(vector.z__i32F20)`
2. The input `vector` is unmodified (passed by value).

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation faithfully fulfills the semantic intent: converting each component of a `Vector__3i32F20` to the corresponding component of a `Vector__3i32` using the established `i32F20_to__i32` conversion helper. The `i32F20_to__i32` function performs an arithmetic right shift by `FRACTIONAL_PERCISION_20__BIT_SIZE` (20 bits), which correctly strips the 20-bit fractional portion and yields the integer component. All three components (x, y, z) are converted and assigned to their corresponding fields in the output struct — no field is omitted or reordered.

## Implementation Correctness
- **Type compatibility:** `i32F20_to__i32` returns `Signed_Index__i32` (which is `typedef int32_t Signed_Index__i32`). The `Vector__3i32` struct fields are of type `Signed_Index__i32`. The types match exactly with no implicit conversions or truncation.
- **Undefined behavior:** None. The function performs no pointer arithmetic, no dereferencing of pointers, no type punning, and no array or out-of-bounds access. The input is a value-type struct and the output is constructed via a compound literal initializer.
- **Validation:** No validation is needed or expected for this pure conversion utility; it operates entirely on value parameters and local computation.

## Side Effects
No side effects. The function is pure: it accepts a `Vector__3i32F20` by value and returns a newly constructed `Vector__3i32`. It does not modify any global or external state.

## Lavender-Specific Semantics
This function is not an initialization or reset function (its name does not contain "init", "initialize", or "reset"). It is a pure conversion function, so the Lavender initialization-vs-RAII distinction does not apply.
