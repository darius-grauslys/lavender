// Review:
// - File: core/source/rendering/font/typer.c
// - Lines: 108 - 149
//   void put_c_string_in__typer(
//           Gfx_Context *p_gfx_context,
//           Typer *p_typer,
//           const char *c_string,
//           Quantity__u32 max_length_of__c_string) {
//       if (!max_length_of__c_string)
//           return;
//       if (!*c_string)
//           return;
//
//       do {
//           char letter = *c_string;
//           switch (letter) {
//               default:
//                   break;
//               case '\n':
//               case '\r':
//                   p_typer->cursor_position__3i32.y__i32 +=
//                       p_typer->p_font->max_height_of__font_letter;
//                   p_typer->cursor_position__3i32.x__i32 = 0;
//                   return;
//           }
//           Font_Letter *p_font_letter =
//               get_p_font_letter_from__typer(
//                   p_typer, 
//                   letter);
//           if (!poll_typer_for__cursor_wrapping(
//                   p_typer, 
//                   p_font_letter)) {
//               break;
//           }
//           PLATFORM_put_char_in__typer(
//                   p_gfx_context, 
//                   p_typer, 
//                   letter);
//           offset_typer_by__font_letter(
//                   p_typer, 
//                   p_font_letter);
//       } while (--max_length_of__c_string
//               && *(++c_string));
//   }
