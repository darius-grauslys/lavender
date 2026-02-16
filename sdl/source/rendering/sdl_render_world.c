#include "rendering/sdl_render_world.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/gfx_context.h"
#include "sdl_defines.h"
#include "world/world.h"
#include "game.h"

void PLATFORM_compose_world(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    f_SDL_Compose_World f_SDL_compose_world =
        get_p_gfx_context_from__game(p_game)
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_compose_world;

    if (!f_SDL_compose_world) {
        debug_error("SDL::PLATFORM_compose_world, f_SDL_compose_world == 0.");
        return;
    }

    f_SDL_compose_world(
            p_game,
            p_graphics_window);
}
