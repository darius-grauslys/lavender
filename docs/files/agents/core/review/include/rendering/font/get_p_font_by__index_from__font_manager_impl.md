// Review:
// - File: core/source/rendering/font/font_manager.c
// - Lines: 4 - 17
//   static inline
//   Font *get_p_font_by__index_from__font_manager(
//           Font_Manager *p_font_manager,
//           Index__u32 index_of__font) {
//       #ifndef NDEBUG
//       if (index_of__font >= MAX_QUANTITY_OF__FONT) {
//           debug_error("get_p_font_by__index_from__font_manager, index out of bounds: %d/%d", index_of__font, MAX_QUANTITY_OF__FONT);
//           return 0;
//       }
//       #endif
//
//       return &p_font_manager
//           ->fonts[index_of__font];
//   }
