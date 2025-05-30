#include "debug/debug.h"
#include "defines_weak.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "rendering/sdl_gfx_context.h"
#include "rendering/sdl_sprite.h"
#include "rendering/sdl_texture_manager.h"
#include "rendering/texture.h"
#include "sdl_defines.h"
#include <rendering/sdl_sprite_manager.h>
#include "rendering/gfx_context.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include <defines.h>

void SDL_initialize_sprite_manager(
        SDL_Sprite_Manager *p_SDL_sprite_manager) {
    memset(p_SDL_sprite_manager,
            0,
            sizeof(SDL_Sprite_Manager));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_SDL_sprite_manager->SDL_sprites, 
            MAX_QUANTITY_OF__SPRITES, 
            sizeof(PLATFORM_Sprite));
    initialize_repeatable_psuedo_random(
            &p_SDL_sprite_manager->randomizer,
            (u32)(u64)p_SDL_sprite_manager);
}

PLATFORM_Sprite *SDL_allocate_sprite_with__sprite_manager(
        SDL_Sprite_Manager *p_SDL_sprite_manager) {
    return (PLATFORM_Sprite*)allocate_serialization_header(
            (Serialization_Header *)p_SDL_sprite_manager, 
            MAX_QUANTITY_OF__SPRITES, 
            &p_SDL_sprite_manager->randomizer);
}

void SDL_release_sprite_from__sprite_manager(
        SDL_Sprite_Manager *p_SDL_sprite_manager,
        PLATFORM_Sprite *p_PLATFORM_sprite) {
    u16 index =
        p_PLATFORM_sprite
        - p_SDL_sprite_manager
        ->SDL_sprites
        ;
    
    if (index < 0 || index >= MAX_QUANTITY_OF__SPRITES) {
        debug_abort("SDL::SDL_release_sprite_from__sprite_manager, p_PLATFORM_sprite is not allocated with this manager, or is invalid.");
        debug_warning("This might cause a GPU memory leak!");
        return;
    }

    DEALLOCATE_P(p_PLATFORM_sprite);
}

void SDL_dispose_sprite_manager(
        Gfx_Context *p_gfx_context,
        SDL_Sprite_Manager *p_SDL_sprite_manager) {
    for (Index__u16 index_of__sdl_sprite = 0;
            index_of__sdl_sprite < MAX_QUANTITY_OF__SPRITES;
            index_of__sdl_sprite++) {
        PLATFORM_Sprite *p_PLATFORM_sprite =
            &p_SDL_sprite_manager
            ->SDL_sprites[index_of__sdl_sprite];
        if (IS_DEALLOCATED_P(
                    p_PLATFORM_sprite)) {
            continue;
        }

        PLATFORM_release_sprite(
                p_gfx_context,
                p_PLATFORM_sprite);
    }
}

PLATFORM_Sprite *PLATFORM_allocate_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window,
        Sprite *p_sprite,
        Texture_Flags texture_flags_for__sprite) {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context);

    SDL_Sprite_Manager *p_SDL_sprite_manager =
        SDL_get_p_sprite_manager_from__gfx_context(p_PLATFORM_gfx_context);

    p_sprite->p_PLATFORM_sprite =
        SDL_allocate_sprite_with__sprite_manager(
                p_SDL_sprite_manager);

    if (!p_sprite->p_PLATFORM_sprite) {
        debug_error("SDL::PLATFORM_allocate_sprite, failed to allocate sprite.");
        return 0;
    }

    SDL_initialize_sprite(
            p_gfx_context,
            p_sprite);

    p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_allocate_sprite(
                p_gfx_context,
                p_graphics_window,
                p_sprite,
                get_length_of__texture_flag__width(
                    texture_flags_for__sprite),
                get_length_of__texture_flag__height(
                    texture_flags_for__sprite));

    if (!p_sprite->p_PLATFORM_sprite->p_SDL_sprite) {
        SDL_release_sprite_from__sprite_manager(
                p_SDL_sprite_manager,
                p_sprite->p_PLATFORM_sprite);
        return 0;
    }
    
    return p_sprite->p_PLATFORM_sprite;
}

void PLATFORM_release_sprite(
        Gfx_Context *p_gfx_context, 
        PLATFORM_Sprite *p_PLATFORM_sprite) {
    p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_release_sprite(
                p_gfx_context,
                p_PLATFORM_sprite);
    SDL_release_sprite_from__sprite_manager(
            SDL_get_p_sprite_manager_from__gfx_context(
                p_gfx_context
                ->p_PLATFORM_gfx_context), 
            p_PLATFORM_sprite);
}
