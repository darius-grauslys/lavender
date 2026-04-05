#include <inventory/test_suite_inventory_item_manager.h>

#include <inventory/item_manager.c>

TEST_FUNCTION(item_manager__initialize__all_templates_empty) {
    Item_Manager manager;
    initialize_item_manager(&manager);
    Item item = get_item_from__item_manager(&manager, Item_Kind__None);
    munit_assert_true(is_p_item__empty(&item));
    return MUNIT_OK;
}

TEST_FUNCTION(item_manager__register_and_get__returns_registered_item) {
    Item_Manager manager;
    initialize_item_manager(&manager);
    Item item;
    initialize_item(&item, Item_Kind__None);
    register_item_in__item_manager(&manager, Item_Kind__None, item);
    Item retrieved = get_item_from__item_manager(&manager, Item_Kind__None);
    munit_assert_int(get_item_kind_of__item(&retrieved), ==, Item_Kind__None);
    return MUNIT_OK;
}

TEST_FUNCTION(item_manager__get_unregistered__returns_empty) {
    Item_Manager manager;
    initialize_item_manager(&manager);
    Item item = get_item_from__item_manager(&manager, Item_Kind__None);
    munit_assert_int(get_item_kind_of__item(&item), ==, Item_Kind__None);
    return MUNIT_OK;
}

TEST_FUNCTION(item_manager__register_overwrites__previous_value) {
    Item_Manager manager;
    initialize_item_manager(&manager);
    Item item_a;
    initialize_item(&item_a, Item_Kind__None);
    register_item_in__item_manager(&manager, Item_Kind__None, item_a);

    Item item_b;
    initialize_item(&item_b, Item_Kind__None);
    register_item_in__item_manager(&manager, Item_Kind__None, item_b);

    Item retrieved = get_item_from__item_manager(&manager, Item_Kind__None);
    munit_assert_int(get_item_kind_of__item(&retrieved), ==, Item_Kind__None);
    return MUNIT_OK;
}

DEFINE_SUITE(item_manager,
    INCLUDE_TEST__STATELESS(item_manager__initialize__all_templates_empty),
    INCLUDE_TEST__STATELESS(item_manager__register_and_get__returns_registered_item),
    INCLUDE_TEST__STATELESS(item_manager__get_unregistered__returns_empty),
    INCLUDE_TEST__STATELESS(item_manager__register_overwrites__previous_value),
    END_TESTS)
