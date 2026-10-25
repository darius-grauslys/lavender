// Review:
// - File: core/include/world/chunk_vectors.h
// - Lines: 119 - 126
//   static Chunk_Vector__3i32 inline vector_3i32_to__chunk_vector_3i32(Vector__3i32 vector) {
//       return (Chunk_Vector__3i32) {
//           normalize_xyz_i32_to__chunk_xyz_i32(vector.x__i32),
//           normalize_xyz_i32_to__chunk_xyz_i32(vector.y__i32),
//           normalize_xyz_i32_to__chunk_xyz_i32(vector.z__i32)
//       };
//   }
