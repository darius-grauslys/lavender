get_tile_vector_using__3i32F4 — core/include/world/tile_vectors.h

Converts a 3D fixed-point position vector (Vector__3i32F4) into a tile vector (Tile_Vector__3i32) by delegating to get_tile_vector_using__i32F4, which normalizes each component from i32F4 (4-bit fractional) to a tile index via two right-shifts: first removing the 4 fractional bits (i32F4_to__i32), then shifting by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3) to obtain the tile coordinate.

Pre-conditions:
1. position__3i32F4 is a valid Vector__3i32F4 struct passed by value; no null-pointer concern.
2. Each field (x__i32F4, y__i32F4, z__i32F4) is of type i32F4 (int32_t); any bit pattern is acceptable as input — no range constraint required.

Post-conditions:
1. Returns a Tile_Vector__3i32 whose x, y, and z fields are the tile indices derived from the corresponding i32F4 components of the input vector.
2. The returned Tile_Vector__3i32 is a fresh value; no mutation of the input occurs.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly extracts all three components (x, y, z) from the input Vector__3i32F4 and passes them, in order, to get_tile_vector_using__i32F4. No component is omitted or reordered. The return type (Tile_Vector__3i32) matches the return type of the delegated function. The delegation is semantically identical to the alternative vector_3i32F4_to__tile_vector function which performs the same computation inline, confirming the intent is correct.

Implementation Correctness:
Type compatibility — position__3i32F4.x__i32F4, .y__i32F4, and .z__i32F4 are all of type i32F4 (int32_t), which exactly matches the parameter types of get_tile_vector_using__i32F4 (i32F4 x, i32F4 y, i32F4 z). No implicit conversions or truncation occur.
Undefined behavior — none. The input is passed by value (no null dereference risk). No pointer arithmetic, no type punning, no out-of-bounds access. The function is a pure delegation wrapper.
Validation — no validation is needed. This is a low-level conversion function; validating i32F4 values for range is not the function's responsibility. The caller is responsible for providing meaningful input.

Side Effects:
No side effects — the function is pure. It reads the input struct by value, delegates to get_tile_vector_using__i32F4, and returns a new Tile_Vector__3i32 without modifying any state.
