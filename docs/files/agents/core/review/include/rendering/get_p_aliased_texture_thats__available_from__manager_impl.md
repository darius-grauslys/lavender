// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 39 - 59
//   Aliased_Texture *get_p_aliased_texture_thats__available_from__manager(
//           Aliased_Texture_Manager *p_aliased_texture_manager) {
//       Aliased_Texture *p_aliased_texture__available = 0;
//       for (Index__u32 index_of__aliased_texture = 0;
//               index_of__aliased_texture
//               < MAX_QUANTITY_OF__ALIASED_TEXTURES;
//               index_of__aliased_texture++) {
//           Aliased_Texture *p_aliased_texture =
//               get_p_aliased_texture_by__index_from__aliased_texture_manager(
//                       p_aliased_texture_manager, 
//                       index_of__aliased_texture);
//           if (is_aliased_texture__used(p_aliased_texture)) {
//               continue;
//           }
//           p_aliased_texture__available = 
//               p_aliased_texture;
//           break;
//       }
//
//       return p_aliased_texture__available;
//   }
