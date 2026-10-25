// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 147 - 160
//   static Vector__3i32 inline chunk_vector_3i32_to__vector_3i32(Chunk_Vector__3i32 chunk_vector) {
//       return (Vector__3i32) {
//           ARITHMETIC_L_SHIFT(chunk_vector.x__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
//           ARITHMETIC_L_SHIFT(chunk_vector.y__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
//           ARITHMETIC_L_SHIFT(chunk_vector.z__i32, LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT),
//       };
//   }
