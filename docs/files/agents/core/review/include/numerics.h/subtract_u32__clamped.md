# subtract_u32__clamped

**File of origin:** `core/include/numerics.h`

## Semantic

Subtracts `second__u32` from `first__u32` and clamps the result to a minimum value of `min__u32`. If the subtraction would underflow (i.e., `first__u32 < second__u32`), the function returns `min__u32` instead.

## Pre-conditions

1. `first__u32`, `second__u32`, and `min__u32` are all unsigned 32-bit integers (`u32`). No special constraints are required — any valid `u32` value is acceptable.
2. No pointer parameters; all arguments are passed by value, so null-safety is not a concern.

## Post-conditions

1. The return value is a `u32`.
2. The return value is always greater than or equal to `min__u32` (i.e., the result is clamped to the minimum). **This guarantee is NOT met by the current implementation due to a logic bug — see Correctness Verdict.**

## Correctness Verdict

**Incorrect**

The function contains a logic bug in the minimum-clamping comparison. On line 270, the condition is:

```c
if (subtraction > min__u32) {
    return min__u32;
}
```

This is inverted. It should be:

```c
if (subtraction < min__u32) {
    return min__u32;
}
```

**Impact of the bug:**
- When `subtraction > min__u32` (result is *above* the minimum), the function incorrectly returns `min__u32` instead of the subtraction result.
- When `subtraction <= min__u32` (result is *at or below* the minimum), the function incorrectly returns the raw subtraction instead of clamping to `min__u32`.

In other words, the clamping behavior is exactly reversed: it clamps values that are above the minimum and allows values that are below the minimum to pass through unclamped.

**Evidence from sibling functions confirming the convention:**
The sibling function `r_bitshift_u32__clamped` (same file, lines 451-461) uses the parameter name `min__u32` as a minimum bound with the correct comparison:

```c
u32 r_bitshift_u32__clamped(u32 value__u32, u32 shift__u32, u32 min__u32) {
    ...
    if (shifted < min__u32) {   // CORRECT: clamps when result is below min
        return min__u32;
    }
    return shifted;
}
```

The `clamp__u8` function (lines 442-449) also confirms the convention:

```c
u8 clamp__u8(u8 value__u8, u8 min__u8, u8 max__u8) {
    if (value__u8 < min__u8)       // CORRECT: clamps when below min
        return min__u8;
    if (value__u8 > max__u8)
        return max__u8;
    return value__u8;
}
```

The sibling functions `subtract_u8__clamped` and `subtract_u16__clamped` contain the same inverted comparison bug.

## Semantic Alignment

The implementation does **not** fulfill the semantic intent. The function is named `subtract_u32__clamped` and its third parameter is named `min__u32`, indicating it should clamp the subtraction result to a minimum value. The correct behavior is:

- If `first__u32 < second__u32`: return `min__u32` (prevent underflow). ✓ Correct in current code.
- If `first__u32 >= second__u32`: compute `subtraction = first__u32 - second__u32`.
  - If `subtraction < min__u32`: return `min__u32` (clamp to minimum). ✗ **Bug: current code checks `subtraction > min__u32` instead.**
  - Otherwise: return `subtraction`. ✗ **Bug: current code reaches this path only when `subtraction <= min__u32`, returning unclamped values below the minimum.**

## Implementation Correctness

- **Type compatibility:** All parameters and the return type are `u32`. The local variable `subtraction` is also `u32`. No implicit conversions or truncation. ✓
- **Undefined behavior:** No null pointer dereference, no out-of-bounds access, no type punning. The subtraction `first__u32 - second__u32` is safe because it is guarded by the `first__u32 < second__u32` check, preventing unsigned underflow. ✓
- **Validation:** The function performs appropriate validation (underflow check) for its role. The clamping check is present but logically inverted. The validation logic itself is appropriate for this function's role. ✓ (aside from the inverted comparison)

## Side Effects

No side effects. This is a pure function: it takes three `u32` values by value and returns a `u32`. No memory is read or written, no global state is modified.
