lerp__i32F8 — core/include/numerics.h

Performs linear interpolation between two i32F8 fixed-point values using a third i32F8 value as the interpolation factor.

Pre-conditions:
1. one__i32F8 is any i32F8 (int32_t) fixed-point value.
2. two__i32F8 is any i32F8 (int32_t) fixed-point value.
3. x is any i32F8 (int32_t) fixed-point value; conventionally in the range [0, 256] (i.e., 0.0 to 1.0 in real-number terms), but no range is enforced.

Post-conditions:
1. Returns an i32F8 value representing the linear interpolation: one + (two - one) * x, computed in fixed-point arithmetic.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the standard fixed-point linear interpolation formula:

    result = one_fp + ((two_fp - one_fp) * x_fp) >> 8

In real-number terms, if one_fp = one * 256, two_fp = two * 256, and x_fp = t * 256, then:

    one_fp + ((two_fp - one_fp) * x_fp) >> 8
    = one*256 + ((two-one)*256 * t*256) / 256
    = (one + (two - one) * t) * 256

This is the correct fixed-point representation of lerp(one, two, t). The multiplication of two i32F8 values produces a product with 16 fractional bits; the arithmetic right shift by 8 (via i32F8_to__i32) restores it to 8 fractional bits, which is then added to one__i32F8 (already in 8-fractional-bit representation) to produce the final i32F8 result.

The sibling function lerp__i32F4 follows the identical pattern, confirming consistency in the codebase's fixed-point lerp implementation.

Implementation Correctness:
Type compatibility — all operands and return values are int32_t (i32F8 = int32_t, Signed_Index__i32 = int32_t). i32F8_to__i32 returns Signed_Index__i32, which is int32_t, matching i32F8. No implicit conversions, no truncation.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The ARITHMETRIC_R_SHIFT macro handles negative numbers correctly by checking the sign before shifting, avoiding implementation-defined behavior for right-shifting negative values.
Overflow — the multiplication (two__i32F8 - one__i32F8) * x can overflow for large input values. This is an inherent limitation of fixed-point arithmetic and is consistent with the codebase's approach (e.g., multiply__i32F8 has the same limitation and documents it with "Can only multiply values 0 <-> BIT(8).F8"). No clamping is performed, which is consistent with other functions in this header. This is a known design tradeoff, not a bug.
Validation — no validation is performed, which is appropriate for a low-level inline numeric utility. The caller is responsible for ensuring inputs are within acceptable ranges to avoid overflow.

Side Effects:
No side effects. The function is pure: it reads its three parameters and returns a computed value without modifying any state or accessing memory through pointers.
