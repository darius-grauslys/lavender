clamp__p_u8 — core/include/numerics.h

Clamps the value pointed to by p_value__u8 to the inclusive range [min__u8, max__u8] in-place, writing the clamped bound back through the pointer if the current value falls outside the range.

Pre-conditions:
1. p_value__u8 must be a non-null pointer to a writable u8 location (it is dereferenced unconditionally).
2. min__u8 and max__u8 are u8 values; the caller is responsible for ensuring min__u8 <= max__u8.

Post-conditions:
1. After return, *p_value__u8 is guaranteed to lie within [min__u8, max__u8].
2. If the original value was less than min__u8, *p_value__u8 is set to min__u8.
3. If the original value was greater than max__u8, *p_value__u8 is set to max__u8.
4. If the original value was already within [min__u8, max__u8], *p_value__u8 is left unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully performs in-place clamping to the range [min__u8, max__u8]. The value is read once into a local, then compared against both bounds; if out of range, the nearest bound is written through the pointer and the function returns early. If the value is within range, no write occurs. This is semantically equivalent to the non-pointer clamp__u8 and follows the same pattern as the analogous clamp__p_i32, confirming consistency across the numerics module.

Implementation Correctness:
Type compatibility — every parameter type matches its usage exactly: u8 *p_value__u8 (pointer to u8), u8 min__u8, u8 max__u8, and the local u8 value__u8. No implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The pointer is dereferenced without a null check, but this is appropriate for a low-level static inline function; null validation is the caller's responsibility, consistent with the rest of the numerics module.
Validation — no validation is needed within this function. The min/max ordering invariant (min <= max) is the caller's responsibility, matching the convention of clamp__u8 and clamp__p_i32.

Side Effects:
Mutates *p_value__u8 if the current value is outside [min__u8, max__u8]; otherwise leaves *p_value__u8 unchanged. No other observable side effects.
