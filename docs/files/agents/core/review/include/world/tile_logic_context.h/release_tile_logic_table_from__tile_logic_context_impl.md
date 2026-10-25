// Review:
// - File: core/source/world/tile_logic_context.c
// - Lines: 28 - 47
//   void release_tile_logic_table_from__tile_logic_context(
//           Tile_Logic_Context *p_tile_logic_context,
//           Tile_Layer the_tile_layer_to__release) {
//       #ifndef NDEBUG
//       if (Tile_Layer__Unknown <= the_tile_layer_to__release) {
//           debug_error("release_tile_logic_table_from__tile_logic_context, invalid tile layer type.");
//           return;
//       }
//       #endif
//       if (0 == p_tile_logic_context->array_of__pM_tile_logic_tables[
//               the_tile_layer_to__release]) {
//           debug_error("release_tile_logic_table_from__tile_logic_context, tile_logic_table record already released for given type.");
//           return;
//       }
//
//       free(p_tile_logic_context->array_of__pM_tile_logic_tables[
//               the_tile_layer_to__release]);
//       p_tile_logic_context->array_of__pM_tile_logic_tables[
//           the_tile_layer_to__release] = 0;
//   }
