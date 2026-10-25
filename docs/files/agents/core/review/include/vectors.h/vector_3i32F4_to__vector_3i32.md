vector_3i32F4_to__vector_3i32 — core/include/vectors.h

Converts a 3D vector with 4-bit fixed-point fractional precision (Vector__3i32F4) into a 3D vector of plain signed 32-bit integers (Vector__3i32) by truncating the fractional bits of each component via an arithmetic right shift.

Pre-conditions:
1. The `vector` parameter is passed by value (not a pointer), so it is always valid — no null check is required.
2. `vector.x__i32F4`, `vector.y__i32F4`, and `vector.z__i32F4` are `i32F4` values (typedef `int32_t` with 4 fractional bits); any representable `i32F4` value is accepted.

Post-conditions:
1. A new `Vector__3i32` is returned by value.
2. The returned struct's `x__i32` field equals `i32F4_to__i32(vector.x__i32F4)`, `y__i32` equals `i32F4_to__i32(vector.y__i32F4)`, and `z__i32` equals `i32F4_to__i32(vector.z__i32F4)`.
3. Each component is the result of an arithmetic right shift by `FRACTIONAL_PERCISION_4__BIT_SIZE` (4 bits), which truncates the 4-bit fractional portion while preserving the sign.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. The function name `vector_3i32F4_to__vector_3i32` correctly describes converting from a 4-bit fixed-point vector to a plain integer vector. Each of the three components (x, y, z) is converted using the correct conversion function `i32F4_to__i32`, which performs an arithmetic right shift by 4 bits — the standard way to convert from `i32F4` (4 fractional bits) to `i32`. The struct initializer `(Vector__3i32){ ... }` assigns all three fields in the correct order (x, y, z), matching the struct definition `typedef struct Vector__3i32_t { Signed_Index__i32 x__i32, y__i32, z__i32; } Vector__3i32;`.

Implementation Correctness:
- Type compatibility: `i32F4_to__i32` accepts `i32F4` (which is `int32_t`) and returns `Signed_Index__i32` (also `int32_t`). The `Vector__3i32` struct fields are `Signed_Index__i32`. Types match exactly with no implicit conversions or truncation.
- Undefined behavior: None. No pointer arithmetic, no null dereference (parameter is passed by value), no type punning, no out-of-bounds access. The `ARITHMETRIC_R_SHIFT` macro correctly handles negative values, avoiding implementation-defined behavior of right-shifting negative integers.
- Validation: No validation is needed. This is a pure conversion function operating on a value-type parameter. It is the caller's responsibility to provide meaningful input.

Side Effects:
No side effects. The function is pure — it takes a `Vector__3i32F4` by value, computes a new `Vector__3i32`, and returns it. No memory is modified, no I/O occurs, and no global state is touched.
