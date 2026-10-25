subtract_u16__clamped — core/include/numerics.h

Subtracts two unsigned 16-bit integers with underflow protection and clamps the result to a minimum value.

Pre-conditions:
1. first__u16 is any u16 (uint16_t) value — no range constraint.
2. second__u16 is any u16 (uint16_t) value — no range constraint.
3. min__u16 is any u16 (uint16_t) value — no range constraint; serves as the floor (minimum) for the result.

Post-conditions:
1. Returns a u16 value that is the result of (first__u16 - second__u16), clamped so it never falls below min__u16 and never underflows past zero.
2. If first__u16 < second__u16 (subtraction would underflow), returns min__u16.
3. If (first__u16 - second__u16) < min__u16, returns min__u16.
4. Otherwise, returns (first__u16 - second__u16).

Correctness Verdict: Incorrect

Semantic Alignment:
The function name and parameter name (min__u16) indicate the intent is to clamp the subtraction result to a minimum value — i.e., result = max(min__u16, first__u16 - second__u16). However, the implementation uses the wrong comparison operator. On line 255, the code checks `if (subtraction > min__u16)` and returns `min__u16` in that case. This means:
- When the subtraction result is GREATER than min__u16, it incorrectly returns min__u16 (clamping down to the minimum, as if it were a maximum).
- When the subtraction result is LESS than min__u16, it incorrectly returns the subtraction result (allowing values below the stated minimum).

This is the opposite of the intended minimum-clamp semantic. The comparison should be `if (subtraction < min__u16)` to properly clamp the result to the minimum value.

The same bug pattern exists in the sibling functions subtract_u8__clamped (line 240) and subtract_u32__clamped (line 270), which use the identical incorrect `>` comparison.

Implementation Correctness:
Type compatibility — all parameters are u16 (uint16_t) and all operations are performed in u16 arithmetic. The local variable `subtraction` is also u16. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The underflow check on line 251 (`if (first__u16 < second__u16)`) correctly prevents unsigned underflow before the subtraction is performed.
No validation is needed — this is a pure arithmetic function. The caller is responsible for ensuring the parameters are meaningful.
The only issue is the incorrect comparison operator (`>` instead of `<`) on line 255, which inverts the clamping logic.

Side Effects:
No side effects — this is a pure function that computes and returns a value without modifying any external state.
