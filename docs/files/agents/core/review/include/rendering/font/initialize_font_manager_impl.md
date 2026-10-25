// Review:
// - File: core/source/rendering/font/font_manager.c
// - Lines: 19 - 30
//   void initialize_font_manager(
//           Font_Manager *p_font_manager) {
//       for (Index__u32 index_of__font = 0;
//               index_of__font
//               < MAX_QUANTITY_OF__FONT;
//               index_of__font++) {
//           Font *p_font = get_p_font_by__index_from__font_manager(
//                   p_font_manager, 
//                   index_of__font);
//           initialize_font(p_font);
//       }
//   }
