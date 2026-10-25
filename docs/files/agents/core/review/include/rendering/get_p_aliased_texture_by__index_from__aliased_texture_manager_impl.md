// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 13 - 24
//   static inline
//   Aliased_Texture *get_p_aliased_texture_by__index_from__aliased_texture_manager(
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Index__u32 index_of__aliased_texture) {
//       if (MAX_QUANTITY_OF__ALIASED_TEXTURES
//               <= index_of__aliased_texture) {
//           debug_error("get_p_aliased_texture_by__index_from__aliased_texture_manager, index out of bounds: %d/%d", index_of__aliased_texture, MAX_QUANTITY_OF__ALIASED_TEXTURES);
//           return 0;
//       }
//       return &p_aliased_texture_manager
//           ->aliased_textures[index_of__aliased_texture];
//   }
