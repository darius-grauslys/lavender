#include <inventory/test_suite_inventory_item_stack.h>

#include <inventory/item_stack.c>

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization, 1.5.6 Postconditions
 *
 * After initialize_item_stack_as__empty: is_p_item_stack__empty returns true.
 */
TEST_FUNCTION(item_stack__initialize_as_empty__is_empty) {
    Item_Stack item_stack;
    initialize_item_stack_as__empty(&item_stack, 0);
    munit_assert_true(is_p_item_stack__empty(&item_stack));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * An empty-initialized item stack has a quantity of zero.
 */
TEST_FUNCTION(item_stack__initialize_as_empty__quantity_is_zero) {
    Item_Stack item_stack;
    initialize_item_stack_as__empty(&item_stack, 0);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * An empty-initialized item stack has Item_Kind__None.
 */
TEST_FUNCTION(item_stack__initialize_as_empty__item_kind_is_none) {
    Item_Stack item_stack;
    initialize_item_stack_as__empty(&item_stack, 0);
    munit_assert_int(get_item_kind_of__item_stack(&item_stack), ==, Item_Kind__None);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * initialize_item_stack sets the quantity to the provided value.
 */
TEST_FUNCTION(item_stack__initialize__sets_quantity) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 5);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * initialize_item_stack sets the item kind to the provided item's kind.
 */
TEST_FUNCTION(item_stack__initialize__sets_item_kind) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_int(get_item_kind_of__item_stack(&item_stack), ==, Item_Kind__Unknown);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.1 Initialization
 *
 * A non-empty initialized item stack is not empty.
 */
TEST_FUNCTION(item_stack__initialize__not_empty) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_false(is_p_item_stack__empty(&item_stack));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stack__full returns true when quantity equals max quantity.
 */
TEST_FUNCTION(item_stack__is_full__when_quantity_equals_max) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 10, 10);
    munit_assert_true(is_p_item_stack__full(&item_stack));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stack__full returns false when quantity is less than max.
 */
TEST_FUNCTION(item_stack__is_not_full__when_quantity_less_than_max) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_false(is_p_item_stack__full(&item_stack));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation
 *
 * set_item_stack overwrites the stack's item, quantity, and max quantity.
 */
TEST_FUNCTION(item_stack__set_item_stack__overwrites_contents) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack_as__empty(&item_stack, 0);
    set_item_stack(&item_stack, item, 3, 10);
    munit_assert_int(get_item_kind_of__item_stack(&item_stack), ==, Item_Kind__Unknown);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 3);
    munit_assert_false(is_p_item_stack__empty(&item_stack));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation
 *
 * copy_item_stack copies source stack contents into destination.
 */
TEST_FUNCTION(item_stack__copy_item_stack__copies_contents) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack src;
    initialize_item_stack(&src, item, 1, 7, 20);
    Item_Stack dst;
    initialize_item_stack_as__empty(&dst, 0);
    copy_item_stack(&src, &dst);
    munit_assert_int(get_item_kind_of__item_stack(&dst), ==, Item_Kind__Unknown);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&dst), ==, 7);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation
 *
 * remove_quantity_of_items_from__item_stack removes items and returns 0
 * remainder when sufficient items exist.
 */
TEST_FUNCTION(item_stack__remove_quantity__removes_items) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 10, 20);
    Quantity__u32 remainder = remove_quantity_of_items_from__item_stack(&item_stack, 3);
    munit_assert_uint32(remainder, ==, 0);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 7);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation, 1.5.7 Error Handling
 *
 * remove_quantity_of_items_from__item_stack returns the underflow remainder
 * when attempting to remove more items than available.
 */
TEST_FUNCTION(item_stack__remove_quantity__returns_underflow) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 3, 20);
    Quantity__u32 remainder = remove_quantity_of_items_from__item_stack(&item_stack, 5);
    munit_assert_uint32(remainder, ==, 2);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation, 1.5.6 Postconditions
 *
 * After removing all items, the quantity is zero.
 */
TEST_FUNCTION(item_stack__remove_all__becomes_empty) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 20);
    remove_quantity_of_items_from__item_stack(&item_stack, 5);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&item_stack), ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stack_of__this_item_kind returns true when the kind matches.
 */
TEST_FUNCTION(item_stack__is_p_item_stack_of__this_item_kind__matches) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_true(is_p_item_stack_of__this_item_kind(&item_stack, Item_Kind__Unknown));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stack_of__this_item_kind returns false when the kind differs.
 */
TEST_FUNCTION(item_stack__is_p_item_stack_of__this_item_kind__no_match) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack item_stack;
    initialize_item_stack(&item_stack, item, 1, 5, 10);
    munit_assert_false(is_p_item_stack_of__this_item_kind(&item_stack, Item_Kind__None));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stacks_the_same__item_kind returns true for matching kinds.
 */
TEST_FUNCTION(item_stack__is_p_item_stacks_the_same__item_kind__same) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack stack_a;
    initialize_item_stack(&stack_a, item, 1, 5, 10);
    Item_Stack stack_b;
    initialize_item_stack(&stack_b, item, 2, 3, 10);
    munit_assert_true(is_p_item_stacks_the_same__item_kind(&stack_a, &stack_b));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.4 Queries
 *
 * is_p_item_stacks_the_same__item_kind returns false for differing kinds.
 */
TEST_FUNCTION(item_stack__is_p_item_stacks_the_same__item_kind__different) {
    Item item_a;
    initialize_item(&item_a, Item_Kind__Unknown);
    Item item_b;
    initialize_item(&item_b, Item_Kind__None);
    Item_Stack stack_a;
    initialize_item_stack(&stack_a, item_a, 1, 5, 10);
    Item_Stack stack_b;
    initialize_item_stack(&stack_b, item_b, 2, 3, 10);
    munit_assert_false(is_p_item_stacks_the_same__item_kind(&stack_a, &stack_b));
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation, 1.5.2 Merge vs. Swap Resolution
 *
 * Same item kind: quantities are merged up to the destination's max.
 * Returns false (no swap).
 */
TEST_FUNCTION(item_stack__merge__same_kind_merges_quantities) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack src;
    initialize_item_stack(&src, item, 1, 5, 10);
    Item_Stack dst;
    initialize_item_stack(&dst, item, 2, 3, 10);
    bool swapped = resolve_item_stack__merge_or_swap(&src, &dst);
    munit_assert_false(swapped);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&dst), ==, 8);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&src), ==, 0);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation, 1.5.2 Merge vs. Swap Resolution
 *
 * Same item kind: overflow remains in the source when destination reaches max.
 */
TEST_FUNCTION(item_stack__merge__overflow_remains_in_source) {
    Item item;
    initialize_item(&item, Item_Kind__Unknown);
    Item_Stack src;
    initialize_item_stack(&src, item, 1, 8, 10);
    Item_Stack dst;
    initialize_item_stack(&dst, item, 2, 7, 10);
    bool swapped = resolve_item_stack__merge_or_swap(&src, &dst);
    munit_assert_false(swapped);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&dst), ==, 10);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&src), ==, 5);
    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/inventory/item_stack.h.spec.md
 * Section: 1.4.3 Manipulation, 1.5.2 Merge vs. Swap Resolution
 *
 * Different item kinds: the two stacks are swapped entirely.
 * Returns true (swap occurred).
 */
TEST_FUNCTION(item_stack__swap__different_kinds_swap) {
    Item item_a;
    initialize_item(&item_a, Item_Kind__Unknown);
    Item item_b;
    initialize_item_as__empty(&item_b);
    Item_Stack src;
    initialize_item_stack(&src, item_a, 1, 5, 10);
    Item_Stack dst;
    initialize_item_stack(&dst, item_b, 2, 3, 10);
    bool swapped = resolve_item_stack__merge_or_swap(&src, &dst);
    munit_assert_true(swapped);
    munit_assert_int(get_item_kind_of__item_stack(&src), ==, Item_Kind__None);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&src), ==, 3);
    munit_assert_int(get_item_kind_of__item_stack(&dst), ==, Item_Kind__Unknown);
    munit_assert_uint32(get_quantity_of__items_in__item_stack(&dst), ==, 5);
    return MUNIT_OK;
}

DEFINE_SUITE(item_stack,
    INCLUDE_TEST__STATELESS(item_stack__initialize_as_empty__is_empty),
    INCLUDE_TEST__STATELESS(item_stack__initialize_as_empty__quantity_is_zero),
    INCLUDE_TEST__STATELESS(item_stack__initialize_as_empty__item_kind_is_none),
    INCLUDE_TEST__STATELESS(item_stack__initialize__sets_quantity),
    INCLUDE_TEST__STATELESS(item_stack__initialize__sets_item_kind),
    INCLUDE_TEST__STATELESS(item_stack__initialize__not_empty),
    INCLUDE_TEST__STATELESS(item_stack__is_full__when_quantity_equals_max),
    INCLUDE_TEST__STATELESS(item_stack__is_not_full__when_quantity_less_than_max),
    INCLUDE_TEST__STATELESS(item_stack__set_item_stack__overwrites_contents),
    INCLUDE_TEST__STATELESS(item_stack__copy_item_stack__copies_contents),
    INCLUDE_TEST__STATELESS(item_stack__remove_quantity__removes_items),
    INCLUDE_TEST__STATELESS(item_stack__remove_quantity__returns_underflow),
    INCLUDE_TEST__STATELESS(item_stack__remove_all__becomes_empty),
    INCLUDE_TEST__STATELESS(item_stack__is_p_item_stack_of__this_item_kind__matches),
    INCLUDE_TEST__STATELESS(item_stack__is_p_item_stack_of__this_item_kind__no_match),
    INCLUDE_TEST__STATELESS(item_stack__is_p_item_stacks_the_same__item_kind__same),
    INCLUDE_TEST__STATELESS(item_stack__is_p_item_stacks_the_same__item_kind__different),
    INCLUDE_TEST__STATELESS(item_stack__merge__same_kind_merges_quantities),
    INCLUDE_TEST__STATELESS(item_stack__merge__overflow_remains_in_source),
    INCLUDE_TEST__STATELESS(item_stack__swap__different_kinds_swap),
    END_TESTS)
