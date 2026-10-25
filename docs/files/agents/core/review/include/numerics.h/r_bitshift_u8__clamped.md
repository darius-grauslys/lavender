r_bitshift_u8__clamped — core/include/numerics.h

Performs a right bit-shift on a u8 value, clamping the result to a minimum value. If the shift amount is greater than or equal to 8 (the bit width of u8), returns the minimum directly to avoid undefined behavior.

Pre-conditions:
1. value__u8: Any valid u8 value (0–255). No constraints.
2. shift__u8: Any valid u8 value (0–255). The function handles all cases safely.
3. min__u8: Any valid u8 value (0–255). No constraints.

Post-conditions:
1. Returns a u8 value.
2. If shift__u8 >= 8, returns min__u8.
3. If shift__u8 < 8 and (value__u8 >> shift__u8) < min__u8, returns min__u8.
4. Otherwise, returns (value__u8 >> shift__u8).
5. The result is always >= min__u8.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly performs a right bit-shift with clamping to a minimum floor. The guard `shift__u8 >= 8` prevents undefined behavior — shifting by an amount greater than or equal to the operand's bit width is undefined in C. For shifts 0–7, right-shifting an unsigned 8-bit value is well-defined. The clamping logic (`if (shifted < min__u8) return min__u8`) correctly ensures the result never falls below the specified minimum. The function is consistent with its u16 and u32 counterparts (r_bitshift_u16__clamped and r_bitshift_u32__clamped), which guard against shifts >= 16 and >= 32 respectively.

Implementation Correctness:
Type compatibility — all parameters are u8, the return type is u8, and the intermediate variable `shifted` is u8. No implicit conversions or truncation occur.
Undefined behavior — the check `shift__u8 >= 8` prevents shifting by an amount >= the bit width, which would be undefined behavior. For shifts 0–7, right-shifting unsigned values is well-defined per the C standard.
No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
Validation — the shift guard is an appropriate and necessary safety check for this function's role. It is not the caller's responsibility to prevent UB from excessive shift amounts.

Side Effects:
No side effects. This is a pure function — it takes inputs and returns a result without modifying any state or observable side effects.
