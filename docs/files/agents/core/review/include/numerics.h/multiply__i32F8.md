multiply__i32F8 — core/include/numerics.h, lines 592-598

Fixed-point multiplication of two i32F8 (8.8 fractional) values, returning the product in i32F8 format.

Pre-conditions:
1. x and y are i32F8 values (int32_t typedef) representing fixed-point numbers with 8 fractional bits.
2. Per the doc comment, the raw F8 values of x and y must each be in the range [0, BIT(8)] (i.e., [0, 256]) to prevent signed integer overflow in the intermediate product x * y. BIT(8) = 256 (from defines_weak.h: #define BIT(n) ((1U) << (n))).
3. Both parameters are passed by value; no pointer constraints apply.

Post-conditions:
1. Returns an i32F8 value equal to (x * y) >> 8, computed via i32F8_to__i32 which applies ARITHMETRIC_R_SHIFT(x, FRACTIONAL_PERCISION_8__BIT_SIZE) — an arithmetic right shift by 8 bits that correctly handles negative operands.
2. The returned value is the correct fixed-point product: if x represents a/256 and y represents b/256, the result represents (a*b)/256 in F8 format.
3. The function does not modify any global state or caller-owned memory.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs fixed-point multiplication for the F8 format. When multiplying two F8 fixed-point numbers, the raw integer product x * y contains 16 fractional bits (8 from each operand). Right-shifting by 8 removes the excess fractional bits, yielding the correct F8 result. The use of i32F8_to__i32 (which delegates to ARITHMETRIC_R_SHIFT) ensures correct behavior for negative values. The doc comment's constraint "0 <-> BIT(8)" documents the safe input range to avoid signed overflow in the intermediate x * y multiplication. This matches the analogous pattern used by multiply__i32F4 (which constrains inputs to BIT(12) for F4 format). The computation matches the semantic intent of fixed-point multiplication.

Implementation Correctness:
Type compatibility — x and y are i32F8 (int32_t); the multiplication x * y is performed in int32_t arithmetic. i32F8_to__i32 returns Signed_Index__i32 (also int32_t), and the function returns i32F8 (int32_t). All types are identical at the underlying level; no implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The only potential UB is signed integer overflow in x * y if inputs exceed the documented safe range, but this is the caller's responsibility per the documented pre-condition.
Validation — no runtime validation is performed, which is appropriate for a low-level inline fixed-point arithmetic helper. The overflow constraint is documented in the doc comment rather than enforced.

Side Effects:
No side effects. The function is a pure computation that reads only its two by-value parameters and returns a result.
