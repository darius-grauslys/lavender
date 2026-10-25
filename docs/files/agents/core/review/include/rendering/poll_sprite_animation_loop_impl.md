// Review:
// - File: core/source/rendering/sprite.c
// - Lines: 15 - 81
//   void poll_sprite_animation_loop(
//           Sprite_Context *p_sprite_context,
//           Sprite *p_sprite) {
//       if (is_sprite_animation__NOT_looping(
//                   get_p_sprite_animation_from__sprite(
//                       p_sprite))) {
//           return;
//       }
//       set_sprite_as__needing_graphics_update(p_sprite);
//       Sprite_Animation *p_sprite_animation =
//           get_p_sprite_animation_from__sprite(p_sprite);
//       if (p_sprite->index_of__sprite_frame + 1
//               < p_sprite_animation->sprite_animation__initial_frame__u8
//               + p_sprite_animation
//               ->sprite_animation__quantity_of__frames__u8) {
//           p_sprite->index_of__sprite_frame++;
//           return;
//       }
//       p_sprite->index_of__sprite_frame =
//           p_sprite_animation->sprite_animation__initial_frame__u8;
//       switch (get_the_kind_of__sprite_animation_group_of__this_sprite(
//                   p_sprite)) {
//           case Sprite_Animation_Group_Kind__None:
//               break;
//           default:
//               ;
//               Sprite_Animation_Group_Set *p_sprite_animation_group =
//                   get_p_sprite_animation_group_from__sprite_context(
//                           p_sprite_context,
//                           get_the_kind_of__sprite_animation_group_of__this_sprite(
//                               p_sprite));
//               Index__u8 quantity_of__columns =
//                   get_length_of__texture_flag__width(
//                           p_sprite
//                           ->texture_for__sprite_to__sample
//                           .texture_flags)
//                   / get_length_of__texture_flag__width(
//                           p_sprite
//                           ->texture_of__sprite
//                           .texture_flags);
//
//               Index__u8 raw_index =
//                   p_sprite_animation_group
//                   ->index_of__sprite_animation_group_in__group_set_u8
//                   * p_sprite_animation_group
//                       ->quantity_of__columns_in__sprite_animation_group__u4
//                   ;
//               Index__u8 column_index =
//                   raw_index
//                   % get_length_of__texture_flag__width(
//                           p_sprite->texture_for__sprite_to__sample
//                           .texture_flags)
//                   ;
//               Index__u8 row_index_by__columns =
//                   (raw_index
//                   / get_length_of__texture_flag__width(
//                           p_sprite->texture_for__sprite_to__sample
//                           .texture_flags))
//                   * p_sprite_animation_group
//                   ->quantity_of__rows_in__sprite_animation_group__u4;
//                   ;
//
//               p_sprite->index_of__sprite_frame +=
//                   column_index
//                   + row_index_by__columns;
//       }
//   }
