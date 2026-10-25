vector_3i32F4_to__vector_3i16F8 — core/include/vectors.h

Converts a Vector__3i32F4 (32-bit fixed-point with 4 fractional bits) to a Vector__3i16F8 (16-bit fixed-point with 8 fractional bits) by shifting each component left by 4 bits.

Pre-conditions:
1. The function takes its parameter by value; no pointer preconditions apply.
2. vector.x__i32F4, vector.y__i32F4, and vector.z__i32F4 are any valid i32F4 (int32_t) values; no range constraint is enforced by the function.

Post-conditions:
1. Returns a Vector__3i16F8 whose x__i16F8, y__i16F8, and z__i16F8 fields are derived from the corresponding i32F4 components shifted left by 4 bits.
2. Values that exceed the representable range of i16F8 (int16_t) will be silently truncated due to implicit narrowing conversion.

Correctness Verdict: Incorrect

Semantic Alignment:
The mathematical conversion is correct in principle: to convert from i32F4 (4 fractional bits) to i16F8 (8 fractional bits), the value should be shifted left by (8 - 4) = 4 bits, which is what FRACTIONAL_PERCISION_4__BIT_SIZE (4) achieves. The function correctly accesses all three components (x, y, z) and maps them to the corresponding fields of the result struct. No struct fields are omitted or reordered.

However, the implementation uses the raw `<<` operator on signed int32_t (i32F4) values. Left-shifting a signed integer is undefined behavior in C (C11 §6.5.7.4) when the operand is negative or when the result overflows the signed integer type. The codebase explicitly provides the ARITHMETRIC_L_SHIFT macro in core/include/numerics.h to handle this safely:

    #define ARITHMETRIC_L_SHIFT(x, n)\
        ((i32)((u32)(x) << (n)))

This macro casts to u32 first, performs the shift, then casts back to i32, avoiding undefined behavior. Other conversion functions in the codebase (e.g., i32_to__i32F4, i32F4_to__i32F20) correctly use these arithmetic shift macros. This function does not, which is a bug.

Implementation Correctness:
Type compatibility — The function operates on i32F4 (int32_t) values and produces a result that is implicitly narrowed to i16F8 (int16_t) fields. The narrowing conversion is expected given the different bit widths, but it is not made explicit with a cast, which could obscure the truncation.

Undefined behavior — The `<<` operator is applied directly to signed i32F4 values. For negative inputs, this invokes undefined behavior in C. The ARITHMETRIC_L_SHIFT macro should be used instead to perform the shift on the unsigned representation.

Validation — No validation is needed; this is a low-level conversion function. Range checking/truncation handling would be the caller's responsibility.

Side Effects:
No side effects. The function is pure: it takes a value parameter, performs a computation, and returns a new struct. No memory is mutated, no I/O occurs, and no global state is accessed.
