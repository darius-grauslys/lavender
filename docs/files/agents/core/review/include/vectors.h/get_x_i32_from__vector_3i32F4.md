# Function Review: `get_x_i32_from__vector_3i32F4`

## File of Origin
`core/include/vectors.h` (lines 420-424)

## Semantic
Extracts the x-component of a `Vector__3i32F4` (a 3-component fixed-point vector with 4 bits of fractional precision) and returns it as a plain signed 32-bit integer (`Signed_Index__i32`), truncating the fractional bits via arithmetic right-shift.

## Pre-conditions
1. `vector__3i32F4` is a valid `Vector__3i32F4` value passed by value (no pointer, so no null concern).
2. The caller does not require the fractional portion of the x-component; only the integer portion is returned.
3. No alignment or memory preconditions are required since the vector is passed by value.

## Post-conditions
1. Returns a `Signed_Index__i32` (`int32_t`) representing the integer portion of `vector__3i32F4.x__i32F4`, computed as an arithmetic right-shift by `FRACTIONAL_PERCISION_4__BIT_SIZE` (4 bits).
2. The input `vector__3i32F4` is not modified (passed by value).
3. The returned value is the truncated-toward-negative-infinity integer equivalent of the fixed-point x-component.

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation fully fulfills its semantic intent. The function composes two well-defined helpers:

- `get_x_i32F4_from__vector_3i32F4(vector__3i32F4)` extracts the raw `x__i32F4` field (an `i32F4`, which is `int32_t` with 4 fractional bits).
- `i32F4_to__i32(...)` converts that fixed-point value to a plain `i32` via `ARITHMETRIC_R_SHIFT(x, FRACTIONAL_PERCISION_4__BIT_SIZE)`.

The arithmetic right-shift correctly handles both positive and negative fixed-point values (the `ARITHMETRIC_R_SHIFT` macro explicitly handles the negative case to avoid implementation-defined behavior of right-shifting negative signed integers). The composition correctly yields the integer portion of the x-component. No fields are omitted, no reordering occurs, and the conversion matches the documented fixed-point semantics of `i32F4`.

## Implementation Correctness
- **Type compatibility:** All types are `int32_t`-compatible. `get_x_i32F4_from__vector_3i32F4` returns `Signed_Index__i32` (`int32_t`), which is passed to `i32F4_to__i32` which accepts `i32F4` (`int32_t`). The return type of `i32F4_to__i32` is `Signed_Index__i32` (`int32_t`), matching the function's declared return type. No implicit conversions or truncation occur.
- **Undefined behavior:** None. No pointer dereference, no null access, no out-of-bounds access, no type punning. The vector is passed by value, so there is no risk of null or dangling pointer dereference.
- **Validation:** No validation is needed for this function's role. It is a pure accessor operating on a value-type parameter. Validation (if any) is the caller's responsibility.

## Side Effects
No side effects. The function is pure: it takes its argument by value, does not modify any global or shared state, does not write through any pointer, and returns a computed value.
