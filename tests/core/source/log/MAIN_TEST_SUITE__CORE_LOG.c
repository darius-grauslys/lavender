#include <log/MAIN_TEST_SUITE__CORE_LOG.h>

INCLUDE_SUB_SUITES(CORE_LOG, 3,
INCLUDE_SUITE(log),
INCLUDE_SUITE(message),NULL);

DEFINE_SUITE_WITH__SUB_SUITES(CORE_LOG, END_TESTS);

