#include "debug/debug.h"
#include "defines_weak.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "random.h"
#include "rendering/sdl_gfx_context.h"
#include "sdl_defines.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include <rendering/sdl_texture_manager.h>
#include <rendering/sdl_texture.h>

static inline
PLATFORM_Texture *SDL_get_p_PLATFORM_texture_by__index_from__texture_manager(
        SDL_Texture_Manager *p_SDL_texture_manager,
        Index__u32 index_of__sdl_texture) {
#ifndef NDEBUG
    if (index_of__sdl_texture
            >= MAX_QUANTITY_OF__TEXTURES) {
        debug_error("SDL_get_p_PLATFORM_texture_by__index_from__texture_manager, index out of bounds: %d,%d", index_of__sdl_texture, MAX_QUANTITY_OF__TEXTURES);
        return 0;
    }
#endif
    return &p_SDL_texture_manager
        ->SDL_textures[index_of__sdl_texture]
        ;
}

void SDL_initialize_texture_manager(
        SDL_Texture_Manager *p_SDL_texture_manager) {
    memset(p_SDL_texture_manager,
            0,
            sizeof(SDL_Texture_Manager));

    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_SDL_texture_manager->SDL_textures, 
            MAX_QUANTITY_OF__TEXTURES, 
            sizeof(PLATFORM_Texture));

    initialize_repeatable_psuedo_random(
            &p_SDL_texture_manager->randomizer, 
            (u32)(u64)p_SDL_texture_manager);
}

void SDL_release_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Texture *p_PLATFORM_texture) {
    p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_release_texture(
                p_PLATFORM_texture);
    SDL_release_texture_from__texture_manager(
            SDL_get_p_texture_manager_from__gfx_context(
                p_PLATFORM_gfx_context), 
            p_PLATFORM_texture);
}

PLATFORM_Texture *SDL_allocate_texture_with__texture_manager(
        SDL_Texture_Manager *p_SDL_texture_manager) {
    return (PLATFORM_Texture*)allocate_serialization_header(
            (Serialization_Header *)p_SDL_texture_manager->SDL_textures, 
            MAX_QUANTITY_OF__TEXTURES, 
            &p_SDL_texture_manager->randomizer);
}

void SDL_release_texture_from__texture_manager(
        SDL_Texture_Manager *p_SDL_texture_manager,
        PLATFORM_Texture *p_PLATFORM_texture) {
    u16 index =
        p_PLATFORM_texture
        - p_SDL_texture_manager->SDL_textures
        ;

    if (index < 0 || index >= MAX_QUANTITY_OF__TEXTURES) {
        debug_warning("This might cause a GPU memory leak!");
        debug_abort("SDL::SDL_release_texture_from__texture_manager, p_PLATFORM_texture is not allocated with this manager, or is invalid.");
        return;
    }

    DEALLOCATE_P(p_PLATFORM_texture);
}

void SDL_dispose_texture_manager(
        SDL_Texture_Manager *p_SDL_texture_manager) {
    for (Index__u16 index_of__sdl_texture = 0;
            index_of__sdl_texture < MAX_QUANTITY_OF__TEXTURES;
            index_of__sdl_texture++) {
        PLATFORM_Texture *p_PLATFORM_texture =
            SDL_get_p_PLATFORM_texture_by__index_from__texture_manager(
                    p_SDL_texture_manager,
                    index_of__sdl_texture);
        if (IS_DEALLOCATED(p_PLATFORM_texture)) {
            continue;
        }

        SDL_release_texture(
                &__SDL_Gfx_Context,
                p_PLATFORM_texture);
    }
}

bool PLATFORM_allocate_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        Texture *p_OUT_texture) {
#ifndef NDEBUG
    if (!p_PLATFORM_gfx_context) {
        debug_error("SDL::PLATFORM_allocate_texture, p_PLATFORM_gfx_context == 0.");
        return true;
    }
    if (!p_OUT_texture) {
        debug_error("SDL::PLATFORM_allocate_texture, p_OUT_texture == 0.");
        return true;
    }
#endif
    p_OUT_texture->p_PLATFORM_texture = 
        __SDL_Gfx_Context
        .SDL_gfx_sub_context__wrapper
        .f_SDL_allocate_texture(
                p_PLATFORM_gfx_context,
                texture_flags);
    p_OUT_texture->texture_flags =
        texture_flags;

    return !p_OUT_texture->p_PLATFORM_texture;
}

bool PLATFORM_allocate_texture_with__path(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        const char *path,
        Texture *p_OUT_texture) {
#ifndef NDEBUG
    if (!p_PLATFORM_gfx_context) {
        debug_error("SDL::PLATFORM_allocate_texture_with__path, p_PLATFORM_gfx_context == 0.");
        return true;
    }
    if (!path) {
        debug_error("SDL::PLATFORM_allocate_texture_with__path, path == 0.");
        return true;
    }
    if (!p_OUT_texture) {
        debug_error("SDL::PLATFORM_allocate_texture_with__path, p_OUT_texture == 0.");
        return true;
    }
#endif
    p_OUT_texture->p_PLATFORM_texture = 
        __SDL_Gfx_Context
        .SDL_gfx_sub_context__wrapper
        .f_SDL_allocate_texture_with__path(
                p_PLATFORM_gfx_context,
                texture_flags,
                path);
    p_OUT_texture->texture_flags =
        texture_flags;
    return !p_OUT_texture->p_PLATFORM_texture;
}

void PLATFORM_use_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture texture) {
    p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_use_texture(
                texture.p_PLATFORM_texture);
}

void PLATFORM_release_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture texture) {
    SDL_release_texture(
            p_PLATFORM_gfx_context, 
            texture.p_PLATFORM_texture);
}
