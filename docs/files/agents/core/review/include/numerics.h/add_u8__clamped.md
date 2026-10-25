# add_u8__clamped

**File of origin:** `core/include/numerics.h`

## Semantic

Adds two unsigned 8-bit integers (`first__u8` and `second__u8`) and clamps the result to `clamp__u8`. If the sum would overflow the u8 range, or if the sum exceeds `clamp__u8`, the function returns `clamp__u8`. Otherwise, it returns the exact sum.

## Pre-conditions

1. `first__u8` is a valid `u8` value (0–255).
2. `second__u8` is a valid `u8` value (0–255).
3. `clamp__u8` is a valid `u8` value (0–255).
4. All parameters are passed by value; no pointer parameters, so no null-check requirements.

## Post-conditions

1. The return value is a `u8` that is guaranteed to be ≤ `clamp__u8`.
2. If `first__u8 + second__u8` would overflow (i.e., exceed `MAX__U8` = 255), the return value is `clamp__u8`.
3. If `first__u8 + second__u8` does not overflow but exceeds `clamp__u8`, the return value is `clamp__u8`.
4. If `first__u8 + second__u8` does not overflow and does not exceed `clamp__u8`, the return value is exactly `first__u8 + second__u8`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of clamped addition. The function first checks for unsigned overflow using the standard idiom `MAX__U8 - first__u8 < second__u8`, which detects when `first__u8 + second__u8` would exceed 255 without causing undefined behavior. If overflow would occur, it returns `clamp__u8`. Otherwise, it safely computes the sum and checks whether it exceeds `clamp__u8`, returning `clamp__u8` if so, or the exact sum otherwise.

The overflow check is well-formed: `MAX__U8 - first__u8` computes the maximum value that can be added to `first__u8` without overflow, and comparing it against `second__u8` correctly determines whether the addition would overflow.

## Implementation Correctness

- **Type compatibility:** All parameters and the return type are `u8`, matching correctly. No implicit conversions or truncation.
- **Undefined behavior:** No undefined behavior. The overflow check prevents any potential unsigned integer overflow before the addition `first__u8 + second__u8` is evaluated. The expression `MAX__U8 - first__u8` is always safe since `first__u8 ≤ MAX__U8`.
- **Validation:** The function is a pure arithmetic utility with no external state. No additional validation (e.g., null checks) is needed or expected for a static inline function operating on value parameters.

## Side Effects

No side effects. The function is pure: it reads only its parameters and returns a computed value without modifying any state.
