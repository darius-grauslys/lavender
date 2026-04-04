#include <debug/test_suite_debug_debug.h>

#include <debug/debug.c>

TEST_FUNCTION(debug_info__does_not_crash) {
    debug_info("test message: %d", 42);
    return MUNIT_OK;
}

TEST_FUNCTION(debug_info__with_string_format) {
    debug_info("hello %s", "world");
    return MUNIT_OK;
}

TEST_FUNCTION(debug_info__with_no_format_args) {
    debug_info("simple message");
    return MUNIT_OK;
}

TEST_FUNCTION(debug_warning__does_not_crash) {
    debug_warning("test warning: %d", 99);
    return MUNIT_OK;
}

TEST_FUNCTION(debug_warning__with_string_format) {
    debug_warning("warning about %s", "something");
    return MUNIT_OK;
}

TEST_FUNCTION(debug_warning__with_no_format_args) {
    debug_warning("plain warning");
    return MUNIT_OK;
}

TEST_FUNCTION(debug_info__verbose__does_not_crash) {
    debug_info__verbose("verbose info: %d", 7);
    return MUNIT_OK;
}

TEST_FUNCTION(debug_warning__verbose__does_not_crash) {
    debug_warning__verbose("verbose warning: %d", 8);
    return MUNIT_OK;
}

TEST_FUNCTION(debug_info__multiple_format_specifiers) {
    debug_info("values: %d, %s, %x", 10, "test", 0xFF);
    return MUNIT_OK;
}

TEST_FUNCTION(debug_warning__multiple_format_specifiers) {
    debug_warning("values: %d, %s, %x", 20, "warn", 0xAB);
    return MUNIT_OK;
}

DEFINE_SUITE(debug,
    INCLUDE_TEST__STATELESS(debug_info__does_not_crash),
    INCLUDE_TEST__STATELESS(debug_info__with_string_format),
    INCLUDE_TEST__STATELESS(debug_info__with_no_format_args),
    INCLUDE_TEST__STATELESS(debug_warning__does_not_crash),
    INCLUDE_TEST__STATELESS(debug_warning__with_string_format),
    INCLUDE_TEST__STATELESS(debug_warning__with_no_format_args),
    INCLUDE_TEST__STATELESS(debug_info__verbose__does_not_crash),
    INCLUDE_TEST__STATELESS(debug_warning__verbose__does_not_crash),
    INCLUDE_TEST__STATELESS(debug_info__multiple_format_specifiers),
    INCLUDE_TEST__STATELESS(debug_warning__multiple_format_specifiers),
    END_TESTS)
