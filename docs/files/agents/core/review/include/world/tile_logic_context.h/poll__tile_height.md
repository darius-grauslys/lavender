// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 98 - 108
//   static inline
//   i32F4 poll__tile_height(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile *p_tile) {
//       Tile_Logic_Record *p_tile_logic_record =
//           get_p_tile_logic_record_from__tile_logic_context(
//                   p_tile_logic_context, 
//                   Tile_Layer__Default__Height,
//                   get_tile_kind_from__tile(p_tile));
//       return p_tile_logic_record->tile_height__i32F4;
//   }
