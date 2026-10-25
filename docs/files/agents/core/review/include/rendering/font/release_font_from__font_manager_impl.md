// Review:
// - File: core/source/rendering/font/font_manager.c
// - Lines: 60 - 74
//   void release_font_from__font_manager(
//           Font_Manager *p_font_manager,
//           Font *p_font) {
//       #ifndef NDEBUG
//       int index = p_font
//           - p_font_manager->fonts;
//       if (index >= MAX_QUANTITY_OF__FONT) {
//           debug_error("release_font_from__font_manager, font was not allocated with this manager.");
//           return;
//       }
//       #endif
//
//       initialize_font(p_font);
//       set_font_as__deallocated(p_font);
//   }
