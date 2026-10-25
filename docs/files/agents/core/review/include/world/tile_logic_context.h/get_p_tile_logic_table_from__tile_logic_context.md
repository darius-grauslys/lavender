// Review:
// - File: core/include/world/tile_logic_context.h
// - Lines: 23 - 36
//   static inline
//   Tile_Logic_Table *get_p_tile_logic_table_from__tile_logic_context(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile_Layer the_tile_layer_to__get) {
//       #ifndef NDEBUG
//       if (Tile_Layer__Unknown <= the_tile_layer_to__get) {
//           debug_error("get_tile_logic_table_from__tile_logic_context, invalid tile layer type.");
//           return 0;
//       }
//       #endif
//
//       return p_tile_logic_context->array_of__pM_tile_logic_tables[
//           the_tile_layer_to__get];
//   }
