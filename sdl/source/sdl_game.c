#include "rendering/sdl_gfx_context.h"
#include "sdl_event.h"
#include "serialization/sdl_filesystem.h"
#include <SDL2/SDL_events.h>
#include <SDL2/SDL_render.h>
#include <platform.h>
#include <game.h>
#include <sdl_defines.h>

#include "debug/opengl/gl_debug.h"
#include "input/sdl_input.h"
#include "platform_defines.h"
#include "rendering/sdl_gfx_context.h"
#include "scene/scene_manager.h"
#include "sdl_event.h"
#include "serialization/sdl_filesystem.h"
#include <SDL2/SDL_events.h>
#include <platform.h>
#include <SDL2/SDL.h>
#include <game.h>
#include <sdl_defines.h>
#include <rendering/opengl/glad/glad.h>
#include <time/sdl_time.h>

void PLATFORM_initialize_game(Game *p_game) {
    SDL_initialize_time();

    SDL_Init(
            SDL_INIT_TIMER
            | SDL_INIT_VIDEO
            | SDL_INIT_AUDIO
            | SDL_INIT_EVENTS);

    p_game->gfx_context.p_PLATFORM_gfx_context =
        &__SDL_Gfx_Context;
    p_game->p_PLATFORM_file_system_context =
        &__SDL_file_system_context;
    SDL_initialize_events();
    SDL_initialize_gfx_context(
            p_game,
            SDL_Gfx_Sub_Context__OpenGL_3_0);
    SDL_initialize_input_bindings();

    PLATFORM_initialize_file_system_context(
            p_game,
            p_game->p_PLATFORM_file_system_context);
}

void PLATFORM_close_game(Game *p_game) {
    SDL_dispose_gfx_context(
            get_p_PLATFORM_gfx_context_from__game(p_game));
    SDL_Quit();
}

void PLATFORM_pre_render(Game *p_game) {
    SDL_PumpEvents();
    SDL_poll_event(p_game);
    SDL_clear_screen(
            get_p_PLATFORM_gfx_context_from__game(p_game));
}

void PLATFORM_post_render(Game *p_game) {
    SDL_GL_SwapWindow(
            get_p_PLATFORM_gfx_context_from__game(
                p_game)
            ->p_SDL_window);
}
