// Review:
// - File: core/source/world/region.c
// - Lines: 37 - 64
//   bool is_chunk_serialized_in__region(
//           Region *p_region,
//           Chunk_Vector__3i32 chunk_vector__3i32) {
//       i32 x__clamped =
//           (chunk_vector__3i32.x__i32 < 0)
//           ? REGION__WIDTH_IN__CHUNKS
//               - ((-chunk_vector__3i32.x__i32)
//                       & MASK(REGION__WIDTH__BIT_SHIFT))
//           : (-chunk_vector__3i32.x__i32)
//                   & MASK(REGION__WIDTH__BIT_SHIFT)
//           ;
//       i32 y__clamped =
//           (chunk_vector__3i32.y__i32 < 0)
//           ? REGION__HEIGHT_IN__CHUNKS
//               - ((-chunk_vector__3i32.y__i32)
//                       & MASK(REGION__HEIGHT__BIT_SHIFT))
//           : (-chunk_vector__3i32.y__i32)
//                   & MASK(REGION__HEIGHT__BIT_SHIFT)
//           ;
//
//       return is_bit_set_in__bitmap(
//               p_region
//               ->bitmap_of__serialized_chunks, 
//               sizeof(p_region->bitmap_of__serialized_chunks), 
//               x__clamped 
//               + y__clamped
//               * REGION__WIDTH_IN__CHUNKS);
//   }
