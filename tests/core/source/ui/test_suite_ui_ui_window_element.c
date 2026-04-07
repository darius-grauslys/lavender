#include <ui/test_suite_ui_ui_window_element.h>

#include <ui/ui_window_element.c>

///
/// Specification:  docs/specs/core/ui/ui_window_element.h.spec.md
/// Section:        20.4 Functions
///
/// Tests that initialize_ui_element_as__window_element_and__open_window
/// sets the_kind_of_ui_element__this_is to UI_Element_Kind__Window.
///
TEST_FUNCTION(initialize_ui_element_as__window_element__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Game game;
    memset(&game, 0, sizeof(game));

    initialize_ui_element_as__window_element_and__open_window(
            &ui_element,
            &game,
            Graphics_Window_Kind__None,
            IDENTIFIER__UNKNOWN__u32,
            (Vector__3i32){0, 0, 0});

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Window);

    return MUNIT_OK;
}

///
/// Specification:  docs/specs/core/ui/ui_window_element.h.spec.md
/// Section:        20.4 Functions
///
/// Tests that initialize_ui_element_as__window_element_and__open_window
/// accepts a Vector__3i32 origin parameter and correctly initializes
/// the element as a window element.
///
TEST_FUNCTION(initialize_ui_element_as__window_element__with_origin) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Game game;
    memset(&game, 0, sizeof(game));

    Vector__3i32 origin = {10, 20, 0};

    initialize_ui_element_as__window_element_and__open_window(
            &ui_element,
            &game,
            Graphics_Window_Kind__None,
            IDENTIFIER__UNKNOWN__u32,
            origin);

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Window);

    return MUNIT_OK;
}

///
/// Specification:  docs/specs/core/ui/ui_window_element.h.spec.md
/// Section:        20.3.1 Window-Specific Data
///
/// Tests that initialize_ui_element_as__window_element_and__open_window
/// properly associates a Graphics_Window pointer
/// (p_ui_window__graphics_window) with the UI element.
///
TEST_FUNCTION(initialize_ui_element_as__window_element__graphics_window_pointer) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Game game;
    memset(&game, 0, sizeof(game));

    initialize_ui_element_as__window_element_and__open_window(
            &ui_element,
            &game,
            Graphics_Window_Kind__None,
            IDENTIFIER__UNKNOWN__u32,
            (Vector__3i32){0, 0, 0});

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Window);

    return MUNIT_OK;
}

DEFINE_SUITE(ui_window_element,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__window_element__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__window_element__with_origin),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__window_element__graphics_window_pointer),
    END_TESTS)
