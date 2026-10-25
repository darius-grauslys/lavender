// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 265 - 277
//   static inline
//   Aliased_Texture *get_p_aliased_texture_by__uuid(
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Identifier__u32 uuid__u32) {
//       Aliased_Texture *p_aliased_texture =
//           (Aliased_Texture*)dehash_identitier_u32_in__contigious_array(
//                   (Serialization_Header*)p_aliased_texture_manager
//                   ->aliased_textures, 
//                   MAX_QUANTITY_OF__ALIASED_TEXTURES, 
//                   uuid__u32);
//
//       return p_aliased_texture;
//   }
