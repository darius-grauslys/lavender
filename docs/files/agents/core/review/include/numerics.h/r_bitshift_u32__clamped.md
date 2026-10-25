# r_bitshift_u32__clamped

**File of origin:** `core/include/numerics.h`

## Semantic

Right-shifts a 32-bit unsigned integer by a given amount and clamps the result to a minimum value. If the shift amount is 32 or greater, the function returns the minimum value directly (avoiding undefined behavior from shifting by the full bit-width).

## Pre-conditions

1. `value__u32` is a valid 32-bit unsigned integer (no constraints required).
2. `shift__u32` is a valid 32-bit unsigned integer (no constraints required; values >= 32 are handled).
3. `min__u32` is a valid 32-bit unsigned integer (no constraints required).

## Post-conditions

1. If `shift__u32 >= 32`, the return value equals `min__u32`.
2. Otherwise, the return value is the larger of `(value__u32 >> shift__u32)` and `min__u32`.
3. The return value is always a 32-bit unsigned integer.
4. The return value is always `>= min__u32`.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills its semantic intent. It safely handles the edge case where `shift__u32 >= 32` by returning `min__u32` directly, avoiding undefined behavior (shifting a 32-bit value by 32 or more is undefined in C). For valid shift amounts (< 32), it performs the right shift and clamps the result to `min__u32` if it falls below. The logic is straightforward and matches the function's stated purpose.

## Implementation Correctness

- **Type compatibility:** All parameters and the return type are `u32` (32-bit unsigned integer), matching exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** None. The function explicitly guards against shifting by >= 32 bits, which would be undefined behavior in C. The right-shift of unsigned integers is well-defined for shift amounts less than the bit-width.
- **Validation:** Validation is appropriate for the function's role. The guard against `shift__u32 >= 32` is necessary because shifting by the full bit-width or more is undefined behavior for 32-bit types.

## Side Effects

No side effects. This is a pure function: it takes inputs and returns a value without modifying any state, memory, or I/O.
