#include <rendering/opengl/MAIN_TEST_SUITE__SDL_RENDERING_OPENGL.h>

INCLUDE_SUB_SUITES(SDL_RENDERING_OPENGL, 19,
INCLUDE_SUITE(gl_render_world),
INCLUDE_SUITE(gl_typer),
INCLUDE_SUITE(gl_shader_graphics_window),
INCLUDE_SUITE(gl_vertex_object),
INCLUDE_SUITE(gl_gfx_sub_context),
INCLUDE_SUITE(gl_texture),
INCLUDE_SUITE(gl_shader_passthrough),
INCLUDE_SUITE(gl_shader_sprite),
INCLUDE_SUITE(gl_framebuffer),
INCLUDE_SUITE(gl_sprite),
INCLUDE_SUITE(gl_framebuffer_manager),
INCLUDE_SUITE(gl_gfx_window),
INCLUDE_SUITE(gl_viewport),
INCLUDE_SUITE(gl_shader_chunk),
INCLUDE_SUITE(gl_shader_manager),
INCLUDE_SUITE(gl_shader),
INCLUDE_SUITE(gl_sprite_manager),
INCLUDE_SUITE(SDL_RENDERING_OPENGL_GLAD),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(SDL_RENDERING_OPENGL, END_TESTS);

