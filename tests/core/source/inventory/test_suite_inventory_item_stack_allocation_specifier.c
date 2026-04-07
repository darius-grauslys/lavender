#include <inventory/test_suite_inventory_item_stack_allocation_specifier.h>

#include <inventory/item_stack_allocation_specifier.c>

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.4 Postconditions
///
TEST_FUNCTION(item_stack_alloc_spec__initialize_as_empty__not_allocated) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier_as__empty(&spec);
    munit_assert_false(is_item_stack_allocation_specifier__allocated(&spec));
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.1 Initialization
///
TEST_FUNCTION(item_stack_alloc_spec__initialize__sets_kind) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier(&spec, Item_Kind__None, 0);
    munit_assert_int(spec.the_kind_of_item__this_specifier_is_for, ==, Item_Kind__None);
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.3 Preconditions
///
TEST_FUNCTION(item_stack_alloc_spec__initialize__with_null_factory) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier(&spec, Item_Kind__Unknown, 0);
    munit_assert_int(spec.the_kind_of_item__this_specifier_is_for, ==, Item_Kind__Unknown);
    munit_assert_ptr_null(spec.f_item_stack__create);
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.2 Allocation State Management
/// @section 1.5.4 Postconditions
///
TEST_FUNCTION(item_stack_alloc_spec__set_allocated__is_allocated) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier_as__empty(&spec);
    set_item_stack_allocation_specifier_as__allocated(&spec);
    munit_assert_true(is_item_stack_allocation_specifier__allocated(&spec));
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.2 Allocation State Management
/// @section 1.5.4 Postconditions
///
TEST_FUNCTION(item_stack_alloc_spec__set_deallocated__is_not_allocated) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier(&spec, Item_Kind__Unknown, 0);
    set_item_stack_allocation_specifier_as__allocated(&spec);
    munit_assert_true(is_item_stack_allocation_specifier__allocated(&spec));
    set_item_stack_allocation_specifier_as__deallocated(&spec);
    munit_assert_false(is_item_stack_allocation_specifier__allocated(&spec));
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.4 Postconditions
///
TEST_FUNCTION(item_stack_alloc_spec__initialize_as_empty__kind_is_none) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier_as__empty(&spec);
    munit_assert_int(spec.the_kind_of_item__this_specifier_is_for, ==, Item_Kind__None);
    return MUNIT_OK;
}

///
/// @spec    core/inventory/item_stack_allocation_specifier.h.spec.md
/// @section 1.4.1 Initialization
/// @section 1.5.4 Postconditions
///
TEST_FUNCTION(item_stack_alloc_spec__initialize_as_empty__factory_is_null) {
    Item_Stack_Allocation_Specifier spec;
    initialize_item_stack_allocation_specifier_as__empty(&spec);
    munit_assert_ptr_null(spec.f_item_stack__create);
    return MUNIT_OK;
}

DEFINE_SUITE(item_stack_allocation_specifier,
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__initialize_as_empty__not_allocated),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__initialize__with_null_factory),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__set_allocated__is_allocated),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__set_deallocated__is_not_allocated),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__initialize_as_empty__kind_is_none),
    INCLUDE_TEST__STATELESS(item_stack_alloc_spec__initialize_as_empty__factory_is_null),
    END_TESTS)
