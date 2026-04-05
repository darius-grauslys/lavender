#include <inventory/test_suite_inventory_inventory_manager.h>

#include <inventory/inventory_manager.c>

TEST_FUNCTION(inventory_manager__initialize__no_inventories_allocated) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv =
        get_inventory_by__uuid_in__inventory_manager(&manager, 42);
    munit_assert_ptr_null(p_inv);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__allocate__returns_non_null) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 100);
    munit_assert_ptr_not_null(p_inv);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__allocate__can_retrieve_by_uuid) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 100);
    munit_assert_ptr_not_null(p_inv);
    Inventory *p_found =
        get_inventory_by__uuid_in__inventory_manager(&manager, 100);
    munit_assert_ptr_not_null(p_found);
    munit_assert_ptr_equal(p_inv, p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__release__cannot_retrieve_after) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 200);
    munit_assert_ptr_not_null(p_inv);
    release_inventory_in__inventory_manager(&manager, p_inv);
    Inventory *p_found =
        get_inventory_by__uuid_in__inventory_manager(&manager, 200);
    munit_assert_ptr_null(p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__allocate_multiple__different_uuids) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv_a =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 10);
    Inventory *p_inv_b =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 20);
    munit_assert_ptr_not_null(p_inv_a);
    munit_assert_ptr_not_null(p_inv_b);
    munit_assert_ptr_not_equal(p_inv_a, p_inv_b);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__allocate_multiple__each_retrievable) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    allocate_p_inventory_using__this_uuid_in__inventory_manager(
        &manager, 10);
    allocate_p_inventory_using__this_uuid_in__inventory_manager(
        &manager, 20);
    Inventory *p_found_a =
        get_inventory_by__uuid_in__inventory_manager(&manager, 10);
    Inventory *p_found_b =
        get_inventory_by__uuid_in__inventory_manager(&manager, 20);
    munit_assert_ptr_not_null(p_found_a);
    munit_assert_ptr_not_null(p_found_b);
    munit_assert_ptr_not_equal(p_found_a, p_found_b);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__get_nonexistent_uuid__returns_null) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    allocate_p_inventory_using__this_uuid_in__inventory_manager(
        &manager, 10);
    Inventory *p_found =
        get_inventory_by__uuid_in__inventory_manager(&manager, 999);
    munit_assert_ptr_null(p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory_manager__release_and_reallocate__works) {
    Inventory_Manager manager;
    initialize_inventory_manager(&manager);
    Inventory *p_inv =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 50);
    munit_assert_ptr_not_null(p_inv);
    release_inventory_in__inventory_manager(&manager, p_inv);
    Inventory *p_inv_new =
        allocate_p_inventory_using__this_uuid_in__inventory_manager(
            &manager, 60);
    munit_assert_ptr_not_null(p_inv_new);
    Inventory *p_found =
        get_inventory_by__uuid_in__inventory_manager(&manager, 60);
    munit_assert_ptr_not_null(p_found);
    munit_assert_ptr_equal(p_inv_new, p_found);
    return MUNIT_OK;
}

DEFINE_SUITE(inventory_manager,
    INCLUDE_TEST__STATELESS(inventory_manager__initialize__no_inventories_allocated),
    INCLUDE_TEST__STATELESS(inventory_manager__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(inventory_manager__allocate__can_retrieve_by_uuid),
    INCLUDE_TEST__STATELESS(inventory_manager__release__cannot_retrieve_after),
    INCLUDE_TEST__STATELESS(inventory_manager__allocate_multiple__different_uuids),
    INCLUDE_TEST__STATELESS(inventory_manager__allocate_multiple__each_retrievable),
    INCLUDE_TEST__STATELESS(inventory_manager__get_nonexistent_uuid__returns_null),
    INCLUDE_TEST__STATELESS(inventory_manager__release_and_reallocate__works),
    END_TESTS)
