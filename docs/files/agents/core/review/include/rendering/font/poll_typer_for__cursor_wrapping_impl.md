// Review:
// - File: core/source/rendering/font/typer.c
// - Lines: 34 - 106
//   bool poll_typer_for__cursor_wrapping(
//           Typer *p_typer,
//           Font_Letter *p_font_letter) {
//
//       Hitbox_AABB font_letter_hitbox;
//       initialize_hitbox_aabb_as__allocated(
//               &font_letter_hitbox, 
//               IDENTIFIER__UNKNOWN__u32,
//               p_font_letter->width_of__font_letter, 
//               p_font_letter->height_of__font_letter,
//               get_vector__3i32F4_using__i32(0, 0, 0));
//
//       Vector__3i32F4 hitbox_position =
//           get_vector__3i32F4_using__i32(
//                   p_typer->cursor_position__3i32.x__i32
//                   + (p_font_letter->width_of__font_letter >> 1),
//                   p_typer->cursor_position__3i32.y__i32
//                   + (p_font_letter->height_of__font_letter >> 1),
//                   0);
//
//       add_p_vectors__3i32F4(
//               &hitbox_position, 
//               &p_typer->text_bounding_box.position__3i32F4);
//
//       hitbox_position.x__i32F4 -=
//           i32_to__i32F4(p_typer->text_bounding_box.width__quantity_u32 >> 1);
//       hitbox_position.y__i32F4 -=
//           i32_to__i32F4(p_typer->text_bounding_box.height__quantity_u32 >> 1);
//
//       font_letter_hitbox.position__3i32F4 =
//           hitbox_position;
//
//       if (is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity(
//                   &font_letter_hitbox,
//                   &p_typer->text_bounding_box)) {
//           return true;
//       }
//
//       Vector__3i32 aa;
//       initialize_vector_3i32_as__aa_bb_without__velocity(
//               &aa, 
//               &p_typer->text_bounding_box, 
//               DIRECTION__SOUTH_WEST);
//
//       p_typer->cursor_position__3i32.x__i32 = 0;
//       p_typer->cursor_position__3i32.y__i32 +=
//           p_typer->p_font->max_height_of__font_letter
//           + p_typer->quantity_of__space_in__pixels_between__lines;
//
//       hitbox_position =
//           get_vector__3i32F4_using__i32(
//                   p_typer->cursor_position__3i32.x__i32
//                   + (p_font_letter->width_of__font_letter >> 1),
//                   p_typer->cursor_position__3i32.y__i32
//                   + (p_font_letter->height_of__font_letter >> 1),
//                   0);
//
//       add_p_vectors__3i32F4(
//               &hitbox_position, 
//               &p_typer->text_bounding_box.position__3i32F4);
//
//       hitbox_position.x__i32F4 -=
//           i32_to__i32F4(p_typer->text_bounding_box.width__quantity_u32 >> 1);
//       hitbox_position.y__i32F4 -=
//           i32_to__i32F4(p_typer->text_bounding_box.height__quantity_u32 >> 1);
//
//       font_letter_hitbox.position__3i32F4 =
//           hitbox_position;
//
//       return is_this_hitbox_aabb__fully_inside_this_hitbox_aabb__without_velocity(
//                   &font_letter_hitbox,
//                   &p_typer->text_bounding_box);
//   }
