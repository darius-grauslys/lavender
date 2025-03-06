#include <rendering/MAIN_TEST_SUITE__SDL_RENDERING.h>

INCLUDE_SUB_SUITES(SDL_RENDERING, 10,
INCLUDE_SUITE(sdl_render_world),
INCLUDE_SUITE(sdl_gfx_window_manager),
INCLUDE_SUITE(sdl_texture_manager),
INCLUDE_SUITE(sdl_sprite),
INCLUDE_SUITE(sdl_gfx_context),
INCLUDE_SUITE(sdl_gfx_window),
INCLUDE_SUITE(sdl_texture),
INCLUDE_SUITE(sdl_sprite_manager),
INCLUDE_SUITE(SDL_RENDERING_OPENGL),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(SDL_RENDERING, END_TESTS);

