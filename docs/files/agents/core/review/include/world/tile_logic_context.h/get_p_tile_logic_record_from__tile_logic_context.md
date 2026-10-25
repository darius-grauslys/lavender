// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 38 - 60
//   static inline
//   Tile_Logic_Record *get_p_tile_logic_record_from__tile_logic_context(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile_Layer the_kind_of__tile_layer,
//           Index__u8 index_of__tile_logic_record__u8) {
//       #ifndef NDEBUG
//       if (!p_tile_logic_context) {
//           debug_error("get_p_tile_logic_record_from__tile_logic_context, p_tile_logic_context == 0.");
//           return 0;
//       }
//       if (Tile_Layer__Unknown <= the_kind_of__tile_layer) {
//           debug_error("get_p_tile_logic_record_from__tile_logic_context, invalid tiletype provided.");
//           return 0;
//       }
//       #endif
//       Tile_Logic_Table *p_tile_logic_table =
//           get_p_tile_logic_table_from__tile_logic_context(
//                   p_tile_logic_context, 
//                   the_kind_of__tile_layer);
//       return get_p_tile_logic_record_from__tile_logic_table(
//               p_tile_logic_table, 
//               index_of__tile_logic_record__u8);
//   }
