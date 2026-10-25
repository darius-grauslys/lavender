clamp__p_i32 — core/include/numerics.h

Clamps the value pointed to by p_value__i32 in-place to the inclusive range [min__i32, max__i32]. If the value is below min__i32 it is set to min__i32; if above max__i32 it is set to max__i32; otherwise it is left unchanged.

Pre-conditions:
1. p_value__i32 must be a non-null pointer to a writable i32.
2. min__i32 and max__i32 are any i32 values; the caller is responsible for ensuring min__i32 <= max__i32 (not enforced by the function).

Post-conditions:
1. The value at *p_value__i32 is clamped to [min__i32, max__i32].
2. If the original value was less than min__i32, then *p_value__i32 == min__i32 after the call.
3. If the original value was greater than max__i32, then *p_value__i32 == max__i32 after the call.
4. If min__i32 <= original value <= max__i32, then *p_value__i32 is unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of in-place clamping to a range. The function reads the value via the pointer, compares it against both bounds, and writes back the clamped value. All three cases (below min, above max, within range) are handled correctly with no semantic drift.

Implementation Correctness:
Type compatibility — all parameter types match exactly (i32 *, i32, i32). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (null is a precondition violation by the caller), no type punning, no out-of-bounds access.
Validation — no validation is performed for null pointer or min > max. This is appropriate for a low-level utility function; validation is the caller's responsibility.

Side Effects:
Mutates the i32 value at the address pointed to by p_value__i32. No other side effects.