normalize_i32__to_tile_u8 — core/include/world/tile_vectors.h

Converts a signed pixel-space coordinate to a local tile index within a chunk (0 to CHUNK_WIDTH−1). It right-shifts the coordinate by TILE__WIDTH_AND__HEIGHT__BIT_SHIFT bits to convert pixels to tiles, applies a floor-division correction for negative values, and then masks the result to wrap within the chunk's tile range.

Pre-conditions:
1. x is a Signed_Index__i32 (int32_t) representing a world pixel coordinate. No null-pointer concern (passed by value).
2. x may be any value in the range of int32_t. No pre-condition on sign or magnitude.

Post-conditions:
1. Returns an Index__u8 (uint8_t) in the range [0, CHUNK__WIDTH−1] (i.e., [0, 7] with default settings), representing the local tile index within a chunk.
2. The returned value is intended to equal floor(x / TILE__WIDTH) mod CHUNK__WIDTH, where TILE__WIDTH = BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT) and CHUNK__WIDTH = BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT).

Correctness Verdict: Incorrect

Semantic Alignment:
The intent is to compute floor(x / TILE__WIDTH) mod CHUNK__WIDTH — a portable floor division followed by modular wrapping. The ARITHMETRIC_R_SHIFT macro truncates toward zero (not floor), so a correction term is needed to convert truncation to floor division. However, the correction term `- (x < 0)` is applied unconditionally for all negative x. This is incorrect: the floor-division correction should only subtract 1 when there is a remainder, i.e., when x is negative AND not an exact multiple of BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT). For negative exact multiples of the tile width (e.g., x = -8, -16, -24, ... with default settings), the function subtracts 1 when it should not, producing an off-by-one error in the tile index.

Concrete counterexample (default settings: TILE__WIDTH_AND__HEIGHT__BIT_SHIFT = 3, CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT = 3, so TILE__WIDTH = 8, CHUNK__WIDTH = 8):
- x = -8: ARITHMETRIC_R_SHIFT(-8, 3) = -(8 >> 3) = -1 (truncation = floor, since -8/8 = -1 exactly). Then -1 - (x < 0) = -1 - 1 = -2. ARITHMETRIC_MASK(-2, 7) = 6. Expected: floor(-8/8) mod 8 = -1 mod 8 = 7. Result is 6, not 7. Off by one.
- x = -16: ARITHMETRIC_R_SHIFT(-16, 3) = -(16 >> 3) = -2. Then -2 - 1 = -3. ARITHMETRIC_MASK(-3, 7) = 5. Expected: floor(-16/8) mod 8 = -2 mod 8 = 6. Result is 5, not 6. Off by one.
- x = -1: ARITHMETRIC_R_SHIFT(-1, 3) = -(1 >> 3) = 0. Then 0 - 1 = -1. ARITHMETRIC_MASK(-1, 7) = 7. Expected: floor(-1/8) mod 8 = -1 mod 8 = 7. Correct.
- x = -9: ARITHMETRIC_R_SHIFT(-9, 3) = -(9 >> 3) = -1. Then -1 - 1 = -2. ARITHMETRIC_MASK(-2, 7) = 6. Expected: floor(-9/8) mod 8 = -2 mod 8 = 6. Correct.

The bug only manifests for negative coordinates that are exact multiples of the tile width. This can occur in practice when world positions align to tile or chunk boundaries (e.g., x = -8.0 as i32F4 = -128, which flows through normalize_i32F4__to_tile_u8 into this function with x = -8).

The correct floor-division correction should be:
  - (x < 0 && (x & MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)) != 0)
instead of:
  - (x < 0)

Note: The sibling function normalize_xyz_i32_to__tile_xyz_i32 in the same file uses plain `>>` (arithmetic right shift, which is floor division on most platforms) and does not apply any correction term, producing correct results. The normalize_xyz_i32_to__chunk_xyz_i32 function in chunk_vectors.h uses the same buggy pattern (ARITHMETRIC_R_SHIFT(x, n) - (x < 0)).

Implementation Correctness:
Type compatibility: The parameter is Signed_Index__i32 (int32_t) and the return type is Index__u8 (uint8_t). The ARITHMETRIC_MASK macro operates on the value and produces a result in [0, n], which fits in a u8 when n = MASK(3) = 7. No truncation issues in the return.
Undefined behavior: No null dereference (value parameter), no out-of-bounds access, no type punning. The ARITHMETRIC_R_SHIFT and ARITHMETRIC_MASK macros use only well-defined integer operations. However, there is a potential integer overflow in ARITHMETRIC_R_SHIFT if x equals INT32_MIN (negating INT32_MIN is undefined behavior), but this is an edge case not directly in scope for this function's logic.
Validation: No validation is present, which is appropriate for this low-level inline utility. The caller is responsible for providing a meaningful coordinate.

Side Effects:
No side effects. The function is pure — it reads only its parameter and returns a computed value.
