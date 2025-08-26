#include <game_action/core/tcp/MAIN_TEST_SUITE__CORE_GAME_ACTION_CORE_TCP.h>

INCLUDE_SUB_SUITES(CORE_GAME_ACTION_CORE_TCP, 6,
INCLUDE_SUITE(game_action__tcp_connect),
INCLUDE_SUITE(game_action__tcp_connect__accept),
INCLUDE_SUITE(game_action__tcp_delivery),
INCLUDE_SUITE(game_action__tcp_begin_connect),
INCLUDE_SUITE(game_action__tcp_connect__reject),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_GAME_ACTION_CORE_TCP, END_TESTS);

