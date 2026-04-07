#include <ui/test_suite_ui_ui_text.h>

#include <ui/ui_text.c>

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.1 Initialization
///
TEST_FUNCTION(initialize_ui_element_as__text_with__const_c_str__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "hello",
            5);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Text);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.1 Initialization
/// @section 10.3.1 Text-Specific Data
///
TEST_FUNCTION(initialize_ui_element_as__text_with__const_c_str__sets_buffer) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    const char *text = "hello";
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            text,
            5);
    munit_assert_ptr_equal(ui_element.pM_char_buffer, (char*)text);
    munit_assert_uint32(ui_element.size_of__char_buffer, ==, 5);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.1 Initialization
/// @section 10.4.3 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text__sets_compose_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "test",
            4);
    munit_assert_true(does_ui_element_have__compose_handler(&ui_element));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.1 Initialization
/// @section 10.4.3 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text__sets_transformed_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "test",
            4);
    munit_assert_true(
            does_ui_element_have__transformed_handler(&ui_element));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.1 Initialization
/// @section 10.4.3 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text__sets_dispose_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "test",
            4);
    munit_assert_true(does_ui_element_have__dispose_handler(&ui_element));
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.4 Accessors
///
TEST_FUNCTION(get_p_const_c_str_text_of__ui_text__returns_text_and_size) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    const char *text = "hello world";
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            text,
            11);
    Quantity__u32 size = 0;
    const char *result =
        get_p_const_c_str_text_of__ui_text(&ui_element, &size);
    munit_assert_ptr_equal(result, text);
    munit_assert_uint32(size, ==, 11);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.4 Accessors
///
TEST_FUNCTION(get_p_typer_of__ui_text__returns_non_null) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "test",
            4);
    Typer *p_typer = get_p_typer_of__ui_text(&ui_element);
    munit_assert_not_null(p_typer);
    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/ui/ui_text.h.spec.md
/// @section 10.4.2 Text Manipulation
///
TEST_FUNCTION(set_cursor_of__ui_text__sets_cursor_index) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__text_with__const_c_str(
            &ui_element,
            0,
            "hello",
            5);
    set_cursor_of__ui_text(&ui_element, 3);
    munit_assert_uint32(ui_element.index_of__cursor_in__char_buffer, ==, 3);
    return MUNIT_OK;
}

DEFINE_SUITE(ui_text,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_with__const_c_str__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_with__const_c_str__sets_buffer),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text__sets_compose_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text__sets_transformed_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text__sets_dispose_handler),
    INCLUDE_TEST__STATELESS(get_p_const_c_str_text_of__ui_text__returns_text_and_size),
    INCLUDE_TEST__STATELESS(get_p_typer_of__ui_text__returns_non_null),
    INCLUDE_TEST__STATELESS(set_cursor_of__ui_text__sets_cursor_index),
    END_TESTS)
