// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 19 - 26
//   static inline
//   i32 normalize_xyz_tile_i32_to__chunk_xyz_i32(i32 tile_xyz__i32) {
//       return ARITHMETIC_R_SHIFT(tile_xyz__i32 + (tile_xyz__i32 < 0), LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT) - (tile_xyz__i32 < 0);
//   }
