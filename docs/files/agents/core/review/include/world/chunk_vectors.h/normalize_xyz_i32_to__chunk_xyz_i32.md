// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 10 - 17
//   static inline
//   i32 normalize_xyz_i32_to__chunk_xyz_i32(i32 tile_xyz__i32) {
//       return ARITHMETIC_R_SHIFT(tile_xyz__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT) - (tile_xyz__i32 < 0);
//   }
