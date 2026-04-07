#include <ui/test_suite_ui_ui_draggable.h>

#include <ui/ui_draggable.c>

///
/// Spec:   docs/specs/core/ui/ui_draggable.h.spec.md
/// Section: 13.3 Functions — initialize_ui_element_as__draggable
///
/// Verifies that initialize_ui_element_as__draggable sets the element
/// kind to UI_Element_Kind__Draggable.
///
TEST_FUNCTION(initialize_ui_element_as__draggable__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__draggable(&ui_element, 0);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Draggable);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_draggable.h.spec.md
/// Section: 13.3 Functions — initialize_ui_element_as__draggable
///
/// Verifies that initialize_ui_element_as__draggable sets the dragged
/// handler (using the default when null is passed).
///
TEST_FUNCTION(initialize_ui_element_as__draggable__sets_dragged_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__draggable(&ui_element, 0);
    munit_assert_true(does_ui_element_have__dragged_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_draggable.h.spec.md
/// Section: 13.3 Functions — initialize_ui_element_as__draggable
///
/// Verifies that initialize_ui_element_as__draggable sets the dropped
/// handler to the default dropped handler.
///
TEST_FUNCTION(initialize_ui_element_as__draggable__sets_dropped_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__draggable(&ui_element, 0);
    munit_assert_true(does_ui_element_have__dropped_handler(&ui_element));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_draggable.h.spec.md
/// Section: 13.3 Functions — initialize_ui_element_as__draggable
///
/// Verifies that initialize_ui_element_as__draggable accepts a custom
/// (non-null) drag handler and sets it on the element.
///
TEST_FUNCTION(initialize_ui_element_as__draggable__custom_drag_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    initialize_ui_element_as__draggable(
            &ui_element,
            m_ui_draggable__dragged_handler__default);
    munit_assert_true(does_ui_element_have__dragged_handler(&ui_element));
    return MUNIT_OK;
}

DEFINE_SUITE(ui_draggable,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__draggable__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__draggable__sets_dragged_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__draggable__sets_dropped_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__draggable__custom_drag_handler),
    END_TESTS)
