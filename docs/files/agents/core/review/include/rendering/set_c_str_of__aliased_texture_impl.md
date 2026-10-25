// Review:
// - File: core/source/rendering/aliased_texture.c
// - Lines: 19 - 28
//   void set_c_str_of__aliased_texture(
//           Aliased_Texture *p_aliased_texture,
//           const char *c_str) {
//       Quantity__u32 length_of__c_str =
//           strnlen(c_str, MAX_LENGTH_OF__TEXTURE_NAME);
//       memcpy(p_aliased_texture
//               ->name_of__texture__c_str,
//               c_str,
//               length_of__c_str);
//   }
