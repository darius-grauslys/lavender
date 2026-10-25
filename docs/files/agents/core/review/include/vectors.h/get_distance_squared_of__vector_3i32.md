get_distance_squared_of__vector_3i32 — core/include/vectors.h

Computes the squared Euclidean distance of a 3D vector from the origin using the formula x² + y² + z².

Pre-conditions:
1. `vector__3i32` is passed by value; no non-null pointer requirement.
2. Each component (`x__i32`, `y__i32`, `z__i32`) is a `Signed_Index__i32` (int32_t) and may be any valid signed 32-bit integer value.
3. The caller is responsible for ensuring component magnitudes do not cause signed integer overflow (see Implementation Correctness). The overflow-safe variant `get_distance_squared_of__vector_3i32__no_overflow` is available when this cannot be guaranteed.

Post-conditions:
1. Returns the squared distance as an `i32` (int32_t), computed as `x*x + y*y + z*z`.
2. The input vector is not modified (passed by value).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly computes the squared distance from the origin using the standard formula `x*x + y*y + z*z`. The computation matches the semantic intent of the function name. The return type `i32` (int32_t) is consistent with the component type `Signed_Index__i32` (also int32_t), so no type mismatch occurs.

Implementation Correctness:
Type compatibility — All struct fields are `Signed_Index__i32` (int32_t) and the return type is `i32` (int32_t). Both are the same underlying type (`int32_t`), so there are no implicit conversions or truncation.
Undefined behavior — Signed integer overflow is possible when any component's absolute value exceeds ~46340 (sqrt(INT32_MAX)), as `x*x` would exceed INT32_MAX. The sum of squares can also overflow. This is a known limitation: the codebase provides `get_distance_squared_of__vector_3i32__no_overflow` as a separate variant for overflow-safe computation. No other UB concerns exist (no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access).
Validation — No validation is performed. This is appropriate for this function's role as a low-level, fast computation helper. The caller is responsible for ensuring values do not overflow, consistent with the similar `is_vector_3i32_within__distance_i32` function which uses the same unchecked pattern.

Side Effects:
No side effects. This is a pure function — it reads only its by-value parameter and returns a computed result. No memory is accessed through pointers, and no global state is modified.
