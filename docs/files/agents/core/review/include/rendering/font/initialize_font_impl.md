// Review:
// - File: core/source/rendering/font/font.c
// - Lines: 42 - 63
//   void initialize_font(Font *p_font) {
//       p_font->max_width_of__font_letter = 0;
//       p_font->max_height_of__font_letter = 0;
//       initialize_texture(p_font->texture_of__font);
//       p_font->font_flags = FONT_FLAGS__NONE;
//       for (Index__u32 index_of__font_letter = 0;
//               index_of__font_letter
//               < FONT_LETTER_MAX_QUANTITY_OF;
//               index_of__font_letter++) {
//           Font_Letter *p_font_letter =
//               get_p_font_letter_by__index_from__font(
//                       p_font, 
//                       index_of__font_letter);
//           initialize_font__letter(
//                   p_font_letter, 
//                   0, 
//                   0, 
//                   0, 
//                   0, 
//                   0);
//       }
//   }
