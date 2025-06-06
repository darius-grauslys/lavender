#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/sprite_animation.h"
#include "serialization/serialization_header.h"
#include <rendering/sprite.h>
#include <defines.h>
#include "timer.h"
#include "types/implemented/sprite_animation_kind.h"
#include "world/world.h"

void m_sprite_animation_handler__default(
        Sprite *p_this_sprite,
        Game *p_game) {
    Sprite_Animation *p_sprite_animation =
        &p_this_sprite->animation;
    if (poll_timer_u8(
                &p_sprite_animation->animation_timer__u8)) {
        reset_timer_u8(&p_sprite_animation->animation_timer__u8);
        if (p_this_sprite->index_of__sprite_frame + 1
                >= p_sprite_animation->sprite_animation__initial_frame__u8
                + p_sprite_animation->sprite_animation__quantity_of__frames__u8) {
            p_this_sprite->index_of__sprite_frame =
                p_sprite_animation->sprite_animation__initial_frame__u8;
        } else {
            p_this_sprite->index_of__sprite_frame++;
        }
        set_sprite_as__needing_graphics_update(p_this_sprite);
        return;
    }
}

void poll_sprite_for__animation(
        Game *p_game,
        Sprite *p_sprite) {
    if (!is_sprite__enabled(p_sprite)
            || !p_sprite->m_sprite_animation_handler) {
        return;
    }
    p_sprite->m_sprite_animation_handler(
            p_sprite,
            p_game);
}
