#include "debug/debug.h"
#include "defines.h"
#include "sdl_defines.h"
#include <rendering/sdl_sprite.h>

void SDL_initialize_sprite(
        Gfx_Context *p_gfx_context,
        PLATFORM_Sprite *p_PLATFORM_sprite) {
    memset(((u8*)p_PLATFORM_sprite) + sizeof(Serialization_Header),
            0,
            sizeof(PLATFORM_Sprite) - sizeof(Serialization_Header));
//     f_SDL_Initialize_Sprite f_SDL_initialize_sprite = 
//         p_gfx_context
//         ->p_PLATFORM_gfx_context
//         ->SDL_gfx_sub_context__wrapper
//         .f_SDL_initialize_sprite;
// #ifndef NDEBUG
//     if (!f_SDL_initialize_sprite) {
//         debug_warning("Did you forget to initialize a graphics backend?");
//         debug_abort("SDL::SDL_initialize_sprite, f_SDL_initialize_sprite == 0.");
//         return;
//     }
// #endif
//     f_SDL_initialize_sprite(
//             p_gfx_context,
//             p_PLATFORM_sprite);
}

void PLATFORM_render_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite *p_sprite,
        Vector__3i32F4 position_of__sprite__3i32F4) {
    f_SDL_Render_Sprite f_SDL_render_sprite = 
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_render_sprite;
#ifndef NDEBUG
    if (!f_SDL_render_sprite) {
        debug_warning("Did you forget to render a graphics backend?");
        debug_abort("SDL::PLATFORM_render_sprite, f_SDL_render_sprite == 0.");
        return;
    }
#endif
    f_SDL_render_sprite(
            p_gfx_context,
            p_gfx_window,
            p_sprite,
            position_of__sprite__3i32F4);
}
