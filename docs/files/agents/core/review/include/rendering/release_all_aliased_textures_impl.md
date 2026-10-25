// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 299 - 315
//   void release_all_aliased_textures(
//           PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
//           Aliased_Texture_Manager *p_aliased_texture_manager) {
//       for (Index__u32 index_of__aliased_texture = 0;
//               index_of__aliased_texture
//               < MAX_QUANTITY_OF__ALIASED_TEXTURES;
//               index_of__aliased_texture++) {
//           Aliased_Texture *p_aliased_texture =
//               get_p_aliased_texture_by__index_from__aliased_texture_manager(
//                       p_aliased_texture_manager, 
//                       index_of__aliased_texture);
//           PLATFORM_release_texture(
//                   p_PLATFORM_gfx_context, 
//                   p_aliased_texture->texture);
//           initialize_aliased_texture(p_aliased_texture);
//       }
//   }
