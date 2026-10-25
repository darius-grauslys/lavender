// Review:
// - File: core/include/rendering/aliased_texture.h
// - Lines: 34 - 44
//   static inline
//   Texture get_texture_from__aliased_texture(
//           Aliased_Texture *p_aliased_texture) {
//       #ifndef NDEBUG
//       if (!p_aliased_texture) {
//           debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
//           return (Texture){0};
//       }
//       #endif
//       return p_aliased_texture->texture;
//   }
