// Review:
// - File: core/source/rendering/font/typer.c
// - Lines: 9 - 32
//   void initialize_typer(
//           Typer *p_typer,
//           i32 x, i32 y,
//           Quantity__u32 width,
//           Quantity__u32 height,
//           Quantity__u32 quantity_of__spacing,
//           i32 x__cursor, i32 y__cursor) {
//       initialize_hitbox_aabb_as__allocated(
//               &p_typer->text_bounding_box, 
//               IDENTIFIER__UNKNOWN__u32,
//               width, height, 
//               get_vector__3i32F4_using__i32(
//                   x, y, 0));
//       p_typer->cursor_position__3i32 =
//           get_vector__3i32(
//                   x__cursor,
//                   y__cursor, 
//                   0);
//       p_typer->quantity_of__space_in__pixels_between__lines = 
//           quantity_of__spacing;
//       p_typer->p_font = 0;
//       initialize_texture(p_typer->texture_of__typer_target);
//       p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window = true;
//   }
