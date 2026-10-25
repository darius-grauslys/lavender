r_bitshift_u16__clamped — core/include/numerics.h

Right bit-shifts a u16 value by a specified amount, clamping the result to a minimum value.

Pre-conditions:
1. value__u16 is any u16 value; no range constraint.
2. shift__u16 is any u16 value; the function handles shifts >= 16 by returning min__u16.
3. min__u16 is any u16 value; no range constraint.

Post-conditions:
1. Returns a u16 value. If shift__u16 >= 16, the result is min__u16. Otherwise, the result is value__u16 >> shift__u16, clamped to at least min__u16 (i.e., if the shifted value is less than min__u16, min__u16 is returned instead).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a right bitshift with clamping to a minimum value. The implementation matches the semantic intent. The guard against shift__u16 >= 16 prevents undefined behavior (shifting a 16-bit value by its full width or more is undefined in C). The clamping logic ensures the result never falls below min__u16. The u8 and u32 variants follow the same pattern with their respective bit widths (8 and 32), confirming consistency across the family of functions.

Implementation Correctness:
Type compatibility — all parameters are u16, the shift operation is performed on u16 values, and the return type is u16. No implicit conversions or truncation.
Undefined behavior — the shift__u16 >= 16 guard prevents undefined behavior from shifting a 16-bit integer by 16 or more bits. No null dereference (no pointers used), no type punning, no out-of-bounds access.
Validation — the shift >= 16 check is appropriate validation for this function's role, as it prevents undefined behavior at the language level. No additional validation is needed.

Side Effects:
No side effects — this is a pure function that only computes and returns a value.