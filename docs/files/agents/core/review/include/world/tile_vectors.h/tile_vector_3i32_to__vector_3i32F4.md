tile_vector_3i32_to__vector_3i32F4 — core/include/world/tile_vectors.h, lines 154-163

Converts a Tile_Vector__3i32 (tile indices) into a Vector__3i32F4 (F4 fixed-point pixel positions) by shifting each tile index left by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3) to obtain pixel coordinates, then passing those to get_vector__3i32F4_using__i32 which shifts left by FRACTIONAL_PERCISION_4__BIT_SIZE (4) to convert pixel positions to F4 representation.

Pre-conditions:
1. tile_vector__3i32 is a Tile_Vector__3i32 (typedef for Vector__3i32) containing tile indices in its x__i32, y__i32, z__i32 fields.
2. The tile indices should be within a range that does not cause overflow when shifted left by 7 bits (3 for tile-to-pixel + 4 for pixel-to-F4). The function does not validate this; it is the caller's responsibility.

Post-conditions:
1. Returns a Vector__3i32F4 where each component is the corresponding tile index shifted left by (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + FRACTIONAL_PERCISION_4__BIT_SIZE) = 7 bits, representing the tile's pixel position in F4 fixed-point format.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly converts tile indices to F4 pixel positions. The two-step shift (<<3 for tile-to-pixel, then <<4 for pixel-to-F4 via get_vector__3i32F4_using__i32) matches the equivalent composition vector_3i32_to__vector_3i32F4(tile_vector_3i32_to__vector_3i32(tile_vector__3i32)), which is the same pattern used by the analogous chunk_vector_3i32_to__vector_3i32F4 function (chunk_vectors.h, line 162-166). Each component is independently and correctly transformed. No struct fields are omitted or reordered.

Implementation Correctness:
- Type compatibility: Tile_Vector__3i32 is a typedef for Vector__3i32, whose fields are Signed_Index__i32 (int32_t). The left-shifted values remain int32_t, which is compatible with the i32F4 (int32_t) parameters of get_vector__3i32F4_using__i32. No implicit conversions or truncation.
- No undefined behavior: The left shifts are well-defined for reasonable tile index values. No pointer dereference, no type punning, no array or out-of-bounds access.
- No validation needed: This is a low-level conversion function operating on a value parameter. Validation of tile indices is the caller's responsibility.

Side Effects:
No side effects. The function is a pure computation — it takes a value parameter and returns a new Vector__3i32F4 without modifying any external state.
