#include <MAIN_TEST_SUITE__SDL_ANCIENTS_GAME.h>

INCLUDE_SUB_SUITES(SDL_ANCIENTS_GAME, 13,
INCLUDE_SUITE(sdl_main),
INCLUDE_SUITE(sdl_event),
INCLUDE_SUITE(sdl_game),
INCLUDE_SUITE(TMP),
INCLUDE_SUITE(sdl_numerics),
INCLUDE_SUITE(SDL_INPUT),
INCLUDE_SUITE(SDL_RENDERING),
INCLUDE_SUITE(SDL_DEBUG),
INCLUDE_SUITE(SDL_SERIALIZATION),
INCLUDE_SUITE(SDL_UI),
INCLUDE_SUITE(SDL_TIME),
INCLUDE_SUITE(SDL_MULTIPLAYER),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(SDL_ANCIENTS_GAME, END_TESTS);

