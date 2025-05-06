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

void initialize_sprite(
        Sprite *sprite,
        Texture_Flags texture_flags_for__sprite) {
    memset(sprite,
            0,
            sizeof(Sprite));
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header *)sprite, 
            sizeof(Sprite));
}

void poll_sprite_for__x_flip(
        Sprite *p_sprite,
        Direction__u8 direction) {
    if (direction & DIRECTION__WEST) {
        if (!is_sprite__flipped_x(p_sprite)) {
            set_sprite_as__needing_graphics_update(
                    p_sprite);
        }
        set_sprite_as__flipped_x(p_sprite);
    } else if (direction & DIRECTION__EAST) {
        if (is_sprite__flipped_x(p_sprite)) {
            set_sprite_as__needing_graphics_update(
                    p_sprite);
        }
        set_sprite_as__NOT_flipped_x(p_sprite);
    }
}

Index__u16 get_offset_of__sprite_frame_for__direction(
        Sprite *p_sprite) {
    Direction__u8 direction =
        (p_sprite->direction__delta__u8)
        ? p_sprite->direction__delta__u8
        : p_sprite->direction__old__u8
        ;
    if (direction & DIRECTION__NORTH) {
        return p_sprite->animation_group
            .quantity_of__columns_in__sprite_animation_group__u4
            * 2
            ;
    } else if (direction & DIRECTION__SOUTH) {
        return p_sprite->animation_group
            .quantity_of__columns_in__sprite_animation_group__u4
            ;
    }
    return 0;
}

Direction__u8 poll_sprite_for__direction(
        Game *p_game,
        Sprite *p_sprite) {
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                GET_UUID_P(p_sprite));

    if (!p_hitbox_aabb) {
        return DIRECTION__NONE;
    }

    return 
        get_movement_direction_of__hitbox(
                p_hitbox_aabb);
}

void update_sprite_animation_for__direction(
        Sprite *p_sprite,
        Direction__u8 direction) {

    poll_sprite_for__x_flip(
            p_sprite, 
            direction);
    if (!is_sprite_animation__offset_by__direction(
                &p_sprite->animation)) {
        return;
    }

    Direction__u8 direction__delta_check =
        (direction ^ p_sprite->direction__old__u8)
            & direction
        ;
    p_sprite->direction__delta__u8 = 
        direction__delta_check
        ? direction__delta_check
        : (direction == p_sprite->direction__old__u8)
            ? p_sprite->direction__delta__u8
            : direction
            ;
    p_sprite->direction__old__u8 = direction;
    Index__u16 offset =
        get_offset_of__sprite_frame_for__direction(
                p_sprite);
    p_sprite->index_of__sprite_frame =
        p_sprite->animation.
        sprite_animation__initial_frame__u8
        + offset;
    p_sprite->index_of__sprite_frame__final =
        p_sprite->animation.
        sprite_animation__initial_frame__u8
        + p_sprite->animation
        .sprite_animation__quantity_of__frames__u8
        + offset;
}

bool poll_sprite_animation(
        Game *p_game,
        Sprite *p_sprite) {

    Direction__u8 direction =
        poll_sprite_for__direction(
                p_game, 
                p_sprite);

    if (direction != p_sprite->direction__old__u8) {
        if (direction) {
            update_sprite_animation_for__direction(
                    p_sprite, 
                    direction);
        } else {
            p_sprite->direction__delta__u8 = 0;
        }
    }

    if (poll_timer_u8(&p_sprite->animation_timer__u8)) {
        reset_timer_u8(&p_sprite->animation_timer__u8);
        if (p_sprite->index_of__sprite_frame + 1
                >= p_sprite->index_of__sprite_frame__final) {
            if (is_sprite_animation__NOT_looping(
                        &p_sprite->animation)) {
                return true;
            }
            set_sprite_as__needing_graphics_update(
                    p_sprite);
            p_sprite->index_of__sprite_frame =
                p_sprite->animation.sprite_animation__initial_frame__u8
                + get_offset_of__sprite_frame_for__direction(
                        p_sprite);
            return true;
        }
        set_sprite_as__needing_graphics_update(
                p_sprite);
        p_sprite->index_of__sprite_frame++;
    } 

    return false;
}

void set_sprite_animation(
        Game *p_game,
        Sprite *p_sprite,
        Sprite_Animation_Kind the_kind_of__sprite_animation,
        Sprite_Animation sprite_animation,
        Sprite_Animation_Group sprite_animation_group) {
    if (p_sprite->the_kind_of_animation__this_sprite_has
            == the_kind_of__sprite_animation) {
        return;
    }
    initialize_timer_u8(
            &p_sprite->animation_timer__u8, 
            sprite_animation.sprite_animation__ticks_per__frame__u5);
    p_sprite->animation_group = sprite_animation_group;
    p_sprite->animation = sprite_animation;
    p_sprite->index_of__sprite_frame =
        sprite_animation.sprite_animation__initial_frame__u8;
    p_sprite->index_of__sprite_frame__final =
        sprite_animation.sprite_animation__initial_frame__u8
        + sprite_animation.sprite_animation__quantity_of__frames__u8;
    set_sprite_as__needing_graphics_update(
            p_sprite);
    p_sprite->the_kind_of_animation__this_sprite_has =
        the_kind_of__sprite_animation;

    update_sprite_animation_for__direction(
            p_sprite, 
            p_sprite->direction__old__u8);
}
