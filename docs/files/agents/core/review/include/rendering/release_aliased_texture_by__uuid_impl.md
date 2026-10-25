// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 317 - 335
//   void release_aliased_texture_by__uuid(
//           PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Identifier__u32 uuid__u32) {
//       Aliased_Texture *p_aliased_texture =
//           get_p_aliased_texture_by__uuid(
//                   p_aliased_texture_manager, 
//                   uuid__u32);
//
//       if (!p_aliased_texture) {
//           debug_warning("release_aliased_texture_by__uuid, failed to find.");
//           return;
//       }
//
//       PLATFORM_release_texture(
//               p_PLATFORM_gfx_context, 
//               p_aliased_texture->texture);
//       initialize_aliased_texture(p_aliased_texture);
//   }
