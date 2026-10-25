// Review:
// - File: core/source/rendering/aliased_texture.c
// - Lines: 30 - 46
//   bool is_c_str_matching__aliased_texture(
//           Aliased_Texture *p_aliased_texture,
//           const char *c_str) {
//       for (Index__u32 index_of__c_str = 0;
//               index_of__c_str
//               < MAX_LENGTH_OF__TEXTURE_NAME;
//               index_of__c_str++) {
//           if (!c_str[index_of__c_str])
//               break;
//           if (c_str[index_of__c_str]
//                   != p_aliased_texture
//                   ->name_of__texture__c_str[index_of__c_str]) {
//               return false;
//           }
//       }
//       return true;
//   }
