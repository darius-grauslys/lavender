subtract_u8__clamped — core/include/numerics.h, lines 231-244

Subtracts two u8 values with a minimum clamp.

Pre-conditions:
1. first__u8 is any u8 value.
2. second__u8 is any u8 value.
3. min__u8 is any u8 value representing the minimum allowed result.

Post-conditions:
1. Returns a u8 result that is the subtraction of second__u8 from first__u8, clamped to a minimum of min__u8.
2. If first__u8 < second__u8, the result is min__u8 (underflow protection).
3. If first__u8 >= second__u8, the result is max(first__u8 - second__u8, min__u8).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent — indicated by the parameter name `min__u8` and the first guard clause — is to subtract second__u8 from first__u8 and clamp the result to a minimum of min__u8. The first guard clause correctly returns min__u8 when first__u8 < second__u8 (the subtraction would underflow). However, the second guard clause is inverted: it checks `subtraction > min__u8` and returns min__u8, when it should check `subtraction < min__u8` and return min__u8. This means that when the subtraction result is above the minimum, the function incorrectly returns the minimum; and when the result is at or below the minimum, the function incorrectly returns the unclamped result.

This is confirmed by comparison with the analogous function `r_bitshift_u8__clamped` in the same file, which performs a minimum clamp with the same parameter name `min__u8` and correctly uses `if (shifted < min__u8) { return min__u8; }`. It is also confirmed by `clamp__u8` in the same file, which correctly uses `if (value__u8 < min__u8) return min__u8;` for the minimum clamp. The `add_u8__clamped` function correctly uses `>` for a maximum clamp (its parameter is named `clamp__u8`, not `min__u8`), confirming that `>` is the wrong operator for a minimum clamp.

The same bug pattern exists in `subtract_u16__clamped` and `subtract_u32__clamped` in the same file, but this review focuses on `subtract_u8__clamped`.

Implementation Correctness:
Type compatibility — all parameter types are u8, matching the local variable `subtraction` (u8). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The first guard prevents unsigned underflow.
Validation — no validation is needed; the function is a pure arithmetic utility. The caller is responsible for passing meaningful values.

Side Effects:
No side effects.
