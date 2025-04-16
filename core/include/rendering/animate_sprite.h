#ifndef ANIMATE_SPRITE_H
#define ANIMATE_SPRITE_H

#include "defines_weak.h"
#include "timer.h"
#include <defines.h>

// static inline
// enum Sprite_Animation_Kind get_animation_kind_from__sprite(
//         Sprite *p_sprite) {
//     return p_sprite->the_kind_of_animation__this_sprite_has;
// }
// 
// static inline
// bool is_animation_playing__this_kind_of__animation(
//         Sprite *p_sprite,
//         enum Sprite_Animation_Kind the_kind_of__animation) {
//     return
//         p_sprite->the_kind_of_animation__this_sprite_has
//         == the_kind_of__animation
//         ;
// }
// 
// static inline
// bool is_animation_finished(
//         Sprite *p_sprite) {
//     return
//         is_timer_u32__elapsed(
//                 &p_sprite->animation_timer__u32);
// }
// 
// static inline
// bool is_animation_not__active(
//         Sprite *p_sprite) {
//     return p_sprite->the_kind_of_animation__this_sprite_has
//         == Sprite_Animation_Kind__None
//         ;
// }
// 
// static inline 
// uint32_t get_sprite_frame (
//         uint32_t col, uint32_t row,
//         uint32_t cols_per_row) {
//     return
//         col
//         + (row * cols_per_row);
// }
// 
// static inline
// bool poll_animation(
//         Sprite *p_sprite) {
//     return poll_timer_u32(&p_sprite->animation_timer__u32);
// }
// 
// void set_animation_and__timer(
//         Sprite *p_sprite,
//         enum Sprite_Animation_Kind the_kind_of__sprite_animation,
//         Index__u8 frame__initial,
//         Index__u8 frame__current,
//         Index__u8 frame__final,
//         Timer__u32 animation_timer__u32);
// 
// static inline
// void set_animation(
//         Sprite *p_sprite,
//         enum Sprite_Animation_Kind the_kind_of__sprite_animation,
//         Index__u8 frame__initial,
//         Index__u8 frame__current,
//         Index__u8 frame__final) {
//     set_animation_and__timer(
//             p_sprite, 
//             the_kind_of__sprite_animation,
//             frame__initial,
//             frame__current,
//             frame__final,
//             (Timer__u32){
//                 p_sprite
//                 ->animation_timer__u32
//                 .start__u32,
//                 p_sprite
//                 ->animation_timer__u32
//                 .start__u32
//             });
// }
// 
// static inline
// void set_animation__direction(
//         Sprite *p_sprite,
//         Direction__u8 direction) {
//     p_sprite->direction__requested =
//         direction;
// }
// 
// uint32_t get_animation_frame_offset_for__direction(
//         Direction__u8 direction,
//         uint32_t cols_per_row);

#endif
