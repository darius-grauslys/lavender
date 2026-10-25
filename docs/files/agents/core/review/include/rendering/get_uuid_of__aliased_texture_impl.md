// Review:
// - File: core/source/rendering/aliased_texture_manager.c
// - Lines: 219 - 238
//   Identifier__u32 get_uuid_of__aliased_texture(
//           Aliased_Texture_Manager *p_aliased_texture_manager,
//           Texture_Name__c_str name_of__texture__c_str) {
//       Aliased_Texture *p_aliased_texture__matching =
//           get_p_aliased_texture_by__alias(
//                   p_aliased_texture_manager, 
//                   name_of__texture__c_str);
//
//       if (!p_aliased_texture__matching) {
//           char name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME+1];
//           memcpy(
//                   name_of__texture__copied__c_str,
//                   name_of__texture__c_str,
//                   MAX_LENGTH_OF__TEXTURE_NAME);
//           name_of__texture__copied__c_str[MAX_LENGTH_OF__TEXTURE_NAME] = 0;
//           debug_error("get_uuid_of__aliased_texture, failed to find texture for given name: %s", name_of__texture__copied__c_str);
//       }
//
//       return GET_UUID_P(p_aliased_texture__matching);
//   }
