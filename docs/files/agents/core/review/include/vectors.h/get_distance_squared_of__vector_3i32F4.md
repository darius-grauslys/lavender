get_distance_squared_of__vector_3i32F4 — core/include/vectors.h

Computes the squared Euclidean distance (magnitude squared) of a 3D vector whose components are i32F4 fixed-point values (int32_t with 4 fractional bits), returning the result in i32F4 format.

Pre-conditions:
1. vector__3i32F4 is passed by value; no pointer validity concerns.
2. No constraints on the component values — they may be any valid i32F4 (int32_t) values, including negative numbers.

Post-conditions:
1. Returns an i32F4 value representing x² + y² + z², where each component is interpreted as a fixed-point number with 4 fractional bits. The returned value is also in i32F4 format (4 fractional bits).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the squared distance of a 3D vector. The fixed-point arithmetic is sound:
- Each component (x__i32F4, y__i32F4, z__i32F4) is i32F4 — an int32_t scaled by 2^4 (4 fractional bits).
- Squaring a component (e.g., x__i32F4 * x__i32F4) produces a product with 8 fractional bits (scaled by 2^8).
- Summing three such products preserves the 8-fractional-bit scale.
- The final right shift by FRACTIONAL_PERCISION_4__BIT_SIZE (4) restores the i32F4 (4-fractional-bit) scale, matching the declared return type i32F4.

This approach is actually more precise than calling multiply__i32F4 three times and summing, because it performs a single right shift at the end rather than truncating each product individually before summing.

Implementation Correctness:
Type compatibility — the parameter is Vector__3i32F4 (a struct of three i32F4 fields), and the return type is i32F4. All field accesses (x__i32F4, y__i32F4, z__i32F4) match the struct definition. The >> operator is applied to an int32_t (i32F4), and FRACTIONAL_PERCISION_4__BIT_SIZE is 4 (an int), which is a valid shift amount.
Undefined behavior — the >> operator on a signed negative int32_t is implementation-defined in C (not strictly undefined, but implementation-defined). The codebase provides an ARITHMETRIC_R_SHIFT macro for this purpose (used in i32F4_to__i32), but this function uses >> directly. This is consistent with other functions in the same file (e.g., vector_3i32F4_to__vector_3u8 uses >> directly). Most compilers implement arithmetic right shift for signed types, making this a minor portability concern rather than a correctness issue.
Integer overflow — multiplication of two i32F4 values and subsequent addition can overflow int32_t. This is a known limitation shared with multiply__i32F4 and other functions in the codebase (e.g., is_vector_3i32F4_within__distance_i32F4). No overflow checking is performed, which is consistent with the function's role as a low-level math helper.
Validation — no validation is needed; this is a pure computation function. The caller is responsible for ensuring inputs are within acceptable ranges.

Side Effects:
No side effects — the function is pure. It reads the input vector by value and returns a computed result without modifying any state.
