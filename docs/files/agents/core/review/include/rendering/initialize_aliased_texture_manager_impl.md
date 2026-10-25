// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 26 - 37
//   void initialize_aliased_texture_manager(
//           Aliased_Texture_Manager *p_aliased_texture_manager) {
//       initialize_serialization_header__contiguous_array(
//               (Serialization_Header*)p_aliased_texture_manager
//                   ->aliased_textures, 
//               MAX_QUANTITY_OF__ALIASED_TEXTURES, 
//               sizeof(Aliased_Texture));
//       initialize_repeatable_psuedo_random(
//               &p_aliased_texture_manager
//               ->repeatable_psuedo_random_for__texture_uuid, 
//               (uint32_t)(uint64_t)p_aliased_texture_manager);
//   }
