#include <debug/test_suite_debug_debug.h>

#include <debug/debug.c>

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_info does not crash when called
 * with a format string and integer argument.
 */
TEST_FUNCTION(debug_info__does_not_crash) {
    debug_info("test message: %d", 42);
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_info does not crash when called
 * with a string format specifier.
 */
TEST_FUNCTION(debug_info__with_string_format) {
    debug_info("hello %s", "world");
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_info does not crash when called
 * with no format arguments.
 */
TEST_FUNCTION(debug_info__with_no_format_args) {
    debug_info("simple message");
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_warning does not crash when called
 * with a format string and integer argument.
 */
TEST_FUNCTION(debug_warning__does_not_crash) {
    debug_warning("test warning: %d", 99);
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_warning does not crash when called
 * with a string format specifier.
 */
TEST_FUNCTION(debug_warning__with_string_format) {
    debug_warning("warning about %s", "something");
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_warning does not crash when called
 * with no format arguments.
 */
TEST_FUNCTION(debug_warning__with_no_format_args) {
    debug_warning("plain warning");
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.1 Verbose Logging
 *
 * Verifies that debug_info__verbose does not crash when called
 * with a format string and integer argument.
 */
TEST_FUNCTION(debug_info__verbose__does_not_crash) {
    debug_info__verbose("verbose info: %d", 7);
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.1 Verbose Logging
 *
 * Verifies that debug_warning__verbose does not crash when called
 * with a format string and integer argument.
 */
TEST_FUNCTION(debug_warning__verbose__does_not_crash) {
    debug_warning__verbose("verbose warning: %d", 8);
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_info does not crash when called
 * with multiple mixed format specifiers.
 */
TEST_FUNCTION(debug_info__multiple_format_specifiers) {
    debug_info("values: %d, %s, %x", 10, "test", 0xFF);
    return MUNIT_OK;
}

/*
 * Spec: docs/specs/core/debug/debug.h.spec.md
 * Section: 1.5.2 Standard Logging
 *
 * Verifies that debug_warning does not crash when called
 * with multiple mixed format specifiers.
 */
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
