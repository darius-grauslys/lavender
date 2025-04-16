#ifndef SPRITE_MANAGER_H
#define SPRITE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/sprite_animation_kind.h"

void initialize_sprite_manager(
        Sprite_Manager *p_sprite_manager);

Sprite *allocate_sprite_from__sprite_manager(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Graphics_Window *p_gfx_window,
        Identifier__u32 uuid__u32,
        PLATFORM_Texture *p_PLATFORM_texture_to__sample_by__sprite,
        Texture_Flags texture_flags_for__sprite);

void release_sprite_from__sprite_manager(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Sprite *p_sprite);

Sprite *get_p_sprite_by__uuid_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Identifier__u32 uuid__u32);

void render_sprites_in__sprite_manager(
        Gfx_Context *p_gfx_context,
        Sprite_Manager *p_sprite_manager,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Graphics_Window *p_gfx_window);

static inline
void register_sprite_animation_into__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Kind the_kind_of__sprite_animation,
        Sprite_Animation sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("register_sprite_animation_into__sprite_manager, p_sprite_manager == 0.");
        return;
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("register_sprite_animation_into__sprite_manager, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return;
    }
#endif
    p_sprite_manager->sprite_animations[
        the_kind_of__sprite_animation] = sprite_animation;
}

static inline
Sprite_Animation get_sprite_animation_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Animation_Kind the_kind_of__sprite_animation) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("get_sprite_animation_from__sprite_manager, p_sprite_manager == 0.");
        return (Sprite_Animation){0};
    }
    if (the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown) {
        debug_error("get_sprite_animation_from__sprite_manager, the_kind_of__sprite_animation >= Sprite_Animation_Kind__Unknown.");
        return (Sprite_Animation){0};
    }
#endif
    return p_sprite_manager->sprite_animations[
        the_kind_of__sprite_animation];
}

#endif
