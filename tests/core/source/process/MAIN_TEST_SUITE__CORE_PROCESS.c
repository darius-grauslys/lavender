#include <process/MAIN_TEST_SUITE__CORE_PROCESS.h>

INCLUDE_SUB_SUITES(CORE_PROCESS, 8,
INCLUDE_SUITE(process_manager),
INCLUDE_SUITE(process_table),
INCLUDE_SUITE(tcp_game_action_process),
INCLUDE_SUITE(filesystem_process),
INCLUDE_SUITE(process_priority_table_entry),
INCLUDE_SUITE(process),
INCLUDE_SUITE(game_action_process),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_PROCESS, END_TESTS);

