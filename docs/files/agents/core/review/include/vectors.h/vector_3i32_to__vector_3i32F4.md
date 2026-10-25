vector_3i32_to__vector_3i32F4 — core/include/vectors.h, lines 267-274

Converts a Vector__3i32 (three signed 32-bit integers) to a Vector__3i32F4 (three signed 32-bit fixed-point integers with 4 bits of fractional precision) by shifting each component left by FRACTIONAL_PERCISION_4__BIT_SIZE (4 bits).

Pre-conditions:
1. `vector` is passed by value; no pointer validity constraints apply.
2. Each component (x__i32, y__i32, z__i32) is of type Signed_Index__i32 (int32_t); no range constraints are required or checked.

Post-conditions:
1. Returns a `Vector__3i32F4` by value whose `x__i32F4`, `y__i32F4`, and `z__i32F4` fields are the fixed-point representations of the corresponding input components.
2. Each output field equals `i32_to__i32F4(input_component)`, i.e., the input value left-shifted by 4 bits (the FRACTIONAL_PERCISION_4__BIT_SIZE).

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills its semantic intent. Each of the three components (x, y, z) is individually converted via `i32_to__i32F4` and placed into the corresponding field of the returned `Vector__3i32F4` struct. All three struct fields are assigned — no member is omitted, and the field order matches the struct declaration (`x__i32F4`, `y__i32F4`, `z__i32F4`). The `i32_to__i32F4` function performs `ARITHMETRIC_L_SHIFT(x, FRACTIONAL_PERCISION_4__BIT_SIZE)`, which is the correct fixed-point conversion for 4-bit fractional precision.

Implementation Correctness:
- Type compatibility: `vector.x__i32` is `Signed_Index__i32` (int32_t), which is exactly the parameter type expected by `i32_to__i32F4`. The return type is `i32F4` (int32_t), which matches the field type of `Vector__3i32F4`. No implicit conversions or truncation occur.
- Undefined behavior: No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The `ARITHMETRIC_L_SHIFT` macro safely handles negative values by casting through `u32` before shifting: `((i32)((u32)(x) << (n)))`.
- Validation: No validation is needed or expected for this function; it is a pure conversion utility. The caller is responsible for providing meaningful input values.

Side Effects:
No side effects. The function is pure — it takes a value parameter and returns a newly constructed `Vector__3i32F4` without modifying any state.
