vector_3i32F4_to__tile_vector — core/include/world/tile_vectors.h, lines 115-122

Converts a fixed-point 3D vector (i32F4, 4 fractional bits) into a tile vector by first stripping the fractional component via arithmetic right shift (i32F4_to__i32, shift by 4), then normalizing the resulting integer coordinate to a tile index via right shift by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3). Each of the three components (x, y, z) is processed identically and independently.

Pre-conditions:
1. vector is a Vector__3i32F4 passed by value; no pointer to validate, no null check required.
2. Each field (x__i32F4, y__i32F4, z__i32F4) is an i32F4 (int32_t) holding a fixed-point value with 4 fractional bits. No range constraint is imposed by this function; any int32_t value is accepted.

Post-conditions:
1. Returns a Tile_Vector__3i32 (typedef of Vector__3i32) whose x__i32, y__i32, and z__i32 fields each hold the tile index computed from the corresponding input component.
2. The returned struct is fully initialized — all three fields are assigned.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of converting a fixed-point world-space vector into a tile-space vector. The function correctly delegates each component to normalize_xyz_i32F4_to__tile_xyz_i32, which first converts the i32F4 value to a plain i32 via i32F4_to__i32 (arithmetic right shift by FRACTIONAL_PERCISION_4__BIT_SIZE = 4), then normalizes to tile coordinates via normalize_xyz_i32_to__tile_xyz_i32 (right shift by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT = 3). This is the correct two-step conversion: fixed-point-to-integer, then integer-to-tile-index.
All three struct fields of Tile_Vector__3i32 (x__i32, y__i32, z__i32) are assigned in declaration order — no member is omitted, no reordering occurs.
This function is semantically consistent with the sibling get_tile_vector_using__3i32F4 / get_tile_vector_using__i32F4, which perform the identical conversion via the same normalize_xyz_i32F4_to__tile_xyz_i32 callee.

Implementation Correctness:
Type compatibility — vector.x__i32F4 is i32F4 (int32_t); normalize_xyz_i32F4_to__tile_xyz_i32 takes i32F4 and returns i32 (int32_t); Tile_Vector__3i32 fields are Signed_Index__i32 (int32_t). All types match exactly with no implicit conversions or truncation.
No undefined behavior — the function itself performs no pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access. The parameter is passed by value (a struct), so there is no pointer to dereference.
No validation is needed or appropriate for this function's role — it is a pure computational conversion. The caller is responsible for ensuring the input values are meaningful.
Note: The callee normalize_xyz_i32_to__tile_xyz_i32 uses the plain >> operator on a signed i32, which is implementation-defined for negative operands in C prior to C23. The codebase elsewhere uses the ARITHMETRIC_R_SHIFT macro to handle this consistently, but that macro is not used in normalize_xyz_i32_to__tile_xyz_i32. This is a concern in the callee, not in the function under review itself; the function under review correctly delegates to the existing conversion pipeline.

Side Effects:
No side effects. The function is pure — it takes a struct by value and returns a newly constructed struct. No memory is read or written beyond the local computation.
