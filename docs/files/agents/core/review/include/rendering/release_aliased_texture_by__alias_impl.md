// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 337 - 355
//   void release_aliased_texture_by__alias(
//           PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Texture_Name__c_str name_of__texture__c_str) {
//       Aliased_Texture *p_aliased_texture =
//           get_p_aliased_texture_by__alias(
//                   p_aliased_texture_manager, 
//                   name_of__texture__c_str);
//
//       if (!p_aliased_texture) {
//           debug_warning("release_aliased_texture_by__alias, failed to find.");
//           return;
//       }
//
//       PLATFORM_release_texture(
//               p_PLATFORM_gfx_context, 
//               p_aliased_texture->texture);
//       initialize_aliased_texture(p_aliased_texture);
//   }
