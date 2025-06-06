#ifndef SPRITE_H
#define SPRITE_H

#include "defines_weak.h"
#include "platform.h"
#include "rendering/texture.h"
#include "serialization/serialization_header.h"
#include <defines.h>

void initialize_sprite(
        Sprite *sprite);

bool poll_sprite_animation(
        Game *p_game,
        Sprite *p_sprite);

void set_sprite_animation(
        Game *p_game,
        Sprite *p_sprite,
        Sprite_Animation_Kind the_kind_of__sprite_animation,
        Sprite_Animation sprite_animation,
        Sprite_Animation_Group sprite_animation_group);

static inline
Direction__u8 get_cached_direction_of__sprite(
        Sprite *p_sprite) {
    return
        (p_sprite->direction__delta__u8)
        ? p_sprite->direction__delta__u8
        : p_sprite->direction__old__u8
        ;
}

static inline
bool is_sprite__deallocated(Sprite *p_sprite) {
    return IS_DEALLOCATED_P(p_sprite);
}

static inline
bool is_sprite__enabled(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 
        & SPRITE_FLAG__BIT_IS_ENABLED;
}

static inline
bool set_sprite_as__enabled(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 |=
        SPRITE_FLAG__BIT_IS_ENABLED;
}

static inline
bool set_sprite_as__disabled(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 &=
        ~SPRITE_FLAG__BIT_IS_ENABLED;
}

static inline
bool is_sprite__needing_graphics_update(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 
        & SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE;
}

static inline
bool set_sprite_as__needing_graphics_update(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 |=
        SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE;
}

static inline
bool set_sprite_as__NOT_needing_graphics_update(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 &=
        ~SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE;
}

static inline
void set_frame_index_of__sprite(
        Sprite *p_sprite,
        Index__u8 index_of__frame__u8) {
    p_sprite->index_of__sprite_frame =
        index_of__frame__u8;
    set_sprite_as__needing_graphics_update(
            p_sprite);
}

static inline
bool is_sprite__flipped_x(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 
        & SPRITE_FLAG__BIT_IS_FLIPPED_X;
}

static inline
bool set_sprite_as__flipped_x(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 |=
        SPRITE_FLAG__BIT_IS_FLIPPED_X;
}

static inline
bool set_sprite_as__NOT_flipped_x(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 &=
        ~SPRITE_FLAG__BIT_IS_FLIPPED_X;
}

static inline
bool is_sprite__flipped_y(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 
        & SPRITE_FLAG__BIT_IS_FLIPPED_Y;
}

static inline
bool set_sprite_as__flipped_y(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 |=
        SPRITE_FLAG__BIT_IS_FLIPPED_Y;
}

static inline
bool set_sprite_as__NOT_flipped_y(Sprite *p_sprite) {
    return p_sprite->sprite_flags__u8 &=
        ~SPRITE_FLAG__BIT_IS_FLIPPED_Y;
}

#endif
