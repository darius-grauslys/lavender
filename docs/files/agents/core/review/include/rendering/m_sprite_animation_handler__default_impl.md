// Review:
// - File: core/source/rendering/sprite.c
// - Lines: 83 - 97
//   void m_sprite_animation_handler__default(
//           Sprite *p_this_sprite,
//           Game *p_game,
//           Sprite_Context *p_sprite_context) {
//       Sprite_Animation *p_sprite_animation =
//           get_p_sprite_animation_from__sprite(p_this_sprite);
//       if (poll_timer_u8(
//                   &p_sprite_animation->animation_timer__u8)) {
//           reset_timer_u8(&p_sprite_animation->animation_timer__u8);
//           poll_sprite_animation_loop(
//                   p_sprite_context, 
//                   p_this_sprite);
//           return;
//       }
//   }
