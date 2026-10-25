# clamp__i32

**File of origin**: `core/include/numerics.h`

## Semantic

Clamps a 32-bit signed integer (`i32`) value to lie within the inclusive range `[min__i32, max__i32]`. If the value is below the minimum, the minimum is returned; if above the maximum, the maximum is returned; otherwise the value itself is returned unchanged.

## Pre-conditions

1. `value__i32` — any valid `i32` (int32_t) value; no constraints.
2. `min__i32` — any valid `i32` (int32_t) value; no constraints.
3. `max__i32` — any valid `i32` (int32_t) value; no constraints.
4. For meaningful clamping behavior, the caller should ensure `min__i32 <= max__i32`. The function does not enforce this; if `min__i32 > max__i32`, the semantics are undefined (the function will return `min__i32` when `value__i32 < min__i32`, and `max__i32` when `value__i32 > max__i32`, but these ranges may not form a coherent interval).
5. All three parameters are passed by value; no pointer parameters, so no null-check is required.

## Post-conditions

1. If `value__i32 < min__i32`, the function returns `min__i32`.
2. If `value__i32 > max__i32`, the function returns `max__i32`.
3. Otherwise, the function returns `value__i32` unchanged.
4. Assuming `min__i32 <= max__i32`, the return value is guaranteed to satisfy `min__i32 <= result <= max__i32`.
5. The function does not modify any global or shared state.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully realizes the semantic intent of clamping. The two sequential comparisons (`value__i32 < min__i32` and `value__i32 > max__i32`) correctly identify out-of-range values and return the appropriate bound. When the value falls within the range, it is returned directly. The logic is straightforward and matches the expected behavior of a clamp function. There is no semantic drift.

## Implementation Correctness

- **Type compatibility**: All parameters (`value__i32`, `min__i32`, `max__i32`) and the return type are `i32` (which is `typedef int32_t i32` from `defines.h`). No implicit conversions or truncation occur.
- **Undefined behavior**: None. The function performs only integer comparisons and returns. No pointer dereferencing, no array access, no arithmetic that could overflow.
- **Validation**: The function does not validate that `min__i32 <= max__i32`. This is acceptable for a low-level numeric utility function in a game engine context, where the caller is expected to provide a well-formed range. Adding a runtime check would introduce overhead inconsistent with the `static inline` performance profile.

## Side Effects

No side effects. This is a pure function: it reads only its parameters and returns a computed value. It does not modify any memory, state, or I/O.
