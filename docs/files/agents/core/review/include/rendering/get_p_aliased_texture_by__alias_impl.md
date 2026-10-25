// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 188 - 217
//   static inline
//   Aliased_Texture *get_p_aliased_texture_by__alias(
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Texture_Name__c_str name_of__texture__c_str) {
//       Aliased_Texture *p_aliased_texture__matching = 0;
//       for (Index__u32 index_of__aliased_texture = 0;
//               index_of__aliased_texture
//               < MAX_QUANTITY_OF__ALIASED_TEXTURES;
//               index_of__aliased_texture++) {
//           Aliased_Texture *p_aliased_texture =
//               get_p_aliased_texture_by__index_from__aliased_texture_manager(
//                       p_aliased_texture_manager, 
//                       index_of__aliased_texture);
//           if (!is_aliased_texture__used(p_aliased_texture)) {
//               continue;
//           }
//           if (is_c_str_matching__aliased_texture(
//                       p_aliased_texture, 
//                       name_of__texture__c_str)) {
//               p_aliased_texture__matching = 
//                   p_aliased_texture;
//               break;
//           }
//       }
//       if (!p_aliased_texture__matching) {
//           return 0;
//       }
//
//       return p_aliased_texture__matching;
//   }
