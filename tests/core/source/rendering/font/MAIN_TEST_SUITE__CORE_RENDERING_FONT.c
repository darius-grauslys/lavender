#include <rendering/font/MAIN_TEST_SUITE__CORE_RENDERING_FONT.h>

INCLUDE_SUB_SUITES(CORE_RENDERING_FONT, 4,
INCLUDE_SUITE(font),
INCLUDE_SUITE(font_manager),
INCLUDE_SUITE(typer),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_RENDERING_FONT, END_TESTS);

