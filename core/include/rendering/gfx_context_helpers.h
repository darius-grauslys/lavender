#ifndef GRAPHICS_CONTEXT_HELPERS_H
#define GRAPHICS_CONTEXT_HELPERS_H

#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "rendering/sprite_manager.h"
#include <defines.h>

/*
 * This header file is created to provide static inline helpers for
 * common constructions in the graphics context at a Lavender CORE level.
 */


static inline
Graphics_Window *GFX_CONTEXT_allocate_graphics_window_with__ui_manager(
        Game *p_game,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    Gfx_Context *p_gfx_context = get_p_gfx_context_from__game(p_game);

    Graphics_Window *p_graphics_window = 
        allocate_graphics_window_from__graphics_window_manager(
            p_gfx_context, 
            get_p_graphics_window_manager_from__gfx_context(p_gfx_context), 
            texture_flags_for__gfx_window);
    
    if (!p_graphics_window) {
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager, failed to allocate graphics window.");
        return 0;
    }

    UI_Manager *p_ui_manager = 
        allocate_ui_manager_for__graphics_window(
            p_gfx_context, 
            p_graphics_window);

    if (!p_ui_manager) {
        release_graphics_window_from__graphics_window_manager(
                p_game, 
                p_graphics_window);
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager, failed to allocate ui_manager.");
        return 0;
    }
    
    return p_graphics_window;
}

static inline
Graphics_Window *GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool(
        Game *p_game,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    Graphics_Window *p_graphics_window = 
        GFX_CONTEXT_allocate_graphics_window_with__ui_manager(
                p_game, 
                uuid__u32, 
                texture_flags_for__gfx_window);

    if (!p_graphics_window) {
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool, failed to allocate graphics_window.");
        return 0;
    }

    Sprite_Pool *p_sprite_pool =
        allocate_sprite_pool_from__sprite_manager(
                get_p_sprite_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                uuid__u32);

    if (!p_sprite_pool) {
        release_graphics_window_from__graphics_window_manager(
                p_game, 
                p_graphics_window);
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool, failed to allocate sprite pool.");
        return 0;
    }
    
    return p_graphics_window;
}

static inline
Graphics_Window *GFX_CONTEXT_allocate_graphics_window_with__sprite_pool(
        Game *p_game,
        Identifier__u32 uuid__u32,
        Texture_Flags texture_flags_for__gfx_window) {
    Gfx_Context *p_gfx_context = get_p_gfx_context_from__game(p_game);

    Graphics_Window *p_graphics_window = 
        allocate_graphics_window_from__graphics_window_manager(
            p_gfx_context, 
            get_p_graphics_window_manager_from__gfx_context(p_gfx_context), 
            texture_flags_for__gfx_window);

    if (!p_graphics_window) {
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager, failed to allocate graphics window.");
        return 0;
    }
    
    Sprite_Pool *p_sprite_pool =
        allocate_sprite_pool_from__sprite_manager(
                get_p_sprite_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                uuid__u32);

    if (!p_sprite_pool) {
        release_graphics_window_from__graphics_window_manager(
                p_game, 
                p_graphics_window);
        debug_error("GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool, failed to allocate sprite pool.");
        return 0;
    }
    
    return p_graphics_window;
}


#endif
