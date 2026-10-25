get_tile_x_u8_from__vector_3i32F4 — core/include/world/tile_vectors.h

Extracts the X component (as i32F4) from a 3D fixed-point vector and normalizes it to a local u8 tile index within a chunk.

Pre-conditions:
1. vector__3i32F4 is passed by value; no null check is required.
2. The x component (x__i32F4) is a valid i32F4 fixed-point value (int32_t with 4 fractional bits) representing a world-space coordinate.

Post-conditions:
1. Returns an Index__u8 (uint8_t) representing the local tile index along the X axis within a chunk.
2. The result is in the range [0, 7], masked to 3 bits via MASK(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT) where CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT = 3.

Correctness Verdict: Incorrect

Semantic Alignment:
The function correctly delegates to get_x_i32F4_from__vector_3i32F4 to extract the x component, and then to normalize_i32F4__to_tile_u8 to convert the i32F4 value to a local tile index. The delegation chain is correct: get_x_i32F4_from__vector_3i32F4 returns the x__i32F4 field (type i32F4 = int32_t), and normalize_i32F4__to_tile_u8 accepts an i32F4. However, the underlying helper normalize_i32__to_tile_u8 (called by normalize_i32F4__to_tile_u8) contains an off-by-one bug that causes this function to produce incorrect results for certain inputs.

The bug is in normalize_i32__to_tile_u8, which computes:
  ARITHMETRIC_MASK(ARITHMETRIC_R_SHIFT(x, 3) - (x < 0), MASK(3))

The ARITHMETRIC_R_SHIFT macro performs truncation toward zero for negative numbers (not floor). The "- (x < 0)" term is intended to convert truncation toward zero into floor division, but it over-corrects for negative values that are exact multiples of the tile size (8). For exact multiples of 8, ARITHMETRIC_R_SHIFT already produces the correct floor value, so subtracting an additional 1 produces floor(x/8) - 1 instead of floor(x/8).

Concrete example: an X position of -8.0 (i32F4 = -128):
- i32F4_to__i32(-128) = -8 (no correction applied since -x = 128 >= BIT(4) = 16)
- normalize_i32__to_tile_u8(-8):
  - ARITHMETRIC_R_SHIFT(-8, 3) = -((8) >> 3) = -1 (already correct floor of -8/8 = -1)
  - -1 - (x < 0) = -1 - 1 = -2 (over-corrected; should remain -1)
  - ARITHMETRIC_MASK(-2, 7) = ((8 - (2 & 7)) & 7) = 6
- Expected: floor(-8/8) mod 8 = (-1) mod 8 = 7
- Actual: 6

The same off-by-one affects all negative positions that are exact multiples of 8 (e.g., -8.0, -16.0, -24.0), producing a tile index one less than the correct value. Non-multiple negative positions (e.g., -7.0, -9.0) are handled correctly.

Implementation Correctness:
Type compatibility — get_x_i32F4_from__vector_3i32F4 returns Signed_Index__i32 (int32_t), and normalize_i32F4__to_tile_u8 accepts i32F4 (int32_t). Both are int32_t; no implicit conversion or truncation occurs. The return type Index__u8 (uint8_t) matches the return type of normalize_i32F4__to_tile_u8. No type issues.
No undefined behavior — the function takes a value parameter (no null dereference), performs no pointer arithmetic, no type punning, and no out-of-bounds access. The ARITHMETRIC_MASK and ARITHMETRIC_R_SHIFT macros operate on well-defined int32_t values.
No validation needed — this is a low-level inline computation function. The caller is responsible for providing a valid Vector__3i32F4.

Side Effects:
No side effects. This is a pure function — it takes a value parameter and returns a computed Index__u8 without modifying any state.
