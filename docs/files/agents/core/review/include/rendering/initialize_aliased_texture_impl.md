// Review:
// - File: core/source/rendering/aliased_texture.c
// - Lines: 6 - 17
//   void initialize_aliased_texture(
//           Aliased_Texture *p_aliased_texture) {
//       initialize_texture(
//               p_aliased_texture->texture);
//       memset(p_aliased_texture
//               ->name_of__texture__c_str,
//               0,
//               sizeof(p_aliased_texture->name_of__texture__c_str));
//       initialize_serialization_header_for__deallocated_struct(
//               (Serialization_Header*)p_aliased_texture, 
//               sizeof(Aliased_Texture));
//   }
