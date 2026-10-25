// Review:
// - File: core/source/rendering/sprite.c
// - Lines: 113 - 125
//   void set_sprite_animation(
//           Sprite_Context *p_sprite_context,
//           Sprite *p_sprite,
//           Sprite_Animation_Kind the_kind_of__sprite_animation) {
//       if (p_sprite->animation.the_kind_of_animation__this_sprite_has
//               == the_kind_of__sprite_animation) {
//           return;
//       }
//       p_sprite->animation =
//           get_sprite_animation_from__sprite_context(
//                   p_sprite_context, 
//                   the_kind_of__sprite_animation);
//   }
