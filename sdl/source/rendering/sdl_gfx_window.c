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
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    f_SDL_Compose_Gfx_Window f_SDL_compose_gfx_window =
        get_p_gfx_context_from__game(p_game)
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
            p_game,
            p_gfx_window);
}

void SDL_compose_ui_span_in__gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window,
        Quantity__u32 width_of__ui_tile_span,
        Quantity__u32 height_of__ui_tile_span,
        Index__u32 index_x__u32,
        Index__u32 index_y__u32) {
    f_SDL_Compose_UI_Span_In__Gfx_Window f_SDL_compose_ui_span_in__gfx_window =
        get_p_gfx_context_from__game(p_game)
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_compose_ui_span_in__gfx_window
        ;

#ifndef NDEBUG
    if (!f_SDL_compose_ui_span_in__gfx_window) {
        debug_warning("Did you forget to initialize a graphics backend?");
        debug_abort("SDL_compose_ui_span_in__gfx_window, f_SDL_compose_ui_span_in__gfx_window == 0.");
        return;
    }
#endif

    f_SDL_compose_ui_span_in__gfx_window(
            p_game,
            p_gfx_window,
            width_of__ui_tile_span,
            height_of__ui_tile_span,
            index_x__u32,
            index_y__u32);
}

void SDL_render_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window) {

    f_SDL_Render_Gfx_Window f_SDL_render_gfx_window =
        get_p_gfx_context_from__game(p_game) 
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
            p_game,
            p_gfx_window);
}

void PLATFORM_compose_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    SDL_compose_gfx_window(
            p_game,
            p_gfx_window);
}

void PLATFORM_compose_ui_span_in__gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window,
        Quantity__u32 width_of__ui_tile_span,
        Quantity__u32 height_of__ui_tile_span,
        Index__u32 index_x__u32,
        Index__u32 index_y__u32) {
    SDL_compose_ui_span_in__gfx_window(
            p_game,
            p_gfx_window,
            width_of__ui_tile_span,
            height_of__ui_tile_span,
            index_x__u32,
            index_y__u32);
}

void PLATFORM_render_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    SDL_render_gfx_window(
            p_game, 
            p_gfx_window);
}
