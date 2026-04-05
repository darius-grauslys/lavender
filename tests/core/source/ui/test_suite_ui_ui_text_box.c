#include <ui/test_suite_ui_ui_text_box.h>

#include <ui/ui_text_box.c>

TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            0,
            "hello",
            5);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Text_Box);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_buffer) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    const char *text = "test";
    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            0,
            text,
            4);
    munit_assert_ptr_equal(ui_element.pM_char_buffer, (char*)text);
    munit_assert_uint32(ui_element.size_of__char_buffer, ==, 4);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__text_box__sets_clicked_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            0,
            "test",
            4