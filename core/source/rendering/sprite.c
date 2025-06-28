#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/sprite_animation.h"
#include "rendering/texture.h"
#include "serialization/serialization_header.h"
#include <rendering/sprite.h>
#include <rendering/sprite_manager.h>
#include <defines.h>
#include "timer.h"
#include "types/implemented/sprite_animation_group_kind.h"
#include "types/implemented/sprite_animation_kind.h"
#include "world/world.h"

void poll_sprite_animation_loop(
        Sprite_Manager *p_sprite_manager,
        Sprite *p_sprite) {
    if (is_sprite_animation__NOT_looping(
                get_p_sprite_animation_from__sprite(
                    p_sprite))) {
        return;
    }
    set_sprite_as__needing_graphics_update(p_sprite);
    Sprite_Animation *p_sprite_animation =
        get_p_sprite_animation_from__sprite(p_sprite);
    if (p_sprite->index_of__sprite_frame + 1
            < p_sprite_animation->sprite_animation__initial_frame__u8
            + p_sprite_animation
            ->sprite_animation__quantity_of__frames__u8) {
        p_sprite->index_of__sprite_frame++;
        return;
    }
    p_sprite->index_of__sprite_frame =
        p_sprite_animation->sprite_animation__initial_frame__u8;
    switch (get_the_kind_of__sprite_animation_group_of__this_sprite(
                p_sprite)) {
        case Sprite_Animation_Group_Kind__None:
            break;
        default:
            ;
            Sprite_Animation_Group_Set *p_sprite_animation_group =
                get_p_sprite_animation_group_from__sprite_manager(
                        p_sprite_manager,
                        get_the_kind_of__sprite_animation_group_of__this_sprite(
                            p_sprite));
            Index__u8 quantity_of__columns =
                get_length_of__texture_flag__width(
                        p_sprite
                        ->texture_for__sprite_to__sample
                        .texture_flags)
                / get_length_of__texture_flag__width(
                        p_sprite
                        ->texture_of__sprite
                        .texture_flags);

            Index__u8 raw_index =
                p_sprite_animation_group
                ->index_of__sprite_animation_group_in__group_set_u8
                * p_sprite_animation_group
                    ->quantity_of__columns_in__sprite_animation_group__u4
                ;
            Index__u8 column_index =
                raw_index
                % get_length_of__texture_flag__width(
                        p_sprite->texture_for__sprite_to__sample
                        .texture_flags)
                ;
            Index__u8 row_index_by__columns =
                (raw_index
                / get_length_of__texture_flag__width(
                        p_sprite->texture_for__sprite_to__sample
                        .texture_flags))
                * p_sprite_animation_group
                ->quantity_of__rows_in__sprite_animation_group__u4;
                ;

            p_sprite->index_of__sprite_frame +=
                column_index
                + row_index_by__columns;
    }
}

void m_sprite_animation_handler__default(
        Sprite *p_this_sprite,
        Game *p_game,
        Sprite_Manager *p_sprite_manager) {
    Sprite_Animation *p_sprite_animation =
        get_p_sprite_animation_from__sprite(p_this_sprite);
    if (poll_timer_u8(
                &p_sprite_animation->animation_timer__u8)) {
        reset_timer_u8(&p_sprite_animation->animation_timer__u8);
        poll_sprite_animation_loop(
                p_sprite_manager, 
                p_this_sprite);
        return;
    }
}

void poll_sprite_for__animation(
        Game *p_game,
        Sprite *p_sprite,
        Sprite_Manager *p_sprite_manager) {
    if (!is_sprite__enabled(p_sprite)
            || !p_sprite->m_sprite_animation_handler) {
        return;
    }
    p_sprite->m_sprite_animation_handler(
            p_sprite,
            p_game,
            p_sprite_manager);
}

void set_sprite_animation(
        Sprite_Manager *p_sprite_manager,
        Sprite *p_sprite,
        Sprite_Animation_Kind the_kind_of__sprite_animation) {
    if (p_sprite->animation.the_kind_of_animation__this_sprite_has
            == the_kind_of__sprite_animation) {
        return;
    }
    p_sprite->animation =
        get_sprite_animation_from__sprite_manager(
                p_sprite_manager, 
                the_kind_of__sprite_animation);
}
