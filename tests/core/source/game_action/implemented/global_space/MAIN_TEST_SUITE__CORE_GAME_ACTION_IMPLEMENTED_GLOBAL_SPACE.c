#include <game_action/implemented/global_space/MAIN_TEST_SUITE__CORE_GAME_ACTION_IMPLEMENTED_GLOBAL_SPACE.h>

INCLUDE_SUB_SUITES(CORE_GAME_ACTION_IMPLEMENTED_GLOBAL_SPACE, 5,
INCLUDE_SUITE(game_action__global_space__request__offline),
INCLUDE_SUITE(game_action__global_space__request__multiplayer),
INCLUDE_SUITE(game_action__global_space__resolve),
INCLUDE_SUITE(game_action__global_space__store),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_GAME_ACTION_IMPLEMENTED_GLOBAL_SPACE, END_TESTS);

