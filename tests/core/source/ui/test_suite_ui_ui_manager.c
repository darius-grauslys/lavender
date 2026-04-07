#include <ui/test_suite_ui_ui_manager.h>

#include <ui/ui_manager.c>

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.1 Initialization and Memory — initialize_ui_manager
///
TEST_FUNCTION(initialize_ui_manager__sets_empty_state) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    munit_assert_ptr_null(ui_manager.pM_ui_element_pool);
    munit_assert_ptr_null(ui_manager.pM_ptr_array_of__ui_elements);
    munit_assert_ptr_null(ui_manager.p_ui_element__focused);
    munit_assert_uint16(ui_manager.max_quantity_of__ui_elements, ==, 0);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.1 Initialization and Memory — allocate_ui_manager__members
///
TEST_FUNCTION(allocate_ui_manager__members__succeeds) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    bool result = allocate_ui_manager__members(&ui_manager, 4);
    munit_assert_true(result);
    munit_assert_not_null(ui_manager.pM_ui_element_pool);
    munit_assert_not_null(ui_manager.pM_ptr_array_of__ui_elements);
    munit_assert_uint16(ui_manager.max_quantity_of__ui_elements, ==, 4);
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.1 Initialization and Memory — release_ui_manager__members
///
TEST_FUNCTION(release_ui_manager__members__cleans_up) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 4);
    release_ui_manager__members(&ui_manager);
    munit_assert_ptr_null(ui_manager.pM_ui_element_pool);
    munit_assert_ptr_null(ui_manager.pM_ptr_array_of__ui_elements);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.5 Allocation — allocate_ui_element_from__ui_manager
///
TEST_FUNCTION(allocate_ui_element_from__ui_manager__returns_non_null) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 4);
    UI_Element *p_element =
        allocate_ui_element_from__ui_manager(&ui_manager);
    munit_assert_not_null(p_element);
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.5 Allocation — allocate_ui_element_from__ui_manager
///
TEST_FUNCTION(allocate_ui_element__exhaust_pool__returns_null) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 2);
    UI_Element *p_e1 =
        allocate_ui_element_from__ui_manager(&ui_manager);
    UI_Element *p_e2 =
        allocate_ui_element_from__ui_manager(&ui_manager);
    UI_Element *p_e3 =
        allocate_ui_element_from__ui_manager(&ui_manager);
    munit_assert_not_null(p_e1);
    munit_assert_not_null(p_e2);
    munit_assert_ptr_null(p_e3);
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.8 Inline Functions — is_ui_manager__empty
///
TEST_FUNCTION(is_ui_manager__empty__true_when_no_elements) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 4);
    munit_assert_true(is_ui_manager__empty(&ui_manager));
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.8 Inline Functions — is_ui_manager__empty
///
TEST_FUNCTION(is_ui_manager__empty__false_after_allocation) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 4);
    allocate_ui_element_from__ui_manager(&ui_manager);
    munit_assert_false(is_ui_manager__empty(&ui_manager));
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.8 Inline Functions — is_ui_manager__dirty
///
TEST_FUNCTION(is_ui_manager__dirty__initially_not_dirty) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    munit_assert_false(is_ui_manager__dirty(&ui_manager));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.8 Inline Functions — set_ui_manager_as__dirty
///
TEST_FUNCTION(set_ui_manager_as__dirty__sets_flag) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    set_ui_manager_as__dirty(&ui_manager);
    munit_assert_true(is_ui_manager__dirty(&ui_manager));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.8 Inline Functions — set_ui_manager_as__NOT_dirty
///
TEST_FUNCTION(set_ui_manager_as__NOT_dirty__clears_flag) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    set_ui_manager_as__dirty(&ui_manager);
    set_ui_manager_as__NOT_dirty(&ui_manager);
    munit_assert_false(is_ui_manager__dirty(&ui_manager));
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.5 Allocation — allocate_many_ui_elements_from__ui_manager_in__succession
///
TEST_FUNCTION(allocate_many_ui_elements_in__succession__links_elements) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 8);
    UI_Element *p_head =
        allocate_many_ui_elements_from__ui_manager_in__succession(
                &ui_manager, 3);
    munit_assert_not_null(p_head);
    munit_assert_true(does_ui_element_have__next(p_head));
    UI_Element *p_second = get_next__ui_element(p_head);
    munit_assert_not_null(p_second);
    munit_assert_true(does_ui_element_have__next(p_second));
    UI_Element *p_third = get_next__ui_element(p_second);
    munit_assert_not_null(p_third);
    munit_assert_false(does_ui_element_have__next(p_third));
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

///
/// Spec:   docs/specs/core/ui/ui_manager.h.spec.md
/// Section: 6.4.2 Queries — get_quantity_of__ui_elements_in__ui_manager
///
TEST_FUNCTION(get_quantity_of__ui_elements_in__ui_manager__returns_correct_count) {
    UI_Manager ui_manager;
    initialize_ui_manager(&ui_manager);
    allocate_ui_manager__members(&ui_manager, 8);
    munit_assert_uint16(
            get_quantity_of__ui_elements_in__ui_manager(&ui_manager),
            ==, 0);
    allocate_ui_element_from__ui_manager(&ui_manager);
    munit_assert_uint16(
            get_quantity_of__ui_elements_in__ui_manager(&ui_manager),
            ==, 1);
    allocate_ui_element_from__ui_manager(&ui_manager);
    munit_assert_uint16(
            get_quantity_of__ui_elements_in__ui_manager(&ui_manager),
            ==, 2);
    release_ui_manager__members(&ui_manager);
    return MUNIT_OK;
}

DEFINE_SUITE(ui_manager,
    INCLUDE_TEST__STATELESS(initialize_ui_manager__sets_empty_state),
    INCLUDE_TEST__STATELESS(allocate_ui_manager__members__succeeds),
    INCLUDE_TEST__STATELESS(release_ui_manager__members__cleans_up),
    INCLUDE_TEST__STATELESS(allocate_ui_element_from__ui_manager__returns_non_null),
    INCLUDE_TEST__STATELESS(allocate_ui_element__exhaust_pool__returns_null),
    INCLUDE_TEST__STATELESS(is_ui_manager__empty__true_when_no_elements),
    INCLUDE_TEST__STATELESS(is_ui_manager__empty__false_after_allocation),
    INCLUDE_TEST__STATELESS(is_ui_manager__dirty__initially_not_dirty),
    INCLUDE_TEST__STATELESS(set_ui_manager_as__dirty__sets_flag),
    INCLUDE_TEST__STATELESS(set_ui_manager_as__NOT_dirty__clears_flag),
    INCLUDE_TEST__STATELESS(allocate_many_ui_elements_in__succession__links_elements),
    INCLUDE_TEST__STATELESS(get_quantity_of__ui_elements_in__ui_manager__returns_correct_count),
    END_TESTS)
