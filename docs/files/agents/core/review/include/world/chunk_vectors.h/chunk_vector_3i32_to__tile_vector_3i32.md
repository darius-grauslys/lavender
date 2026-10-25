// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 128 - 145
//   static inline Chunk_Vector__3i32 chunk_vector_3i32_to__tile_vector_3i32(Chunk_Vector__3i32 chunk_vector) {
//       return (Tile_Vector__3i32) {
//           ARITHMETIC_L_SHIFT(chunk_vector.x__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
//           ARITHMETIC_L_SHIFT(chunk_vector.y__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
//           ARITHMETIC_L_SHIFT(chunk_vector.z__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT - TILE__WIDTH_AND__HEIGHT__BIT_SHIFT),
//       };
//   }
