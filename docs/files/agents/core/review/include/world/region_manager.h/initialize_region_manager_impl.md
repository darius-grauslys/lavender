// Review:
// - File: core/source/world/region_manager.c
// - Lines: 13 - 19
//   void initialize_region_manager(
//           Region_Manager *p_region_manager) {
//       initialize_serialization_header__contiguous_array(
//               (Serialization_Header*)p_region_manager->regions, 
//               REGION_MAX_QUANTITY_OF, 
//               sizeof(Region));
//   }
