#include <inventory/test_suite_inventory_item_stack_manager.h>

#include <inventory/item_stack_manager.c>

TEST_FUNCTION(item_stack_manager__initialize__all_slots_deallocated) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    for (Index__u32 i = 0; i < ITEM_STACK_RECORD_MAX_QUANTITY_OF; i++) {
        Item_Stack_Allocation_Specifier *p_spec =
            get_p_item_stack_alloc_spec_by__index_from__item_stack_manager(
                &manager, i);
        munit_assert_false(
            is_item_stack_allocation_specifier__allocated(p_spec));
    }
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__initialize__count_is_zero) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    munit_assert_uint32(manager.quantity_of__item_stack_allocation_specifier, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__allocate__returns_non_null) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    Item_Stack_Allocation_Specifier *p_spec =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &manager, Item_Kind__Unknown);
    munit_assert_ptr_not_null(p_spec);
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__allocate__specifier_is_allocated) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    Item_Stack_Allocation_Specifier *p_spec =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &manager, Item_Kind__Unknown);
    munit_assert_ptr_not_null(p_spec);
    munit_assert_true(
        is_item_stack_allocation_specifier__allocated(p_spec));
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__release__specifier_is_deallocated) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    Item_Stack_Allocation_Specifier *p_spec =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &manager, Item_Kind__Unknown);
    munit_assert_ptr_not_null(p_spec);
    release_item_stack_allocation_specification_in__item_stack_manager(
        &manager, p_spec);
    munit_assert_false(
        is_item_stack_allocation_specifier__allocated(p_spec));
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__get_by_index__returns_valid_specifier) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    Item_Stack_Allocation_Specifier *p_spec =
        get_p_item_stack_alloc_spec_by__index_from__item_stack_manager(
            &manager, 0);
    munit_assert_ptr_not_null(p_spec);
    return MUNIT_OK;
}

TEST_FUNCTION(item_stack_manager__allocate_multiple__all_non_null) {
    Item_Stack_Manager manager;
    initialize_item_stack_manager(&manager);
    Item_Stack_Allocation_Specifier *p_spec_a =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &manager, Item_Kind__None);
    Item_Stack_Allocation_Specifier *p_spec_b =
        allocate_item_stack_allocation_specification_in__item_stack_manager(
            &manager, Item_Kind__Unknown);
    munit_assert_ptr_not_null(p_spec_a);
    munit_assert_ptr_not_null(p_spec_b);
    munit_assert_ptr_not_equal(p_spec_a, p_spec_b);
    return MUNIT_OK;
}

DEFINE_SUITE(item_stack_manager,
    INCLUDE_TEST__STATELESS(item_stack_manager__initialize__all_slots_deallocated),
    INCLUDE_TEST__STATELESS(item_stack_manager__initialize__count_is_zero),
    INCLUDE_TEST__STATELESS(item_stack_manager__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(item_stack_manager__allocate__specifier_is_allocated),
    INCLUDE_TEST__STATELESS(item_stack_manager__release__specifier_is_deallocated),
    INCLUDE_TEST__STATELESS(item_stack_manager__get_by_index__returns_valid_specifier),
    INCLUDE_TEST__STATELESS(item_stack_manager__allocate_multiple__all_non_null),
    END_TESTS)
