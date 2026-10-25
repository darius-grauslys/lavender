is_vector_3i32_within__distance_i32 — core/include/vectors.h, lines 709-717

Determines whether a 3D integer vector's Euclidean distance from the origin is within a given threshold distance, by comparing squared magnitudes to avoid a square-root computation.

Pre-conditions:
1. `vector` is passed by value; no constraints on individual components.
2. `distance` is a `Signed_Index__i32` (i.e., `int32_t`). The function does not validate that `distance` is non-negative; if a negative value is passed, `distance * distance` is still positive, so the comparison is mathematically valid, though semantically a negative distance is meaningless. It is the caller's responsibility to pass a non-negative distance.
3. Component magnitudes and `distance` should be small enough that squaring does not overflow `int32_t` (i.e., absolute values should not exceed approximately 46340, the square root of `INT32_MAX`). Overflow is not detected; the caller should use `get_distance_squared_of__vector_3i32__no_overflow` when overflow protection is required.

Post-conditions:
1. Returns `true` if `vector.x__i32² + vector.y__i32² + vector.z__i32² <= distance²`, i.e., the vector's distance from the origin is within `distance`.
2. Returns `false` otherwise.
3. No state is mutated; the function is pure.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of checking whether a vector lies within a given distance from the origin. By comparing squared distances (`x² + y² + z² <= distance²`) instead of computing actual Euclidean distance, the function avoids an unnecessary `sqrt` call — a standard and correct optimization. The algorithm matches the intent exactly.

Implementation Correctness:
Type compatibility — all operands (`vector.x__i32`, `vector.y__i32`, `vector.z__i32`, and `distance`) are `Signed_Index__i32` (i.e., `int32_t`). No implicit conversions or truncation occur.
Undefined behavior — signed integer multiplication (`vector.x__i32 * vector.x__i32` and `distance * distance`) and addition can overflow `int32_t` when component magnitudes or `distance` exceed approximately 46340. In C, signed integer overflow is undefined behavior. However, this is an expected limitation of this utility function; the codebase provides `get_distance_squared_of__vector_3i32__no_overflow` as an overflow-safe alternative. No null dereference, pointer arithmetic, or out-of-bounds access occurs.
Validation — no validation of `distance` (e.g., non-negativity) or overflow is performed. This is appropriate for a low-level inline utility function; validation is the caller's responsibility, consistent with the pattern used by sibling functions such as `is_vector_3i32F4_within__distance_i32F4`.

Side Effects:
No side effects. The function is pure: it reads only its parameters and returns a boolean result.
