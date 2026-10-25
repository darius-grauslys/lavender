tile_vector_3i32_to__vector_3i32 — core/include/world/tile_vectors.h

Converts a Tile_Vector__3i32 (tile indices) into a Vector__3i32 (world/pixel coordinates) by multiplying each component by the tile size in pixels (BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT) = 8).

Pre-conditions:
1. tile_vector__3i32 is passed by value; no null-pointer or writability constraint applies.
2. Each field (x__i32, y__i32, z__i32) is of type Signed_Index__i32 (int32_t) and may be negative, zero, or positive. No range constraint is enforced by this function.

Post-conditions:
1. Returns a Vector__3i32 whose x, y, and z components are each equal to the corresponding tile index left-shifted by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (i.e., multiplied by 8).
2. The returned vector is the inverse of normalize_xyz_i32_to__tile_xyz_i32 (which right-shifts by the same amount).

Correctness Verdict: Correct

Semantic Alignment:
The computation correctly fulfills the semantic intent: converting tile indices to pixel/world coordinates by multiplying each component by the tile size in pixels (8). Each component is left-shifted by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3), which is equivalent to multiplying by BIT(3) = 8. This is the proper inverse of normalize_xyz_i32_to__tile_xyz_i32, which right-shifts by the same amount to convert pixel coordinates back to tile indices. Tile_Vector__3i32 and Vector__3i32 are the same underlying type (struct Vector__3i32_t), so no data loss or reinterpretation occurs in the type conversion.

Implementation Correctness:
- Type compatibility: tile_vector__3i32.x__i32 is Signed_Index__i32 (int32_t); left-shifting by 3 yields a value of type int (promoted), which is implicitly compatible with the Signed_Index__i32 parameter expected by get_vector__3i32. No truncation or implicit conversions occur.
- Undefined behavior: The function uses raw `<<` on Signed_Index__i32 (a signed int32_t). Left-shifting a negative signed integer is undefined behavior in C. The codebase provides the ARITHMETRIC_L_SHIFT macro in numerics.h specifically to avoid this (it casts to u32 before shifting). The sibling function tile_vector_3i32_to__vector_3i32F4 in the same file has the same pattern, while chunk_vector_3i32_to__vector_3i32 in chunk_vectors.h correctly uses ARITHMETRIC_L_SHIFT for the same operation. This inconsistency should be addressed by using ARITHMETRIC_L_SHIFT for consistency and to eliminate UB for negative tile coordinates.
- Validation: No validation is needed — this is a low-level conversion function. The caller is responsible for ensuring the input is valid.

Side Effects:
No side effects. The function is pure: it takes a Tile_Vector__3i32 by value and returns a new Vector__3i32 without modifying any global or external state.
