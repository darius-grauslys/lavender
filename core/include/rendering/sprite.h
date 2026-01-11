#ifndef SPRITE_H
#define SPRITE_H

#include "defines_weak.h"
#include "platform.h"
#include "rendering/texture.h"
#include "serialization/serialization_header.h"
#include "types/implemented/sprite_animation_group_kind.h"
#include "types/implemented/sprite_animation_kind.h"
#include <defines.h>

void m_sprite_animation_handler__default(
        Sprite *p_this_sprite,
        Game *p_game,
        Sprite_Context *p_sprite_context);

void poll_sprite_for__animation(
        Game *p_game,
        Sprite *p_sprite,
        Sprite_Context *p_sprite_context);

void set_sprite_animation(
        Sprite_Context *p_sprite_context,
        Sprite *p_sprite,
        Sprite_Animation_Kind the_kind_of__sprite_animation);

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

static inline
Sprite_Animation *get_p_sprite_animation_from__sprite(
        Sprite *p_sprite) {
    return &p_sprite->animation;
}

static inline
Sprite_Animation_Group_Kind 
get_the_kind_of__sprite_animation_group_of__this_sprite(
        Sprite *p_sprite) {
    return p_sprite->the_kind_of__sprite__animation_group;
}

#endif
