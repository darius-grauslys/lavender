# Function Review: is_vector_3i32F20_within__squared_distance_i32F4

- **Function name:** `is_vector_3i32F20_within__squared_distance_i32F4`
- **File of origin:** `core/include/vectors.h` (lines 686-695)

## Semantic

Determines whether the squared magnitude (distance from origin) of a 3D vector stored in `i32F20` fixed-point format is within a given squared distance threshold, using `i32F4` fixed-point arithmetic for the computation.

## Pre-conditions

1. `vector` is a valid `Vector__3i32F20` struct; its `x__i32F20`, `y__i32F20`, and `z__i32F20` fields contain valid `i32F20` values (20 fractional bits).
2. `distance` is a valid `i32` value representing a squared distance threshold.

## Post-conditions

1. Returns `true` if the squared distance (computed in `i32F4` fixed-point format) is less than or equal to `distance`; `false` otherwise.
2. The function is pure — no side effects on any state.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function name suffix `_squared_distance_i32F4` indicates that the `distance` parameter is expected to be in `i32F4` fixed-point format. However, the parameter is declared as `i32 distance` (a plain integer, no fractional bits).

The computation on the left side of the comparison uses `multiply__i32F4()`, which performs fixed-point multiplication preserving the F4 format (4 fractional bits). This means the result of `multiply__i32F4(x, x) + multiply__i32F4(y, y) + multiply__i32F4(z, z)` is a value in **F4 format** (scaled by 2^4 = 16).

The right side of the comparison, `distance`, is a plain `i32` (unscaled). Comparing an F4-scaled value against an unscaled integer produces semantically incorrect results.

**Example:**
- Vector (1.0, 0.0, 0.0) in F20: stored as (1048576, 0, 0)
- Converted to F4 via `i32F20_to__i32F4`: (16, 0, 0) — 16 in F4 represents 1.0
- `multiply__i32F4(16, 16)` = `i32F4_to__i32(256)` = `256 >> 4` = 16 — 16 in F4 represents 1.0 (correct: 1.0² = 1.0)
- Squared distance result = 16 (in F4 format)
- If caller passes `distance = 1` (plain i32): comparison is `16 <= 1` → **false** (incorrect — should be true)
- If the parameter were `i32F4 distance` and caller passes `i32_to__i32F4(1)` = 16: comparison is `16 <= 16` → **true** (correct)

**Comparison with sibling functions:**
- `is_vector_3i32F20_within__squared_distance_i32` (line 676): Correctly takes `i32 distance` and uses plain integer arithmetic throughout. The `i32` suffix matches the parameter type.
- `is_vector_3i32F4_within__distance_i32F4` (line 698): Correctly takes `i32F4 distance` to match F4 arithmetic.

The fix is to change the parameter type from `i32 distance` to `i32F4 distance`, so the parameter format matches both the function name and the F4 fixed-point arithmetic used in the computation.

## Implementation Correctness

1. **Type compatibility:** The assignment `i32F4 x = i32F20_to__i32F4(vector.x__i32F20)` is type-compatible since both `i32F4` and the return type of `i32F20_to__i32F4` (`Signed_Index__i32`) are `int32_t`. However, the parameter type `i32 distance` does not match the F4 format of the computed squared distance, creating a semantic type mismatch.

2. **Undefined behavior:** No null pointer dereference, no out-of-bounds access, no type punning. The function is safe from UB.

3. **Validation:** No validation is needed for this function's role — it is a pure computation function. Input validation is the caller's responsibility.

## Side Effects

No side effects. The function is pure — it reads from the input vector and returns a boolean result without modifying any state.
