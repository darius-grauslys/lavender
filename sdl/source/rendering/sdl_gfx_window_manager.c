#include "rendering/sdl_gfx_window_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/sdl_gfx_context.h"
#include "rendering/sdl_gfx_window.h"
#include "rendering/texture.h"
#include "sdl_defines.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile_map.h"
#include "ui/ui_tile_map_manager.h"
#include "rendering/gfx_context.h"
#include "vectors.h"

static inline
PLATFORM_Graphics_Window *SDL_get_p_PLATFORM_gfx_window_by__index_from__manager(
        SDL_Gfx_Window_Manager *p_SDL_gfx_window_manager,
        Index__u32 index_of__gfx_window) {
#ifndef NDEBUG
    if (index_of__gfx_window
            >= PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF) {
        debug_error("SDL_get_p_PLATFORM_gfx_window_by__type_from__manager, index out of bounds.");
        return 0;
    }
#endif

    return &p_SDL_gfx_window_manager
        ->SDL_gfx_windows[index_of__gfx_window];
}

PLATFORM_Graphics_Window *_p_PLATFORM_gfx_window__backbuffer = 0;

void SDL_initialize_gfx_window_manager(
        SDL_Gfx_Window_Manager *p_SDL_gfx_window_manager) {
    for (Index__u32 index_of__gfx_window = 0;
            index_of__gfx_window
            < PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF;
            index_of__gfx_window++) {
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window =
            SDL_get_p_PLATFORM_gfx_window_by__index_from__manager(
                    p_SDL_gfx_window_manager, 
                    index_of__gfx_window);

        SDL_initialize_gfx_window(
                p_PLATFORM_gfx_window);
    }
}

Quantity__u32 PLATFORM_get_provided_windows(
        Gfx_Context *p_gfx_context,
        PLATFORM_Graphics_Window **ptr_array_of__PLATFORM_graphics_windows,
        Texture_Flags *array_of__texture_flags,
        Quantity__u32 quantity_of__ptrs_in_buffer__u32,
        Index__u32 index_of__offset__u32)  {
    if (!quantity_of__ptrs_in_buffer__u32)
        return 1;

    memset(ptr_array_of__PLATFORM_graphics_windows,
            0, 
            sizeof(PLATFORM_Graphics_Window*)
            * quantity_of__ptrs_in_buffer__u32);

    Texture_Flags texture_flags =
        TEXTURE_FLAGS(
            TEXTURE_FLAG__SIZE_256x256,
            0,
            TEXTURE_FLAG__FORMAT__RGBA8888
            );

    if (!_p_PLATFORM_gfx_window__backbuffer) {
        _p_PLATFORM_gfx_window__backbuffer =
            PLATFORM_allocate_gfx_window(
                    p_gfx_context, 
                    texture_flags);
    }

    ptr_array_of__PLATFORM_graphics_windows[0] =
        _p_PLATFORM_gfx_window__backbuffer;
    array_of__texture_flags[0] = texture_flags;

    return 0;
}

PLATFORM_Graphics_Window *PLATFORM_allocate_gfx_window(
        Gfx_Context *p_gfx_context,
        Texture_Flags texture_flags_for__gfx_window) {
    f_SDL_Allocate_Gfx_Window f_sdl_allocate_gfx_window =
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_allocate_gfx_window;

    if (!f_sdl_allocate_gfx_window) {
        debug_error("SDL::PLATFORM_allocate_gfx_window, f_sdl_allocate_gfx_window == 0.");
        return 0;
    }
    
    PLATFORM_Graphics_Window *p_PLATFORM_gfx_window = 
        SDL_allocate_PLATFORM_gfx_window_from__manager(
            SDL_get_p_gfx_window_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context)));
    if (!p_PLATFORM_gfx_window)
        return p_PLATFORM_gfx_window;

    f_sdl_allocate_gfx_window(
            p_gfx_context
            ->p_PLATFORM_gfx_context,
            p_PLATFORM_gfx_window,
            texture_flags_for__gfx_window);

    return p_PLATFORM_gfx_window;
}

void PLATFORM_release_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {
    SDL_release_PLATFORM_gfx_window_from__manager(
            SDL_get_p_gfx_window_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context)),
            p_gfx_window->p_PLATFORM_gfx_window);
}

PLATFORM_Graphics_Window *SDL_allocate_PLATFORM_gfx_window_from__manager(
        SDL_Gfx_Window_Manager *p_SDL_gfx_window_manager) {
    for (Index__u32 index_of__gfx_window = 0;
            index_of__gfx_window
            < PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF;
            index_of__gfx_window++) {
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window =
            SDL_get_p_PLATFORM_gfx_window_by__index_from__manager(
                    p_SDL_gfx_window_manager, 
                    index_of__gfx_window);

        if (SDL_is_gfx_window__allocated(
                    p_PLATFORM_gfx_window)) {
            continue;
        }

        SDL_set_gfx_window_as__allocated(
                p_PLATFORM_gfx_window);

        return p_PLATFORM_gfx_window;
    }

    return 0;
}

void SDL_release_PLATFORM_gfx_window_from__manager(
        SDL_Gfx_Window_Manager *p_SDL_gfx_window_manager,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
#ifndef NDEBUG
    uint32_t index = p_PLATFORM_gfx_window
        - p_SDL_gfx_window_manager->SDL_gfx_windows
        ;
    if (index 
            >= PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF) {
        debug_error("SDL_release_PLATFORM_gfx_window_from__manager, p_PLATFORM_gfx_window was not allocated by this manager.");
        return;
    }
#endif
    SDL_initialize_gfx_window(
            p_PLATFORM_gfx_window);
    if (p_PLATFORM_gfx_window
            == _p_PLATFORM_gfx_window__backbuffer) {
        p_PLATFORM_gfx_window
            ->is_allocated = true;
    }
}

// TODO: move alloc/release into a manager, and take
// that mngr as a pointer parameter
PLATFORM_Graphics_Window *SDL_allocate_gfx_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Camera *p_camera,
        Texture_Flags texture_flags) {

    f_SDL_Allocate_Gfx_Window f_SDL_allocate_gfx_window =
        p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_allocate_gfx_window
        ;

#ifndef NDEBUG
    if (!f_SDL_allocate_gfx_window) {
        debug_warning("Did you forget to initialize a graphics backend?");
        debug_abort("SDL_allocate_gfx_window, f_SDL_allocate_gfx_window == 0.");
        return 0;
    }
#endif

    PLATFORM_Graphics_Window *p_PLATFORM_gfx_window =
        SDL_allocate_PLATFORM_gfx_window_from__manager(
                SDL_get_p_gfx_window_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context));

    if (!p_PLATFORM_gfx_window) {
        debug_error("SDL_allocate_gfx_window, failed to allocate window from manager. Is the manager full?");
        return 0;
    }

    SDL_initialize_gfx_window(
            p_PLATFORM_gfx_window);

    f_SDL_allocate_gfx_window(
            p_PLATFORM_gfx_context,
            p_PLATFORM_gfx_window,
            texture_flags);

    return p_PLATFORM_gfx_window;
}

void SDL_release_gfx_window(
        Game *p_game,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context = 
        get_p_PLATFORM_gfx_context_from__game(
                p_game);

    f_SDL_Release_Gfx_Window f_SDL_release_gfx_window =
        p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_release_gfx_window
        ;

#ifndef NDEBUG
    if (!f_SDL_release_gfx_window) {
        debug_warning("Did you forget to initialize a graphics backend?");
        debug_abort("SDL_release_gfx_window, f_SDL_release_gfx_window == 0.");
        return;
    }
#endif

    f_SDL_release_gfx_window(
            p_PLATFORM_gfx_context,
            p_PLATFORM_gfx_window);

    SDL_release_PLATFORM_gfx_window_from__manager(
            SDL_get_p_gfx_window_manager_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context), 
            p_PLATFORM_gfx_window);
}

