#include <MAIN_TEST_SUITE__CORE_LAVENDER.h>

int main(int argc, char* argv[MUNIT_ARRAY_PARAM(argc + 1)]) {
    MunitSuite test_suite;

    include_test_suite__CORE_LAVENDER(&test_suite);

    return munit_suite_main(&test_suite, (void*) "µnit", argc, argv);
}
