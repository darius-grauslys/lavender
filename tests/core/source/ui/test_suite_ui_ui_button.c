#include <ui/test_suite_ui_ui_button.h>

#include <ui/ui_button.c>

static void mock_click_handler(
        UI_Element *p_this,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    (void)p_this;
    (void)p_game;
    (void)p_gfx_window;
}

TEST_FUNCTION(initialize_ui_element_as__button__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            false,
            false);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Button);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__button__toggleable_and_toggled) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            true);
    munit_assert_true(is_ui_button__toggleable(&ui_element));
    munit_assert_true(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__button__not_toggleable) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            false,
            false);
    munit_assert_false(is_ui_button__toggleable(&ui_element));
    munit_assert_false(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggleable__sets_flag) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            false,
            false);
    set_ui_button_as__toggleable(&ui_element);
    munit_assert_true(is_ui_button__toggleable(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggled__sets_flag) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            false);
    munit_assert_false(is_ui_button__toggled(&ui_element));
    set_ui_button_as__toggled(&ui_element);
    munit_assert_true(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__untoggled__clears_flag) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            true);
    munit_assert_true(is_ui_button__toggled(&ui_element));
    set_ui_button_as__untoggled(&ui_element);
    munit_assert_false(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__non_toggleable__clears_both_flags) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            true);
    set_ui_button_as__non_toggleable(&ui_element);
    munit_assert_false(is_ui_button__toggleable(&ui_element));
    munit_assert_false(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(toggle_ui_button__flips_state) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            false);
    munit_assert_false(is_ui_button__toggled(&ui_element));
    bool result = toggle_ui_button(&ui_element);
    munit_assert_true(result);
    munit_assert_true(is_ui_button__toggled(&ui_element));
    result = toggle_ui_button(&ui_element);
    munit_assert_false(result);
    munit_assert_false(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggled_or__not_toggled__true) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            false);
    set_ui_button_as__toggled_or__not_toggled(&ui_element, true);
    munit_assert_true(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggled_or__not_toggled__false) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            true);
    set_ui_button_as__toggled_or__not_toggled(&ui_element, false);
    munit_assert_false(is_ui_button__toggled(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggleable_or__non_toggleable__true) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            false,
            false);
    set_ui_button_as__toggleable_or__non_toggleable(&ui_element, true);
    munit_assert_true(is_ui_button__toggleable(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_button_as__toggleable_or__non_toggleable__false) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__button(
            &ui_element,
            mock_click_handler,
            true,
            true);
    set_ui_button_as__toggleable_or__non_toggleable(&ui_element, false);
    munit_assert_false(is_ui_button__toggleable(&ui_element));
    return MUNIT_OK;
}

DEFINE_SUITE(ui_button,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__button__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__button__toggleable_and_toggled),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__button__not_toggleable),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggleable__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggled__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_button_as__untoggled__clears_flag),
    INCLUDE_TEST__STATELESS(set_ui_button_as__non_toggleable__clears_both_flags),
    INCLUDE_TEST__STATELESS(toggle_ui_button__flips_state),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggled_or__not_toggled__true),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggled_or__not_toggled__false),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggleable_or__non_toggleable__true),
    INCLUDE_TEST__STATELESS(set_ui_button_as__toggleable_or__non_toggleable__false),
    END_TESTS)
