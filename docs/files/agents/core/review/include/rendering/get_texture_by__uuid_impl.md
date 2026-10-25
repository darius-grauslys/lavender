// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 279 - 297
//   bool get_texture_by__uuid(
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Identifier__u32 uuid__u32,
//           Texture *p_OUT_texture) {
//       Aliased_Texture *p_aliased_texture =
//           get_p_aliased_texture_by__uuid(
//                   p_aliased_texture_manager, 
//                   uuid__u32);
//
//       if (!p_aliased_texture) {
//           debug_error("get_texture_by__uuid, failed to find texture.");
//           return true;
//       }
//
//       *p_OUT_texture =
//           get_texture_from__aliased_texture(
//               p_aliased_texture);
//       return false;
//   }
