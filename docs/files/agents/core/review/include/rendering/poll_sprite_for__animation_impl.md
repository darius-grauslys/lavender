// Review:
// - File: core/source/rendering/sprite.c
// - Lines: 99 - 111
//   void poll_sprite_for__animation(
//           Game *p_game,
//           Sprite *p_sprite,
//           Sprite_Context *p_sprite_context) {
//       if (!is_sprite__enabled(p_sprite)
//               || !p_sprite->m_sprite_animation_handler) {
//           return;
//       }
//       p_sprite->m_sprite_animation_handler(
//               p_sprite,
//               p_game,
//               p_sprite_context);
//   }
