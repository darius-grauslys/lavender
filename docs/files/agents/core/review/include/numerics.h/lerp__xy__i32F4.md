lerp__xy__i32F4 — core/include/numerics.h

Bilinear interpolation between four i32F4 (4-bit fixed-point) corner values using fixed-point interpolation parameters x and y.

Pre-conditions:
1. v__00, v__10, v__01, v__11 are i32F4 fixed-point values representing the four corners of a bilinear grid.
2. x is an i32F4 fixed-point value in the range [0, 16] representing the horizontal interpolation parameter (0 = 0.0, 16 = 1.0 in 4-bit fractional).
3. y is an i32F4 fixed-point value in the range [0, 16] representing the vertical interpolation parameter (0 = 0.0, 16 = 1.0 in 4-bit fractional).
4. All parameters are plain values (no pointers), so no null-check is required.

Post-conditions:
1. Returns an i32F4 value representing the bilinearly interpolated result: lerp(lerp(v__00, v__10, x), lerp(v__01, v__11, x), y).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs bilinear interpolation. It first interpolates along the top edge (v__00 to v__10) using x, then along the bottom edge (v__01 to v__11) using x, and finally interpolates vertically between the two edge results using y. This is the standard bilinear interpolation formula.

The underlying lerp__i32F4 computes: one + ((two - one) * x) >> 4, which is correct for fixed-point arithmetic where x is in [0, 1] (represented as 0 to 16 in i32F4). The multiplication of two i32F4 values produces a result with 8 fractional bits; the right-shift by 4 (via i32F4_to__i32) reduces it to 4 fractional bits, making it compatible for addition with the i32F4 'one' operand.

Implementation Correctness:
Type compatibility — all parameters and the return type are i32F4 (int32_t). The intermediate results from lerp__i32F4 are also i32F4, so all types match exactly. i32F4_to__i32 returns Signed_Index__i32 (also int32_t), which is compatible with i32F4 for the addition. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The arithmetic right-shift on negative numbers is handled by the ARITHMETRIC_R_SHIFT macro, which correctly computes -( (-x) >> n ) for negative values.
No validation needed — this is a pure arithmetic function with no resource management. The caller is responsible for providing valid fixed-point parameters.

Side Effects:
No side effects — the function is a pure computation that returns a value without modifying any state.
