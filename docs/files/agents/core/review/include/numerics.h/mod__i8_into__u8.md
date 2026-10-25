mod__i8_into__u8 — core/include/numerics.h

Computes the mathematical (always non-negative) modulo of a signed 8-bit integer x__i8 with respect to mod__i8, returning the result as an unsigned 8-bit integer.

Pre-conditions:
1. mod__i8 must be positive (mod__i8 > 0). A zero modulus causes undefined behavior (division by zero in the modulo operator). A negative modulus produces incorrect results outside the expected range.
2. x__i8 may be any value in the full i8 range [-128, 127]; no sign constraint.

Post-conditions:
1. Returns a u8 value in the range [0, mod__i8 - 1] (guaranteed when mod__i8 > 0).
2. The returned value is always non-negative.
3. No state is modified; the function is pure.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent. The formula (x % m + m) % m is the standard C idiom for computing a non-negative modulo result when m > 0. In C, the % operator yields a remainder with the sign of the dividend (x__i8), so for negative x__i8 the intermediate result x__i8 % mod__i8 can be negative. Adding mod__i8 and reducing again shifts the result into the non-negative range [0, mod__i8 - 1]. The cast to u8 is safe because the result is guaranteed to fit within u8 range (maximum mod__i8 - 1 = 126 when mod__i8 is i8 and positive). The sibling function mod__i32_into__u32 uses the identical pattern, confirming this is a deliberate, consistent design.

Implementation Correctness:
Type compatibility — i8 operands (int8_t) are promoted to int per C integer promotion rules. The intermediate computation is performed in int arithmetic, which is sufficient to avoid overflow for i8-range values. The final result is cast to u8, which is safe given the result range [0, 126].
Undefined behavior — If mod__i8 is 0, the modulo operation invokes undefined behavior. If mod__i8 is negative, the result is not in the expected non-negative range. No validation guards against these cases, which is consistent with the codebase convention for low-level static inline arithmetic utilities (e.g., min__u8, max__u8, clamp__u8) where the caller is responsible for ensuring valid inputs.
Validation — No input validation is performed. This is appropriate for a static inline utility function in a header; the caller is expected to ensure mod__i8 > 0.

Side Effects:
No side effects. This is a pure function: it reads its parameters and returns a computed value without modifying any state or global variables.
