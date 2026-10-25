get_z_i32_from__vector_3i32F4 — core/include/vectors.h

Extracts the z-component from a Vector__3i32F4 (fixed-point with 4 fractional bits) and converts it to a regular Signed_Index__i32 by arithmetic right-shifting by FRACTIONAL_PERCISION_4__BIT_SIZE (4) bits.

Pre-conditions:
1. vector__3i32F4 is a valid Vector__3i32F4 value (passed by value, so no null-check needed).

Post-conditions:
1. Returns the z-component of the input vector, converted from i32F4 fixed-point format to a plain Signed_Index__i32 by truncating the 4 fractional bits via arithmetic right shift.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its intent. It delegates to get_z_i32F4_from__vector_3i32F4 to extract the z field (vector__3i32F4.z__i32F4), then converts the i32F4 fixed-point value to a Signed_Index__i32 via i32F4_to__i32, which performs an arithmetic right shift by 4 bits. This is consistent with the sibling functions get_x_i32_from__vector_3i32F4 and get_y_i32_from__vector_3i32F4, which follow the same pattern for their respective components.

Implementation Correctness:
Type compatibility — i32F4 and Signed_Index__i32 are both typedefs of int32_t, so there are no implicit conversions or truncation issues. The return type Signed_Index__i32 matches the return type of i32F4_to__i32.
No undefined behavior — the function takes its parameter by value (no pointer dereference), and the arithmetic right shift is performed safely via the ARITHMETRIC_R_SHIFT macro which handles negative values correctly.
No validation is needed — this is a pure accessor/conversion function. The caller is responsible for providing a valid vector.

Side Effects:
No side effects.
