// Review:
// - File: core/include/world/region.h
// - Lines: 27 - 37
//   static inline
//   void truncate_p_chunk_vector_3i32_to__region(
//           Chunk_Vector__3i32 *p_chunk_vector__3i32) {
//       p_chunk_vector__3i32->x__i32 &=
//           MASK(REGION__WIDTH__BIT_SHIFT)
//           >> CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT;
//       p_chunk_vector__3i32->y__i32 &=
//           MASK(REGION__HEIGHT__BIT_SHIFT)
//           >> CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT;
//       // TODO: Z-axis
//   }
