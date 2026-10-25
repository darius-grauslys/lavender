divide_into__i32F4 — core/include/numerics.h

Divides two integers p and q, producing a fixed-point result by first converting p to i32F4 format (4-bit fractional precision) and then dividing by q.

Pre-conditions:
1. p is any i32 (signed 32-bit integer).
2. q is any i32 (signed 32-bit integer) and must be non-zero (caller's responsibility — no division-by-zero check exists).
3. The caller must ensure that i32_to__i32F4(p) does not overflow; i.e., p must be within the representable range for i32F4 after left-shifting by FRACTIONAL_PERCISION_4__BIT_SIZE (4 bits).

Post-conditions:
1. Returns a value of type i32F8 (int32_t) representing the quotient, but the value is computed with only i32F4 (4-bit) fractional precision despite the i32F8 (8-bit) return type.

Correctness Verdict: Incorrect

Semantic Alignment:
The function name and return type suggest the result should be in i32F8 format (8 bits of fractional precision). However, the implementation calls i32_to__i32F4(p), which left-shifts p by 4 bits, producing a value in i32F4 format (4-bit fractional precision). Dividing this i32F4 value by q yields a result that has only 4 bits of fractional precision, not 8. The returned value is therefore semantically incorrect for the i32F8 return type — it is off by a factor of 2^4 = 16 from what a true i32F8 representation of (p / q) would be.

Compare with the sibling function divide_into__i32F8, which calls i32_to__i32F8(p) (shifting by 8 bits) and returns i32F8 — that function is internally consistent. divide_into__i32F4 is not: it computes in i32F4 precision but returns as i32F8.

The fix is to change the return type to i32F4, which would correctly match the 4-bit fractional precision of the computation. Alternatively, the implementation should call i32_to__i32F8(p) to produce a true i32F8 result.

Implementation Correctness:
Type compatibility — i32F4, i32F8, and i32 are all typedefs for int32_t, so the division i32F4 / i32 yields int32_t, which is compatible with the i32F8 return type. No implicit conversion issues.
No undefined behavior from pointer arithmetic, null dereference, type punning, or out-of-bounds access.
No validation is provided for q != 0, but this is consistent with the codebase's pattern of leaving such checks to the caller for low-level numeric functions.

Side Effects:
No side effects — the function is pure, performing only arithmetic on its value parameters and returning a result.
