normalize_xyz_i32F20_to__tile_xyz_i32 — core/include/world/tile_vectors.h, lines 24-27

Converts an i32F20 fixed-point position value to a tile index by first converting to integer (shift right by 20 fractional bits) and then converting pixels to tiles (shift right by 3 bits, since each tile is 8 pixels = BIT(3)).

Pre-conditions:
1. xyz__i32F20 is any valid i32F20 value (int32_t). No null pointer or range constraints.

Post-conditions:
1. Returns an i32 tile index.
2. For non-negative values, the result correctly computes floor(xyz__i32F20 / 2^23).
3. For negative values with fractional parts (i.e., values not exact multiples of 2^20), the result is incorrect due to truncation toward zero in the i32F20_to__i32 conversion step, which is not corrected by the subsequent shift.

Correctness Verdict: Incorrect

Semantic Alignment:
The function intends to convert an i32F20 position to a tile index using floor division by (8 * 2^20) = 2^23. However, the two-step conversion does not correctly implement floor division for negative values with fractional parts.

The pipeline is:
  1. i32F20_to__i32(xyz__i32F20) — uses ARITHMETRIC_R_SHIFT(x, 20), which for negative x computes -(abs(x) >> 20), i.e., truncation toward zero (not floor).
  2. normalize_xyz_i32_to__tile_xyz_i32(result) — uses plain `result >> 3` (implementation-defined for signed negatives; not portable).

For non-negative inputs, trunc = floor, so the result is correct. For negative inputs with fractional parts, the truncation in step 1 rounds toward zero (upward for negatives), and step 2 cannot recover the lost fractional information. Concrete counterexamples:

- xyz__i32F20 = -524288 (-0.5 in world coords):
  Step 1: i32F20_to__i32(-524288) = -(524288 >> 20) = -(0) = 0
  Step 2: 0 >> 3 = 0
  Expected: floor(-524288 / 2^23) = floor(-0.0625) = -1
  Result: 0 (incorrect)

- xyz__i32F20 = -8388609 (-8.000000954 in world coords):
  Step 1: i32F20_to__i32(-8388609) = -(8388609 >> 20) = -(8) = -8
  Step 2: -8 >> 3 = -1 (assuming arithmetic shift)
  Expected: floor(-8388609 / 2^23) = floor(-1.000000119) = -2
  Result: -1 (incorrect)

The chunk counterpart normalize_xyz_i32F4_to__chunk_xyz_i32 in chunk_vectors.h avoids this class of bug by:
  - Using ARITHMETRIC_R_SHIFT with `- (x < 0)` floor correction in its base function (normalize_xyz_i32_to__chunk_xyz_i32).
  - Adding a small-negative correction term: -(xyz__i32F4 < 0 && -xyz__i32F4 < BIT(FRACTIONAL_PERCISION_4__BIT_SIZE)).

The u8 counterpart normalize_i32F4__to_tile_u8 in the same file similarly uses ARITHMETRIC_R_SHIFT with `- (x < 0)` correction and a small-negative correction.

The tile_xyz base function normalize_xyz_i32_to__tile_xyz_i32 uses plain `>>` without any floor correction, and neither normalize_xyz_i32F4_to__tile_xyz_i32 nor normalize_xyz_i32F20_to__tile_xyz_i32 include the small-negative correction. This is an inconsistency with both the chunk and u8 counterparts.

Implementation Correctness:
- Type compatibility: All types are int32_t. i32F20 is typedef int32_t i32F20; i32F20_to__i32 returns Signed_Index__i32 (also int32_t); normalize_xyz_i32_to__tile_xyz_i32 takes i32 (also int32_t). No implicit conversions or truncation.
- Undefined behavior: No null dereference, no out-of-bounds access, no type punning. However, the base function normalize_xyz_i32_to__tile_xyz_i32 uses plain `>>` on signed integers, which is implementation-defined for negative values per the C standard. The codebase explicitly defines ARITHMETRIC_R_SHIFT to address this portability concern, but it is not used here.
- Validation: No validation needed; this is a pure computation function.

Side Effects:
No side effects. Pure function — reads only its parameter and returns a computed i32 value.
