#include <ui/test_suite_ui_ui_drop_zone.h>

#include <ui/ui_drop_zone.c>

static void mock_receive_drop_handler(
        UI_Element *p_this,
        UI_Element *p_dropped,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    (void)p_this;
    (void)p_dropped;
    (void)p_game;
    (void)p_gfx_window;
}

TEST_FUNCTION(initialize_ui_element_as__drop_zone__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__drop_zone(
            &ui_element,
            mock_receive_drop_handler);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Drop_Zone);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__drop_zone__sets_receive_drop_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__drop_zone(
            &ui_element,
            mock_receive_drop_handler);
    munit_assert_true(
            does_ui_element_have__receive_drop_handler(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__drop_zone__null_handler_uses_default) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__drop_zone(&ui_element, 0);
    munit_assert_true(
            does_ui_element_have__receive_drop_handler(&ui_element));
    return MUNIT_OK;
}

DEFINE_SUITE(ui_drop_zone,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__drop_zone__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__drop_zone__sets_receive_drop_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__drop_zone__null_handler_uses_default),
    END_TESTS)
