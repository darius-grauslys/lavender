#include <ui/test_suite_ui_ui_text_box.h>

#include <ui/ui_text_box.c>

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.1 Initialization
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *test_str = "hello";
    Quantity__u32 length = 5;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Text_Box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.1 Initialization
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__pM_c_str__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    char test_str[] = "hello";
    Quantity__u32 length = 5;

    initialize_ui_element_as__text_box_with__pM_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Text_Box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.1 Initialization
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__buffer_size__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    Quantity__u32 buffer_size = 32;

    initialize_ui_element_as__text_box_with__buffer_size(
            &ui_element,
            &font,
            buffer_size);

    munit_assert_int(ui_element.the_kind_of_ui_element__this_is,
            ==, UI_Element_Kind__Text_Box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.2 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_clicked_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *test_str = "test";
    Quantity__u32 length = 4;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    munit_assert_ptr_not_null((void*)ui_element.m_ui_clicked_handler);
    munit_assert_ptr_equal(
            (void*)ui_element.m_ui_clicked_handler,
            (void*)m_ui_element__clicked_handler__text_box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.2 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_typed_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *test_str = "test";
    Quantity__u32 length = 4;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    munit_assert_ptr_not_null((void*)ui_element.m_ui_typed_handler);
    munit_assert_ptr_equal(
            (void*)ui_element.m_ui_typed_handler,
            (void*)m_ui_element__typed_handler__text_box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.2 Handlers
///
TEST_FUNCTION(initialize_ui_element_as__text_box_with__const_c_str__sets_compose_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *test_str = "test";
    Quantity__u32 length = 4;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    munit_assert_ptr_not_null((void*)ui_element.m_ui_compose_handler);
    munit_assert_ptr_equal(
            (void*)ui_element.m_ui_compose_handler,
            (void*)m_ui_element__compose_handler__text_box);

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.3 Delegate Functions
///
TEST_FUNCTION(get_p_const_c_str_text_of__ui_text_box__returns_set_string) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *test_str = "hello";
    Quantity__u32 length = 5;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            test_str,
            length);

    Quantity__u32 size_of__text = 0;
    const char *result = get_p_const_c_str_text_of__ui_text_box(&ui_element, &size_of__text);

    munit_assert_ptr_not_null(result);
    munit_assert_string_equal(result, "hello");

    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/ui/ui_text_box.h.spec.md
/// Section: 16.3.3 Delegate Functions
///
TEST_FUNCTION(set_c_str_of__ui_text_box_with__const_c_str__updates_string) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));

    Font font;
    memset(&font, 0, sizeof(font));

    const char *initial_str = "hello";
    Quantity__u32 length = 5;

    initialize_ui_element_as__text_box_with__const_c_str(
            &ui_element,
            &font,
            initial_str,
            length);

    const char *new_str = "world";
    Quantity__u32 new_length = 5;

    set_c_str_of__ui_text_box_with__const_c_str(
            0, // TODO: this test must be updated to include a ui_manager.
            &ui_element,
            new_str,
            new_length);

    Quantity__u32 size_of__text = 0;
    const char *result = get_p_const_c_str_text_of__ui_text_box(&ui_element, &size_of__text);

    munit_assert_ptr_not_null(result);
    munit_assert_string_equal(result, "world");

    return MUNIT_OK;
}

DEFINE_SUITE(ui_text_box,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__const_c_str__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__pM_c_str__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__buffer_size__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__const_c_str__sets_clicked_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__const_c_str__sets_typed_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__text_box_with__const_c_str__sets_compose_handler),
    INCLUDE_TEST__STATELESS(get_p_const_c_str_text_of__ui_text_box__returns_set_string),
    INCLUDE_TEST__STATELESS(set_c_str_of__ui_text_box_with__const_c_str__updates_string),
    END_TESTS)
