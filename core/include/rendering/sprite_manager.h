#ifndef SPRITE_POOL_H
#define SPRITE_POOL_H

#include "defines.h"
#include "defines_weak.h"
#include "rendering/sprite.h"
#include "types/implemented/sprite_animation_group_kind.h"
#include "types/implemented/sprite_animation_kind.h"

void initialize_sprite_manager(
        Sprite_Manager *p_sprite_manager);

bool allocate_sprite_manager__members(
        Sprite_Manager *p_sprite_manager,
        Quantity__u32 quantity_of__sprites__u32);

Sprite *allocate_sprite_from__sprite_manager(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Graphics_Window *p_gfx_window,
        Identifier__u32 uuid__u32,
        Texture texture_to__sample_by__sprite,
        Texture_Flags texture_flags_for__sprite);

void release_sprite_from__sprite_manager(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Sprite *p_sprite);

Sprite *get_p_sprite_by__uuid_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Identifier__u32 uuid__u32);

void render_sprites_in__sprite_manager(
        Game *p_game,
        Sprite_Context *p_sprite_context,
        Sprite_Manager *p_sprite_manager,
        Graphics_Window *p_gfx_window);

#endif
