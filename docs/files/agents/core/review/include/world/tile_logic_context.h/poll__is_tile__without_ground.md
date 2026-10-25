// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 86 - 96
//   static inline
//   bool poll__is_tile__without_ground(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile *p_tile) {
//       Tile_Logic_Record *p_tile_logic_record =
//           get_p_tile_logic_record_from__tile_logic_context(
//                   p_tile_logic_context, 
//                   Tile_Layer__Default__Is_With_Ground,
//                   get_tile_kind_from__tile(p_tile));
//       return is_tile_logic_record__without_ground(p_tile_logic_context);
//   }
