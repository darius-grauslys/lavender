// Review:
// - File: core/source/rendering/font/font.c
// - Lines: 25 - 40
//   static inline
//   Font_Letter *get_p_font_letter_by__index_from__font(
//           Font *p_font,
//           Index__u32 index_of__font_letter) {
//       #ifndef NDEBUG
//       if (FONT_LETTER_MAX_QUANTITY_OF
//               <= index_of__font_letter) {
//           debug_error("get_p_font_letter_by__index_from__font, index out of bounds: %d/%d",
//                   index_of__font_letter,
//                   FONT_LETTER_MAX_QUANTITY_OF);
//           return 0;
//       }
//       #endif
//
//       return &p_font->font_lookup_table[index_of__font_letter];
//   }
