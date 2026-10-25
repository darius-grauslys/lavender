multiply_u8__clamped — core/include/numerics.h

Multiplies two u8 values and clamps the result to a caller-specified upper bound, returning the clamp value if the product would overflow u8 or exceed the clamp.

Pre-conditions:
1. first__u8 is any u8 value (0–255); no null constraint (passed by value).
2. second__u8 is any u8 value (0–255); no null constraint (passed by value).
3. clamp__u8 is any u8 value (0–255); no null constraint (passed by value).

Post-conditions:
1. Returns a u8 that is the product of first__u8 and second__u8, clamped to clamp__u8 if the true product exceeds clamp__u8 or would overflow u8.
2. The return value is always <= clamp__u8.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to compute first__u8 * second__u8 and clamp the result to clamp__u8, returning clamp__u8 when the product overflows u8 or exceeds the clamp. The implementation partially fulfills this but contains a bug in the overflow detection.

The overflow check uses the heuristic: `(MAX__U8>>1) < first__u8 || (MAX__U8>>1) < second__u8`, which only catches cases where at least one operand exceeds 127 (MAX__U8>>1 = 127). This is insufficient. When both operands are <= 127 but their product exceeds 255 (MAX__U8), the multiplication overflows u8. In C, the expression `first__u8 * second__u8` is promoted to int (so the multiplication itself is correct), but the assignment `u8 multiple = first__u8 * second__u8` truncates the result to 8 bits, producing a wrapped value.

Concrete counterexample:
- multiply_u8__clamped(127, 127, 255):
  - Overflow check: 127 is NOT > 127, so no early return.
  - multiple = (u8)(127 * 127) = (u8)16129 = 25 (truncated).
  - 25 <= 255 (clamp), so returns 25.
  - Correct result should be 255 (since 16129 > 255, the product overflows u8 and should be clamped).
- multiply_u8__clamped(100, 100, 255):
  - Overflow check: 100 <= 127, no early return.
  - multiple = (u8)(100 * 100) = (u8)10000 = 16 (truncated).
  - 16 <= 255, so returns 16.
  - Correct result should be 255.

The sibling function add_u8__clamped uses a correct overflow check (`MAX__U8 - first__u8 < second__u8`), but multiply_u8__clamped does not follow the same pattern. A correct overflow check for u8 multiplication would be: `first__u8 != 0 && second__u8 > MAX__U8 / first__u8`.

Implementation Correctness:
- Type compatibility: Parameter types (u8) match the local variable type (u8). The multiplication first__u8 * second__u8 is performed in int (due to integer promotion), then implicitly truncated to u8 when assigned to `u8 multiple`. This truncation is the source of the bug.
- Undefined behavior: No undefined behavior per se — the truncation is well-defined (implementation-defined wraparound for unsigned), but the result is semantically incorrect.
- Validation: The overflow check is present but incorrect. A correct check is needed to detect when the product exceeds MAX__U8 before the truncation occurs.

Side Effects:
No side effects — the function is pure. It reads only its parameters and returns a computed u8 value without modifying any state.
