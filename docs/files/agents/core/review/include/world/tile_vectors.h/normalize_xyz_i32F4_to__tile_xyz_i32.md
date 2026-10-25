normalize_xyz_i32F4_to__tile_xyz_i32 — core/include/world/tile_vectors.h

Converts a 32-bit fixed-point value with 4 fractional bits into a tile index by first stripping the fractional portion and then bit-shifting to extract the tile coordinate.

Pre-conditions:
1. xyz__i32F4 is a valid i32F4 value (int32_t with 4 bits of fractional precision). No null pointer concerns since the parameter is passed by value.

Post-conditions:
1. Returns an i32 tile index derived from the input by removing the 4-bit fractional component and then right-shifting by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3) bits.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its intent of converting an i32F4 fixed-point coordinate into a tile index. It first calls i32F4_to__i32 which performs an arithmetic right shift by FRACTIONAL_PERCISION_4__BIT_SIZE (4) to remove the fractional bits, then calls normalize_xyz_i32_to__tile_xyz_i32 which right-shifts by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3) to extract the tile index. The composition of these two operations correctly normalizes an i32F4 value to a tile coordinate.

Implementation Correctness:
Type compatibility — the parameter type i32F4 (int32_t) matches the expected type of i32F4_to__i32. The return type of i32F4_to__i32 is Signed_Index__i32 (int32_t), which matches the parameter type of normalize_xyz_i32_to__tile_xyz_i32 (i32). The final return type is i32, matching the function signature. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The arithmetic shifts are well-defined for all int32_t values via the ARITHMETRIC_R_SHIFT macro which handles negative numbers correctly.
No validation is needed — this is a pure arithmetic function with a value parameter. The caller is responsible for providing a meaningful i32F4 value.

Side Effects:
No side effects — this is a pure function that takes a value parameter and returns a computed result without modifying any state.
