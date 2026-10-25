// Review:
// - File: core/source/world/region.c
// - Lines: 27 - 35
//   Region_Vector__3i32 get_region_that__this_global_space_is_in(
//           Global_Space *p_global_space) {
//       return get_vector__3i32(
//               p_global_space->chunk_vector__3i32.x__i32 
//               >> REGION__WIDTH__BIT_SHIFT, 
//               p_global_space->chunk_vector__3i32.y__i32 
//               >> REGION__HEIGHT__BIT_SHIFT, 
//               0);
//   }
