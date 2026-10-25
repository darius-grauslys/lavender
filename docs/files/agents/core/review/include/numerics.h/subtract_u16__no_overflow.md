subtract_u16__no_overflow — core/include/numerics.h

Performs saturating subtraction of two unsigned 16-bit integers, returning 0 when the result would underflow.

Pre-conditions:
1. first__u16 is any u16 value (no constraint).
2. second__u16 is any u16 value (no constraint).

Post-conditions:
1. If first__u16 >= second__u16, returns first__u16 - second__u16 (a u16 in range [0, UINT16_MAX]).
2. If first__u16 < second__u16, returns 0 (preventing unsigned underflow).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of "subtract with no overflow." When the subtrahend exceeds the minuend, returning 0 prevents unsigned wraparound. When the minuend is greater than or equal to the subtrahend, the subtraction is performed normally. The result is always a valid u16 in the range [0, UINT16_MAX].

Implementation Correctness:
Type compatibility — both parameters are u16 and the return type is u16. The literal 0 is an int constant that is safely and implicitly converted to u16 (0 fits in u16 without truncation). The subtraction first__u16 - second__u16 is computed with integer promotion (u16 promoted to int), but since first__u16 >= second__u16 is guaranteed by the guard, the result is non-negative and fits within u16, so the implicit narrowing on return is safe.
Undefined behavior — none. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The comparison and subtraction are well-defined for all u16 inputs.
Validation — no validation is needed; the function is a low-level arithmetic utility. Both inputs are unsigned integers with no invalid values.

Side Effects:
No side effects — this is a pure function. It reads only its two parameters and returns a value without modifying any state.
