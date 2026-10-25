# get_distance_squared_of__vector_3i32F20

**File of origin:** `core/include/vectors.h`

## Semantic

Computes the squared Euclidean distance (x² + y² + z²) of a `Vector__3i32F20` vector, returning the result as an `i32F20` fixed-point value. The intent is to preserve 20-bit fractional precision in the result.

## Pre-conditions

1. The input `vector__3i32F20` must be a valid `Vector__3i32F20` struct. No null pointer or validity check is performed (the parameter is passed by value, so this is trivially satisfied).
2. No explicit bounds or range checking is performed on the vector components.

## Post-conditions

1. Returns an `i32F20` value representing the squared distance of the vector.
2. The input vector is not modified (passed by value).

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation does **not** fulfill the semantic intent of computing the distance squared in `i32F20` precision. The function:

1. **Lossy conversion to i32F4**: Converts the input `Vector__3i32F20` to `Vector__i32F4` via `vector_3i32F20_to__vector_3i32F4`, which calls `i32F20_to__i32F4`. This right-shifts each component by `FRACTIONAL_PERCISION_16__BIT_SIZE` (16 bits), discarding 16 bits of fractional precision. A `Vector__3i32F20` has 20 fractional bits; after conversion to `Vector__3i32F4` (4 fractional bits), 16 bits of fractional precision are permanently lost.

2. **Computes in reduced precision**: The distance squared is then computed by `get_distance_squared_of__vector_3i32F4`, which operates entirely in the i32F4 domain.

3. **Type mismatch on return**: The function signature declares a return type of `i32F20`, but the actual computation is performed in `i32F4`. Since both `i32F20` and `i32F4` are typedefs for `int32_t`, the i32F4 result is returned as-is, reinterpreted as `i32F20`. This means the returned value is semantically an i32F4 value masquerading as i32F20 — the precision has already been lost and cannot be recovered.

The TODO comment `// TODO: can we preserve more percision?` directly above the function confirms the author's awareness of this precision issue. A correct implementation would compute the distance squared directly in the i32F20 domain (e.g., using `multiply__i32F4`-style fixed-point multiplication adapted for 20-bit fractional parts), or at minimum avoid the lossy i32F20→i32F4→i32F20 round-trip.

## Implementation Correctness

1. **Overflow risk in `get_distance_squared_of__vector_3i32F4`**: The multiplication `vector__3i32F4.x__i32F4 * vector__3i32F4.x__i32F4` performs a direct signed integer multiplication of two `int32_t` values. If either component is large, the product can exceed `INT32_MAX`, causing signed integer overflow — which is **undefined behavior** in C. A safer approach would use the existing `multiply__i32F4` helper, which performs `i32F4_to__i32(x * y)` to properly handle the fixed-point scaling (though this still has the same overflow risk — the function comment notes it "Can only multiply values 0 <-> BIT(12).F4").

2. **Type compatibility**: The parameter types match the struct field types. The return type (`i32F20`) is compatible with the intermediate return from `get_distance_squared_of__vector_3i32F4` (which returns `i32F4`), but as noted above, this is a semantic type mismatch rather than a compilation error.

3. **No undefined behavior** from pointer dereference, out-of-bounds access, or null pointers — the function operates on value types only.

## Side Effects

No side effects. The function is pure: it takes its input by value and returns a computed result without modifying any external state or global variables.
