#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "rendering/graphics_window.h"
#include "rendering/sdl_gfx_context.h"
#include "rendering/sdl_sprite.h"
#include "rendering/texture.h"
#include "sdl_defines.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile_map_manager.h"
#include <rendering/sdl_gfx_window.h>
#include "vectors.h"

void SDL_initialize_gfx_window(
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
    initialize_texture(
            p_PLATFORM_gfx_window
            ->SDL_graphics_window__texture);
    p_PLATFORM_gfx_window
        ->p_SDL_graphics_window__data = 0;
    p_PLATFORM_gfx_window
        ->is_allocated = false;
}

void SDL_compose_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {
    f_SDL_Compose_Gfx_Window f_SDL_compose_gfx_window =
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_compose_gfx_window
        ;

#ifndef NDEBUG
    if (!f_SDL_compose_gfx_window) {
        debug_warning("Did you forget to initialize a graphics backend?");
        debug_abort("SDL_compose_gfx_window, f_SDL_compose_gfx_window == 0.");
        return;
    }
#endif

    f_SDL_compose_gfx_window(
            p_gfx_context,
            p_gfx_window);
}

void SDL_render_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {

    f_SDL_Render_Gfx_Window f_SDL_render_gfx_window =
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_render_gfx_window
        ;

#ifndef NDEBUG
    if (!f_SDL_render_gfx_window) {
        debug_warning("Did you forget to initialize a graphics backend?");
        debug_abort("SDL_render_gfx_window, f_SDL_render_gfx_window == 0.");
        return;
    }
#endif

    f_SDL_render_gfx_window(
            p_gfx_context,
            p_gfx_window);
}

void PLATFORM_compose_gfx_window(
        Gfx_Context *p_gfx_context, 
        Graphics_Window *p_gfx_window) {
    SDL_compose_gfx_window(
            p_gfx_context, 
            p_gfx_window);
}

void PLATFORM_render_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {
    SDL_render_gfx_window(
            p_gfx_context, 
            p_gfx_window);
}
