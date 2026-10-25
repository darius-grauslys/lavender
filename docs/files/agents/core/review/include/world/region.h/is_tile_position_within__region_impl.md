// Review:
// - File: core/source/world/region.c
// - Lines: 7 - 18
//   bool is_tile_position_within__region(
//           Tile_Vector__3i32 tile_position__3i32,
//           Region_Vector__3i32 region_position__3i32) {
//       return
//           tile_position__3i32.x__i32
//           >> REGION__WIDTH__BIT_SHIFT
//           == region_position__3i32.x__i32
//           && tile_position__3i32.y__i32
//           >> REGION__WIDTH__BIT_SHIFT
//           == region_position__3i32.y__i32
//           ;
//   }
