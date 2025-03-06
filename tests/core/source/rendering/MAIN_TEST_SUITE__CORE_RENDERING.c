#include <rendering/MAIN_TEST_SUITE__CORE_RENDERING.h>

INCLUDE_SUB_SUITES(CORE_RENDERING, 11,
INCLUDE_SUITE(animate_sprite),
INCLUDE_SUITE(graphics_window),
INCLUDE_SUITE(sprite_gfx_allocator_manager),
INCLUDE_SUITE(sprite),
INCLUDE_SUITE(aliased_texture),
INCLUDE_SUITE(aliased_texture_manager),
INCLUDE_SUITE(texture_strings),
INCLUDE_SUITE(texture),
INCLUDE_SUITE(graphics_window_manager),
INCLUDE_SUITE(CORE_RENDERING_FONT),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_RENDERING, END_TESTS);

