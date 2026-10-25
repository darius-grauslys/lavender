// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 49 - 54
//   static inline
//   i32 normalize_xyz_i32F4_to__chunk_xyz_i32(i32F4 xyz__i32F4) {
//       return normalize_xyz_i32_to__chunk_xyz_i32(i32F4_to__i32(xyz__i32F4)) - (xyz__i32F4 < 0 && -xyz__i32F4 < BIT(FRACTIONAL_PERCISION_4__BIT_SIZE));
//   }
