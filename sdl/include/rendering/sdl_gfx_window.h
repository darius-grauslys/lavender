#ifndef SDL_GFX_WINDOW_H
#define SDL_GFX_WINDOW_H

#include "defines.h"
#include "defines_weak.h"
#include "vectors.h"
#include <sdl_defines.h>

void SDL_initialize_gfx_window(
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window);

void SDL_compose_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window);

void SDL_render_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window);

static inline
bool SDL_is_gfx_window__allocated(
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
    return 
        p_PLATFORM_gfx_window
        && p_PLATFORM_gfx_window
        ->is_allocated
        ;
}

static inline
void SDL_set_gfx_window_as__allocated(
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
    p_PLATFORM_gfx_window
        ->is_allocated = true;
}

static inline
void SDL_set_gfx_window_as__deallocated(
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window) {
    p_PLATFORM_gfx_window
        ->is_allocated = false;
}

#endif
