// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 62 - 72
//   static inline
//   bool poll__is_tile__unpassable(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile *p_tile) {
//       Tile_Logic_Record *p_tile_logic_record =
//           get_p_tile_logic_record_from__tile_logic_context(
//                   p_tile_logic_context, 
//                   Tile_Layer__Default__Is_Passable,
//                   get_tile_kind_from__tile(p_tile));
//       return is_tile_logic_record__unpassable(p_tile_logic_record);
//   }
