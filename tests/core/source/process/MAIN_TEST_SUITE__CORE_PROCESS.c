#include <process/MAIN_TEST_SUITE__CORE_PROCESS.h>

INCLUDE_SUB_SUITES(CORE_PROCESS, 4,
INCLUDE_SUITE(process_manager),
INCLUDE_SUITE(process),
INCLUDE_SUITE(game_action_process),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_PROCESS, END_TESTS);

