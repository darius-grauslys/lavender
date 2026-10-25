vector_3i32F20_to__vector_3i32F4 — core/include/vectors.h

Converts a Vector__3i32F20 (20-bit fixed-point) to a Vector__3i32F4 (4-bit fixed-point) by right-shifting each component by 16 bits, discarding the excess fractional precision.

Pre-conditions:
1. vector is passed by value; no pointer constraints apply. Any valid Vector__3i32F20 is acceptable.
2. Each component (x__i32F20, y__i32F20, z__i32F20) is a standard i32F20 (int32_t); no range constraint is required.

Post-conditions:
1. A new Vector__3i32F4 is returned with all three fields (x__i32F4, y__i32F4, z__i32F4) populated by converting the corresponding i32F20 components via i32F20_to__i32F4.
2. The original vector is not modified (input is taken by value).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly converts from 20-bit fractional precision to 4-bit fractional precision. The conversion i32F20_to__i32F4 right-shifts by 16 bits (FRACTIONAL_PERCISION_16__BIT_SIZE), which is exactly the difference 20 − 4 = 16. This preserves the integer portion and the top 4 fractional bits while discarding the lower 16 fractional bits. All three vector components are converted — no field is omitted. The returned struct is fully initialized.

Implementation Correctness:
Type compatibility — i32F20_to__i32F4 returns Signed_Index__i32 (int32_t), and the target struct fields are i32F4 (also int32_t). No implicit conversions or truncation occur.
Undefined behavior — none. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The ARITHMETRIC_R_SHIFT macro correctly handles right-shifting negative values (implementation-defined in standard C) by using arithmetic right shift semantics.
Validation — no validation is needed; this is a pure conversion function operating on a by-value parameter.

Side Effects:
No side effects. The function is pure: it takes its input by value, performs no memory writes, and returns a newly constructed Vector__3i32F4.
