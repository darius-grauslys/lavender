vector_3i32F4_to__local_tile_vector_3u8 — core/include/world/tile_vectors.h

Converts a 3D fixed-point position (Vector__3i32F4, 4 fractional bits) into a local tile vector (Local_Tile_Vector__3u8), yielding the per-axis tile index local to a chunk.

Pre-conditions:
1. vector__3i32F4 is a valid Vector__3i32F4 value (passed by value, no pointer constraints).
2. Each component (x__i32F4, y__i32F4, z__i32F4) is an i32F4 (int32_t with 4 fractional bits); no range constraint beyond what fits in i32F4.

Post-conditions:
1. Returns a Local_Tile_Vector__3u8 (a Vector__3u8 with fields x__u8, y__u8, z__u8) where each field holds the local tile index within a chunk for the corresponding axis.
2. The x, y, z components of the result correspond to the x, y, z components of the input respectively — no reordering.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly converts a Vector__3i32F4 to a Local_Tile_Vector__3u8 by delegating to three axis-specific helpers (get_tile_x_u8_from__vector_3i32F4, get_tile_y_u8_from__vector_3i32F4, get_tile_z_u8_from__vector_3i32F4). Each helper extracts the corresponding i32F4 component, converts it to an i32 via i32F4_to__i32 (right-shift by FRACTIONAL_PERCISION_4__BIT_SIZE), applies negative-value floor adjustment, then normalizes to a local tile index via normalize_i32__to_tile_u8 (right-shift by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT, then mask with MASK(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)). The total computation yields (i32F4_value >> 7) & 0x7, which is the tile index modulo chunk size — the correct local tile index within a chunk.

The struct initializer (Local_Tile_Vector__3u8){...} assigns all three fields (x__u8, y__u8, z__u8) in declaration order, matching the struct definition of Vector__3u8: { Index__u8 x__u8, y__u8, z__u8; }. No member is omitted and no reordering occurs.

Implementation Correctness:
Type compatibility — the helper functions return Index__u8 (uint8_t), and the struct fields x__u8, y__u8, z__u8 are Index__u8. Types match exactly with no implicit conversions or truncation.
Undefined behavior — none. No pointer arithmetic, no null dereference (function takes value parameters), no type punning, no out-of-bounds access. The ARITHMETRIC_MASK and ARITHMETRIC_R_SHIFT macros handle negative values safely.
Validation — not needed. This is a low-level static inline helper; validation is the caller's responsibility.

Side Effects:
No side effects. The function is pure — it takes a value parameter and returns a new struct without modifying any external state.
