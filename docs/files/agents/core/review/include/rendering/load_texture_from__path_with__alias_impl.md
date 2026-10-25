// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 119 - 186
//   bool load_texture_from__path_with__alias(
//           PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
//           PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Texture_Name__c_str name_of__texture__c_str,
//           Texture_Flags texture_flags,
//           const char *c_str__path,
//           Texture *p_OUT_texture) {
//       Texture __tmp_texture;
//       if (!p_OUT_texture)
//           p_OUT_texture = &__tmp_texture;
//       if (!name_of__texture__c_str[0]) {
//           debug_warning("texture: %s", name_of__texture__c_str);
//           debug_error("load_texture_from__path_with__alias, alias cannot be empty.");
//           return true;
//       }
//
//       Aliased_Texture *p_aliased_texture__available =
//           (Aliased_Texture*)allocate_serialization_header_with__uuid_branding(
//                   (Serialization_Header*)p_aliased_texture_manager->aliased_textures, 
//                   MAX_QUANTITY_OF__ALIASED_TEXTURES, 
//                   &p_aliased_texture_manager->repeatable_psuedo_random_for__texture_uuid, 
//                   GET_UUID_BRANDING(
//                       Lavender_Type__Aliased_Texture,
//                       0));
//       if (!p_aliased_texture__available) {
//           debug_warning("texture: %s", name_of__texture__c_str);
//           debug_error("load_texture_from__path_with__alias, too many aliased textures are allocated.");
//           return true;
//       }
//
//       IO_path full_path;
//       memset(full_path,
//               0,
//               sizeof(full_path));
//       Quantity__u32 length_of__base_directory = 
//           PLATFORM_get_base_directory(full_path);
//       if (MAX_LENGTH_OF__IO_PATH 
//               <= length_of__base_directory) {
//           debug_warning("texture: %s", name_of__texture__c_str);
//           debug_error("load_texture_from__path_with__alias, game directory exceeds MAX_LENGTH_OF__IO_PATH.");
//           return true;
//       }
//       full_path[length_of__base_directory++] = '/';
//       memcpy(&full_path[length_of__base_directory],
//               c_str__path,
//               MAX_LENGTH_OF__IO_PATH
//               - length_of__base_directory);
//
//       if (PLATFORM_allocate_texture_with__path(
//                   p_PLATFORM_gfx_context,
//                   p_PLATFORM_gfx_window,
//                   texture_flags,
//                   full_path,
//                   p_OUT_texture)) {
//           debug_warning("texture: %s", name_of__texture__c_str);
//           debug_error("load_texture_from__path_with__alias, failed to allocate texture.");
//           return true;
//       }
//
//       set_c_str_of__aliased_texture(
//               p_aliased_texture__available, 
//               name_of__texture__c_str);
//       give_texture_to__aliased_texture(
//               p_aliased_texture__available, 
//               p_OUT_texture);
//       return false;
//   }
