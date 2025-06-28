#ifndef SPRITE_ANIMATION_H
#define SPRITE_ANIMATION_H

#include "defines.h"

static inline
bool is_sprite_animation__NOT_looping(
        Sprite_Animation *p_sprite_animation) {
    return p_sprite_animation->sprite_animation__flags__u3
        & SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING
        ;
}

static inline
bool is_sprite_animation__looping(
        Sprite_Animation *p_sprite_animation) {
    return !(p_sprite_animation->sprite_animation__flags__u3
        & SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING)
        ;
}

static inline
void set_sprite_animation_as__looping(
        Sprite_Animation *p_sprite_animation) {
    p_sprite_animation->sprite_animation__flags__u3 &=
        ~SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING
        ;
}

static inline
void set_sprite_animation_as__NOT_looping(
        Sprite_Animation *p_sprite_animation) {
    p_sprite_animation->sprite_animation__flags__u3 |=
        SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING
        ;
}

static inline
bool is_sprite_animation__offset_by__direction(
        Sprite_Animation *p_sprite_animation) {
    return p_sprite_animation->sprite_animation__flags__u3
        & SPRITE_ANIMATION_FLAG__IS_OFFSET_BY__DIRECTION
        ;
}

static inline
void set_sprite_animation_as__NOT_offset_by__direction(
        Sprite_Animation *p_sprite_animation) {
    p_sprite_animation->sprite_animation__flags__u3 &=
        ~SPRITE_ANIMATION_FLAG__IS_OFFSET_BY__DIRECTION
        ;
}

static inline
void set_sprite_animation_as__offset_by__direction(
        Sprite_Animation *p_sprite_animation) {
    p_sprite_animation->sprite_animation__flags__u3 |=
        SPRITE_ANIMATION_FLAG__IS_OFFSET_BY__DIRECTION
        ;
}

#endif
