// Review:
// - File: core/source/world/region_manager.c
// - Lines: 21 - 42
//   void set_center_of__region_manager(
//           Game *p_game,
//           Region_Manager *p_region_manager,
//           Region_Vector__3i32 region_vector__3i32) {
//       if (is_vectors_3i32__equal(
//                   region_vector__3i32, 
//                   p_region_manager->center_of__region_manager)) {
//           return;
//       }
//
//       for (Index__u32 index_of__region = 0;
//               index_of__region < REGION_MAX_QUANTITY_OF;
//               index_of__region++) {
//           Region *p_region = get_p_region_by__index_from__region_manager(
//                   p_region_manager, 
//                   index_of__region);
//
//       }
//
//       p_region_manager->center_of__region_manager =
//           region_vector__3i32;
//   }
