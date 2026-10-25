clamp__u8 — core/include/numerics.h

Clamps a u8 value to the range [min__u8, max__u8].

Pre-conditions:
1. value__u8 is any valid u8 (0–255).
2. min__u8 is any valid u8 (0–255).
3. max__u8 is any valid u8 (0–255).
4. The caller is expected to ensure min__u8 <= max__u8; the function does not validate this invariant.

Post-conditions:
1. Returns min__u8 if value__u8 < min__u8.
2. Returns max__u8 if value__u8 > max__u8.
3. Returns value__u8 unchanged if min__u8 <= value__u8 <= max__u8.
4. The returned value is guaranteed to be within [min__u8, max__u8], assuming the pre-condition min__u8 <= max__u8 holds.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of clamping. It checks the lower bound first, then the upper bound, and returns the value itself if it already falls within range. The logic is consistent with the analogous clamp__i32 function in the same file, following the established pattern.

Implementation Correctness:
Type compatibility — all three parameters (value__u8, min__u8, max__u8) and the return type are u8. No implicit conversions or truncation occur.
Undefined behavior — none. The function performs only unsigned integer comparisons and returns. There is no pointer dereference, no arithmetic that could overflow, no type punning, and no out-of-bounds access.
Validation — no validation of the min <= max invariant is performed. This is appropriate for a low-level inline utility function; enforcing the invariant is the caller's responsibility. If min > max, the function would return min when value < min, or max when value > max, which could produce surprising results, but this is a caller error, not a defect in the function.

Side Effects:
No side effects. This is a pure function — it reads only its parameters and returns a value without modifying any external state.
