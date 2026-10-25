is_vector_3i32F20_within__squared_distance_i32 — core/include/vectors.h, lines 676-683

Checks whether the squared magnitude of a 3D vector (with i32F20 fixed-point components) is within a provided squared distance threshold (i32). The vector components are converted from i32F20 (20-bit fractional fixed-point) to plain i32 (integer) before computing the squared magnitude.

Pre-conditions:
1. `vector` is a valid `Vector__3i32F20` struct with x, y, z fields of type `i32F20` (int32_t).
2. `distance` is a pre-squared distance value (not a linear distance); it is expected to be non-negative. The caller is responsible for squaring the distance before passing it.

Post-conditions:
1. Returns `true` if `x*x + y*y + z*z <= distance`, where x, y, z are the integer representations (truncated via arithmetic right shift by 20 bits) of the i32F20 components.
2. Returns `false` otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent expressed by the function name. The name `is_vector_3i32F20_within__squared_distance_i32` indicates that the `distance` parameter is a pre-squared distance (not a linear distance), and the function should compare the squared magnitude of the vector against it directly. The implementation does exactly this — it does NOT square the `distance` parameter before comparing, which is correct.

This is consistent with the sibling function `is_vector_3i32_within__distance_i32` (which takes a linear distance and squares it internally as `distance * distance`), and `is_vector_3i32F20_within__squared_distance_i32F4` (which also treats the distance parameter as pre-squared).

The three components are correctly converted from i32F20 to i32 using `i32F20_to__i32`, which performs an arithmetic right shift by 20 bits (`FRACTIONAL_PERCISION_20__BIT_SIZE`). The squared magnitude is then computed as `x*x + y*y + z*z` and compared against `distance`.

Implementation Correctness:
Type compatibility — `i32F20_to__i32` returns `Signed_Index__i32` (int32_t), which is assigned to `i32` (also int32_t) — no implicit conversion or truncation. The `distance` parameter is `i32` (int32_t). All arithmetic (`x * x + y * y + z * z`) and the comparison (`<= distance`) operate on int32_t values. No type mismatches.

Undefined behavior — no pointer arithmetic, no null dereference (all parameters are passed by value), no type punning, no out-of-bounds access. The function is `static inline` and operates entirely on stack-local variables.

Overflow — `x * x` can overflow a 32-bit signed integer if the integer component of any axis exceeds 46340. This is consistent with the codebase pattern: the same approach is used in `get_distance_squared_of__vector_3i32` and `is_vector_3i32_within__distance_i32`. The codebase also provides `get_distance_squared_of__vector_3i32__no_overflow` for overflow-safe computation, indicating this is a known and accepted trade-off for the non-overflow-checked variants.

Validation — no validation is needed for this function's role. It is a low-level pure computation helper; validating inputs (e.g., checking for negative distance) would be the caller's responsibility.

Side Effects:
No side effects. The function is pure — it takes its parameters by value and returns a boolean result with no mutation of any state.
