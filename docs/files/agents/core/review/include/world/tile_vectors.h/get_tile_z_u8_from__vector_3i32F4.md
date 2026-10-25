get_tile_z_u8_from__vector_3i32F4 — core/include/world/tile_vectors.h

Extracts the Z component from a 3D fixed-point vector (i32F4 format) and normalizes it to a tile index (u8).

Pre-conditions:
1. vector__3i32F4 is a valid Vector__3i32F4 struct (passed by value, so always valid).
2. No pointer parameters; no nullability concerns.
3. The Z component (z__i32F4) is any i32F4 value (int32_t); no range constraint is imposed by this function.

Post-conditions:
1. Returns an Index__u8 (uint8_t) representing the tile Z index derived from the input vector's Z component.
2. The returned value is the result of normalize_i32F4__to_tile_u8 applied to the Z component, which performs fixed-point-to-integer conversion and arithmetic masking to produce a tile-local index.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it extracts the Z component from a Vector__3i32F4 and normalizes it to a tile u8 index. The implementation is structurally identical to the sibling functions get_tile_x_u8_from__vector_3i32F4 and get_tile_y_u8_from__vector_3i32F4, differing only in which vector component is extracted. The delegation chain is:
  1. get_z_i32F4_from__vector_3i32F4 extracts z__i32F4 (returns i32F4 / int32_t).
  2. normalize_i32F4__to_tile_u8 converts the i32F4 to i32 (removing fractional bits) and then normalizes to a tile-local u8 index via arithmetic right shift and masking.
No semantic drift or computation mismatch exists.

Implementation Correctness:
Type compatibility — The parameter Vector__3i32F4 is passed by value (appropriate for a small struct). get_z_i32F4_from__vector_3i32F4 returns i32F4 (int32_t), which matches the parameter type of normalize_i32F4__to_tile_u8 (i32F4 / int32_t) exactly. The return type Index__u8 (uint8_t) matches normalize_i32F4__to_tile_u8's return type exactly. No implicit conversions or truncation occur within this function.
Undefined behavior — No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function operates entirely on value types.
Validation — No validation is needed. This is a low-level inline accessor/normalizer. The caller is responsible for providing a meaningful Vector__3i32F4.

Side Effects:
No side effects — the function is pure: it takes a value parameter and returns a computed value without modifying any state.
