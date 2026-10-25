lerp__xy__i32F8 — core/include/numerics.h

Bilinear interpolation between four i32F8 fixed-point corner values using x and y interpolation factors.

Pre-conditions:
1. v__00, v__10, v__01, v__11 are i32F8 (int32_t with 8 fractional bits) corner values.
2. x and y are i32F8 interpolation factors; semantically expected to be in the range [0, 256] (representing [0.0, 1.0] in fixed-point), but no runtime validation is performed.
3. No pointer parameters; all arguments are passed by value.

Post-conditions:
1. Returns an i32F8 value representing the bilinearly interpolated result: lerp_y(lerp_x(v00, v10, x), lerp_x(v01, v11, x), y).

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly performs bilinear interpolation by first interpolating along the x-axis between v__00 and v__10, and between v__01 and v__11, then interpolating the two results along the y-axis. This matches the standard bilinear interpolation formula. The function follows the exact same structure as lerp__xy__i32F4 (the 4-bit fractional counterpart), confirming consistency across fixed-point precisions.

Implementation Correctness:
Type compatibility — all parameters and return values are i32F8 (int32_t). The nested calls to lerp__i32F8 receive i32F8 arguments and return i32F8, which is type-compatible. The i32F8_to__i32 helper returns Signed_Index__i32 (also int32_t), so no implicit conversions or truncation occur.
Undefined behavior — no pointer arithmetic, no null dereference (no pointers), no type punning, no out-of-bounds access. Integer overflow in the intermediate multiplication (two - one) * x is a known limitation of the fixed-point approach, consistent with lerp__i32F8 and lerp__xy__i32F4.
No validation is needed at this level — this is a low-level math helper. The caller is responsible for ensuring x and y are within the expected [0, 256] range.

Side Effects:
No side effects — this is a pure function with no memory access, no pointer dereferences, and no observable state changes.
