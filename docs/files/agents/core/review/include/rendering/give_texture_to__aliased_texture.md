// Review:
// - File: core/include/rendering/aliased_texture.h
// - Lines: 20 - 32
//   static inline
//   void give_texture_to__aliased_texture(
//           Aliased_Texture *p_aliased_texture,
//           Texture *p_texture) {
//       #ifndef NDEBUG
//       if (!p_aliased_texture) {
//           debug_error("give_PLATFORM_texture_to__aliased_texture, p_aliased_texture == 0.");
//           return;
//       }
//       #endif
//       p_aliased_texture->texture=
//           *p_texture;
//   }
