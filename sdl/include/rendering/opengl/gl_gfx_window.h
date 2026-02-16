#ifndef GL_GFX_WINDOW_H
#define GL_GFX_WINDOW_H

#include "defines_weak.h"
#include "rendering/opengl/gl_defines.h"

void GL_allocate_gfx_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window,
        Texture_Flags texture_flags);

void GL_compose_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window);

void GL_compose_ui_span_in__gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window,
        Quantity__u32 width_of__ui_tile_span,
        Quantity__u32 height_of__ui_tile_span,
        Index__u32 index_x__u32,
        Index__u32 index_y__u32);

void GL_render_gfx_window(
        Game *p_game,
        Graphics_Window *p_gfx_window);

void GL_release_gfx_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window);

#endif
