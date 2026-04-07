#include <ui/test_suite_ui_ui_window.h>

#include <ui/ui_window.c>

// Before writing any tests, please see the README
// found in ./tests

///
/// Specification: docs/specs/core/ui/ui_window.h.spec.md
/// Section: 18.3 Functions
///
/// Tests that f_ui_window__close__default releases all UI elements
/// from the manager and returns successfully.
///
void test_f_ui_window__close__default__releases_ui_elements(
        Test_Flags *p_test_flags) {
    // TODO: implement test
}

///
/// Specification: docs/specs/core/ui/ui_window.h.spec.md
/// Section: 18.4.1 Usage Pattern
///
/// Tests that f_ui_window__close__default conforms to the
/// f_UI_Window__Close callback signature and can be used
/// as the default close handler in UI_Window_Record.
///
void test_f_ui_window__close__default__matches_close_signature(
        Test_Flags *p_test_flags) {
    // TODO: implement test
}

///
/// Specification: docs/specs/core/ui/ui_window.h.spec.md
/// Section: 18.4.2 Preconditions
///
/// Tests that f_ui_window__close__default handles the case
/// where all parameters are non-null as required.
///
void test_f_ui_window__close__default__preconditions_non_null(
        Test_Flags *p_test_flags) {
    // TODO: implement test
}

DEFINE_SUITE(ui_window,
    INCLUDE_TEST(test_f_ui_window__close__default__releases_ui_elements),
    INCLUDE_TEST(test_f_ui_window__close__default__matches_close_signature),
    INCLUDE_TEST(test_f_ui_window__close__default__preconditions_non_null),
    END_TESTS)
