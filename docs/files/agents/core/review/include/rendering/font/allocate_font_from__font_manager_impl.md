// Review:
// - File: core/source/rendering/font/font_manager.c
// - Lines: 32 - 58
//   Font *allocate_font_from__font_manager(
//           Font_Manager *p_font_manager) {
//       Font *p_font__available = 0;
//
//       for (Index__u32 index_of__font = 0;
//               index_of__font
//               < MAX_QUANTITY_OF__FONT;
//               index_of__font++) {
//           Font *p_font = get_p_font_by__index_from__font_manager(
//                   p_font_manager, 
//                   index_of__font);
//           if (is_font__allocated(p_font)) {
//               continue;
//           }
//
//           p_font__available = p_font;
//           break;
//       }
//
//       if (p_font__available) {
//           set_font_as__allocated(p_font__available);
//       } else {
//           debug_error("allocate_font_from__font_manager, failed to allocate font.");
//       }
//
//       return p_font__available;
//   }
