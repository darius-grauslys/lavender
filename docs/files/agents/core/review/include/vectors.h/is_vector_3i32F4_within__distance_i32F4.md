# is_vector_3i32F4_within__distance_i32F4

**File of origin:** `core/include/vectors.h` (lines 698–706)

## Semantic

Returns `true` if the Euclidean magnitude of the given `Vector__3i32F4` is less than or equal to the given `i32F4` distance. The check is performed by comparing the squared magnitude of the vector against the squared distance, avoiding a square-root computation.

## Pre-conditions

1. `vector` — a `Vector__3i32F4` struct containing three `i32F4` components (`x__i32F4`, `y__i32F4`, `z__i32F4`). No constraints on the values; they may be positive, negative, or zero.
2. `distance` — an `i32F4` scalar representing the threshold distance. May be any value (positive, negative, or zero). If negative, the squared comparison `distance * distance` will still yield a non-negative result.

## Post-conditions

1. The function returns `true` if and only if `vector.x__i32F4² + vector.y__i32F4² + vector.z__i32F4² ≤ distance²` (in raw fixed-point integer arithmetic).
2. No state is mutated; the function is pure.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function compares the squared magnitude of the vector to the squared distance threshold.

**Fixed-point scaling analysis:**

- `i32F4` is a signed 32-bit integer with 4 fractional bits (`FRACTIONAL_PERCISION_4__BIT_SIZE = 4`). A stored value `v` represents the real number `v / 2⁴`.
- Raw multiplication of two `i32F4` values (`a * b`) produces a result with 8 fractional bits (i32F8 representation), representing `(a/16) * (b/16) = (a*b) / 256`.
- The left-hand side `vector.x__i32F4 * vector.x__i32F4 + vector.y__i32F4 * vector.y__i32F4 + vector.z__i32F4 * vector.z__i32F4` is therefore in i32F8 format, representing `|vector|²` scaled by `2⁸`.
- The right-hand side `distance * distance` is also in i32F8 format, representing `distance²` scaled by `2⁸`.
- Since both sides share the same i32F8 scaling, the comparison `<=` is semantically correct.

This is consistent with the companion function `get_distance_squared_of__vector_3i32F4`, which performs the same raw multiplications and then shifts right by 4 to convert the result back to i32F4. The within-distance check avoids that shift because both sides of the comparison carry identical scaling.

## Implementation Correctness

- **Type compatibility:** All operands are `i32F4` (i.e., `int32_t`). The multiplication `vector.x__i32F4 * vector.x__i32F4` and `distance * distance` both produce `int32_t` results. The addition of the three squared components is also `int32_t`. The comparison `<=` between two `int32_t` values is well-defined. No implicit conversions or truncation occur.
- **Undefined behavior:** No pointer dereference, no array indexing, no type punning. The function operates only on pass-by-value parameters.
- **Overflow:** As with all fixed-point multiplication of 32-bit integers, large component or distance values can cause signed integer overflow (UB in C). However, this is the same pattern used by the sibling function `is_vector_3i32_within__distance_i32` (which uses plain `i32`), and the function does not document overflow protection. Overflow prevention is the caller's responsibility.
- **Validation:** No validation is performed, which is appropriate for a low-level `static inline` helper. The caller is responsible for ensuring inputs are within a safe range.

## Side Effects

No side effects. The function is pure — it reads only its pass-by-value parameters and returns a `bool`.
