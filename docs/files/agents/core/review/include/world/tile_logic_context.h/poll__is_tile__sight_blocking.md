// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 74 - 84
//   static inline
//   bool poll__is_tile__sight_blocking(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile *p_tile) {
//       Tile_Logic_Record *p_tile_logic_record =
//           get_p_tile_logic_record_from__tile_logic_context(
//                   p_tile_logic_context, 
//                   Tile_Layer__Default__Sight_Blocking,
//                   get_tile_kind_from__tile(p_tile));
//       return is_tile_logic_record__sight_blocking(p_tile_logic_record);
//   }
