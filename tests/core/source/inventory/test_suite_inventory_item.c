#include <inventory/test_suite_inventory_item.h>

#include <inventory/item.c>

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(item__initialize_item__sets_kind) {
    Item item;
    initialize_item(&item, Item_Kind__None);
    munit_assert_int(get_item_kind_of__item(&item), ==, Item_Kind__None);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.1 Initialization, 1.5.6 Postconditions
///
TEST_FUNCTION(item__initialize_item_as__empty__is_empty) {
    Item item;
    initialize_item_as__empty(&item);
    munit_assert_true(is_p_item__empty(&item));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.1 Initialization, 1.5.6 Postconditions
///
TEST_FUNCTION(item__initialize_item_as__empty__kind_is_none) {
    Item item;
    initialize_item_as__empty(&item);
    munit_assert_int(get_item_kind_of__item(&item), ==, Item_Kind__None);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.1 Initialization, 1.5.6 Postconditions
///
TEST_FUNCTION(item__get_item__empty__returns_empty_item) {
    Item item = get_item__empty();
    munit_assert_true(is_p_item__empty(&item));
    munit_assert_int(get_item_kind_of__item(&item), ==, Item_Kind__None);
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.2 Queries (static inline)
///
TEST_FUNCTION(item__is_p_item__empty__true_for_none) {
    Item item;
    initialize_item(&item, Item_Kind__None);
    munit_assert_true(is_p_item__empty(&item));
    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/inventory/item.h.spec.md
/// Section: 1.4.2 Queries (static inline), 1.5.6 Postconditions
///
TEST_FUNCTION(item__is_p_item__empty__false_for_unknown) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    munit_assert_false(is_p_item__empty(&item));
    return MUNIT_OK;
}

DEFINE_SUITE(item,
    INCLUDE_TEST__STATELESS(item__initialize_item__sets_kind),
    INCLUDE_TEST__STATELESS(item__initialize_item_as__empty__is_empty),
    INCLUDE_TEST__STATELESS(item__initialize_item_as__empty__kind_is_none),
    INCLUDE_TEST__STATELESS(item__get_item__empty__returns_empty_item),
    INCLUDE_TEST__STATELESS(item__is_p_item__empty__true_for_none),
    INCLUDE_TEST__STATELESS(item__is_p_item__empty__false_for_unknown),
    END_TESTS)
