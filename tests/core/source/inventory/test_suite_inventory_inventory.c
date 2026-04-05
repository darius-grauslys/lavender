#include <inventory/test_suite_inventory_inventory.h>

#include <inventory/inventory.c>

TEST_FUNCTION(inventory__initialize_as_empty__is_empty) {
    Inventory inventory;
    initialize_inventory_as__empty(&inventory);
    munit_assert_true(is_inventory__empty(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__initialize__has_available_stacks) {
    Inventory inventory;
    initialize_inventory(&inventory, 42);
    munit_assert_true(does_inventory_have__available_item_stacks(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__initialize__is_empty) {
    Inventory inventory;
    initialize_inventory(&inventory, 42);
    munit_assert_true(is_inventory__empty(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_item__returns_non_null) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack *p_stack = add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_ptr_not_null(p_stack);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_item__no_longer_empty) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_false(is_inventory__empty(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_item__can_find_by_kind) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    Item_Stack *p_found =
        get_first_p_item_stack_of__this_item_kind_from__inventory(
            &inventory, Item_Kind__Unknown);
    munit_assert_ptr_not_null(p_found);
    munit_assert_int(get_item_kind_of__item_stack(p_found), ==, Item_Kind__Unknown);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_item__find_nonexistent_returns_null) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    Item_Stack *p_found =
        get_first_p_item_stack_of__this_item_kind_from__inventory(
            &inventory, Item_Kind__None);
    munit_assert_ptr_null(p_found);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__does_have_item_kind__true_when_present) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_true(
        does_inventory_have_this__item_kind(&inventory, Item_Kind__Unknown));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__does_have_item_kind__false_when_absent) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    munit_assert_false(
        does_inventory_have_this__item_kind(&inventory, Item_Kind__Unknown));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__does_have_this_many__true_when_enough) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_true(
        does_inventory_have_this_many_of__item_kind(
            &inventory, Item_Kind__Unknown, 5));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__does_have_this_many__true_when_more_than_enough) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_true(
        does_inventory_have_this_many_of__item_kind(
            &inventory, Item_Kind__Unknown, 3));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__does_have_this_many__false_when_not_enough) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    munit_assert_false(
        does_inventory_have_this_many_of__item_kind(
            &inventory, Item_Kind__Unknown, 6));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__remove_item_stack__becomes_empty) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack *p_stack = add_item_to__inventory(&inventory, item, 5, 10);
    remove_p_item_stack_from__inventory(&inventory, p_stack);
    munit_assert_true(is_inventory__empty(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__remove_all__becomes_empty) {
    // TODO: remove_all_item_stacks_from__inventory lacks an implementation.
    //
    // Inventory inventory;
    // initialize_inventory(&inventory, 1);
    // Item item;
    // initialize_item(&item, Item_Kind__Unknown);
    // add_item_to__inventory(&inventory, item, 5, 10);
    // add_item_to__inventory(&inventory, item, 3, 10);
    // munit_assert_false(is_inventory__empty(&inventory));
    // remove_all_item_stacks_from__inventory(&inventory);
    // munit_assert_true(is_inventory__empty(&inventory));
    return MUNIT_FAIL;
}

TEST_FUNCTION(inventory__remove_this_many__removes_correct_quantity) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    remove_this_many_item_kinds_from__inventory(
        &inventory, Item_Kind__Unknown, 3);
    munit_assert_true(
        does_inventory_have_this_many_of__item_kind(
            &inventory, Item_Kind__Unknown, 2));
    munit_assert_false(
        does_inventory_have_this_many_of__item_kind(
            &inventory, Item_Kind__Unknown, 3));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__remove_this_many__removes_all_empties_inventory) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 5, 10);
    remove_this_many_item_kinds_from__inventory(
        &inventory, Item_Kind__Unknown, 5);
    munit_assert_false(
        does_inventory_have_this__item_kind(&inventory, Item_Kind__Unknown));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__get_by_index__returns_valid_stack) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item_Stack *p_stack =
        get_p_item_stack_from__inventory_by__index(&inventory, 0);
    munit_assert_ptr_not_null(p_stack);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_multiple__has_available_until_full) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    for (int i = 0; i < INVENTORY_ITEM_MAXIMUM_QUANTITY_OF; i++) {
        munit_assert_true(does_inventory_have__available_item_stacks(&inventory));
        Item_Stack *p_stack = add_item_to__inventory(&inventory, item, 1, 10);
        munit_assert_ptr_not_null(p_stack);
    }
    munit_assert_false(does_inventory_have__available_item_stacks(&inventory));
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__add_when_full__returns_null) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    for (int i = 0; i < INVENTORY_ITEM_MAXIMUM_QUANTITY_OF; i++) {
        add_item_to__inventory(&inventory, item, 1, 10);
    }
    Item_Stack *p_stack = add_item_to__inventory(&inventory, item, 1, 10);
    munit_assert_ptr_null(p_stack);
    return MUNIT_OK;
}

TEST_FUNCTION(inventory__iterator__finds_all_matching_stacks) {
    Inventory inventory;
    initialize_inventory(&inventory, 1);
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    add_item_to__inventory(&inventory, item, 2, 10);
    add_item_to__inventory(&inventory, item, 3, 10);

    int count = 0;
    Item_Stack *p_stack =
        get_first_p_item_stack_of__this_item_kind_from__inventory(
            &inventory, Item_Kind__Unknown);
    while (p_stack) {
        count++;
        p_stack = get_next_p_item_stack_of__this_item_kind_from__inventory(
            &inventory, p_stack, Item_Kind__Unknown);
    }
    munit_assert_int(count, ==, 2);
    return MUNIT_OK;
}

DEFINE_SUITE(inventory,
    INCLUDE_TEST__STATELESS(inventory__initialize_as_empty__is_empty),
    INCLUDE_TEST__STATELESS(inventory__initialize__has_available_stacks),
    INCLUDE_TEST__STATELESS(inventory__initialize__is_empty),
    INCLUDE_TEST__STATELESS(inventory__add_item__returns_non_null),
    INCLUDE_TEST__STATELESS(inventory__add_item__no_longer_empty),
    INCLUDE_TEST__STATELESS(inventory__add_item__can_find_by_kind),
    INCLUDE_TEST__STATELESS(inventory__add_item__find_nonexistent_returns_null),
    INCLUDE_TEST__STATELESS(inventory__does_have_item_kind__true_when_present),
    INCLUDE_TEST__STATELESS(inventory__does_have_item_kind__false_when_absent),
    INCLUDE_TEST__STATELESS(inventory__does_have_this_many__true_when_enough),
    INCLUDE_TEST__STATELESS(inventory__does_have_this_many__true_when_more_than_enough),
    INCLUDE_TEST__STATELESS(inventory__does_have_this_many__false_when_not_enough),
    INCLUDE_TEST__STATELESS(inventory__remove_item_stack__becomes_empty),
    INCLUDE_TEST__STATELESS(inventory__remove_all__becomes_empty),
    INCLUDE_TEST__STATELESS(inventory__remove_this_many__removes_correct_quantity),
    INCLUDE_TEST__STATELESS(inventory__remove_this_many__removes_all_empties_inventory),
    INCLUDE_TEST__STATELESS(inventory__get_by_index__returns_valid_stack),
    INCLUDE_TEST__STATELESS(inventory__add_multiple__has_available_until_full),
    INCLUDE_TEST__STATELESS(inventory__add_when_full__returns_null),
    INCLUDE_TEST__STATELESS(inventory__iterator__finds_all_matching_stacks),
    END_TESTS)
