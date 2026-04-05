#include <sort/sort_list/test_suite_sort_sort_list_sort_list_manager.h>

#include <sort/sort_list/sort_list_manager.c>

TEST_FUNCTION(sort_list_manager__initialize) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    munit_assert_uint32(
        get_quantity_of__allocated_sort_lists_in__sort_list_manager(&manager),
        ==, 0);
    munit_assert_uint32(
        get_quantity_of__allocated_sort_nodes_in__sort_list_manager(&manager),
        ==, 0);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__allocate_sort_list) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_List *p_sort_list =
        allocate_sort_list_in__sort_list_manager(&manager, 8);

    munit_assert_ptr_not_null(p_sort_list);
    munit_assert_true(is_sort_list__allocated(p_sort_list));
    munit_assert_uint32(get_length_of__sort_list(p_sort_list), ==, 8);

    munit_assert_uint32(
        get_quantity_of__allocated_sort_lists_in__sort_list_manager(&manager),
        ==, 1);
    munit_assert_uint32(
        get_quantity_of__allocated_sort_nodes_in__sort_list_manager(&manager),
        ==, 8);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__release_sort_list) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_List *p_sort_list =
        allocate_sort_list_in__sort_list_manager(&manager, 4);
    munit_assert_ptr_not_null(p_sort_list);

    release_sort_list_in__sort_list_manager(&manager, p_sort_list);

    munit_assert_uint32(
        get_quantity_of__allocated_sort_lists_in__sort_list_manager(&manager),
        ==, 0);
    munit_assert_uint32(
        get_quantity_of__allocated_sort_nodes_in__sort_list_manager(&manager),
        ==, 0);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__allocate_multiple) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_List *p_list_1 =
        allocate_sort_list_in__sort_list_manager(&manager, 4);
    Sort_List *p_list_2 =
        allocate_sort_list_in__sort_list_manager(&manager, 8);

    munit_assert_ptr_not_null(p_list_1);
    munit_assert_ptr_not_null(p_list_2);
    munit_assert_ptr_not_equal(p_list_1, p_list_2);

    munit_assert_uint32(
        get_quantity_of__allocated_sort_lists_in__sort_list_manager(&manager),
        ==, 2);
    munit_assert_uint32(
        get_quantity_of__allocated_sort_nodes_in__sort_list_manager(&manager),
        ==, 12);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__release_and_reallocate) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_List *p_list_1 =
        allocate_sort_list_in__sort_list_manager(&manager, 4);
    munit_assert_ptr_not_null(p_list_1);

    release_sort_list_in__sort_list_manager(&manager, p_list_1);

    Sort_List *p_list_2 =
        allocate_sort_list_in__sort_list_manager(&manager, 4);
    munit_assert_ptr_not_null(p_list_2);

    munit_assert_uint32(
        get_quantity_of__allocated_sort_lists_in__sort_list_manager(&manager),
        ==, 1);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__get_sort_list_by_index) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_List *p_list_0 =
        get_p_sort_list_by__index_in__sort_list_manager(&manager, 0);
    Sort_List *p_list_1 =
        get_p_sort_list_by__index_in__sort_list_manager(&manager, 1);

    munit_assert_ptr_not_null(p_list_0);
    munit_assert_ptr_not_null(p_list_1);
    munit_assert_ptr_not_equal(p_list_0, p_list_1);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__get_sort_node_by_index) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    Sort_Node *p_node_0 =
        get_p_sort_node_by__index_in__sort_list_manager(&manager, 0);
    Sort_Node *p_node_1 =
        get_p_sort_node_by__index_in__sort_list_manager(&manager, 1);

    munit_assert_ptr_not_null(p_node_0);
    munit_assert_ptr_not_null(p_node_1);
    munit_assert_ptr_not_equal(p_node_0, p_node_1);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__all_nodes_initially_unallocated) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    for (int i = 0; i < SORT_NODE__MAXIMUM_QUANTITY_OF; i++) {
        Sort_Node *p_node =
            get_p_sort_node_by__index_in__sort_list_manager(&manager, i);
        munit_assert_false(is_sort_node__allocated(p_node));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list_manager__all_lists_initially_unallocated) {
    Sort_List_Manager manager;
    initialize_sort_list_manager(&manager);

    for (int i = 0; i < SORT_LIST__MAXIMUM_QUANTITY_OF; i++) {
        Sort_List *p_list =
            get_p_sort_list_by__index_in__sort_list_manager(&manager, i);
        munit_assert_false(is_sort_list__allocated(p_list));
    }

    return MUNIT_OK;
}

DEFINE_SUITE(sort_list_manager,
    INCLUDE_TEST__STATELESS(sort_list_manager__initialize),
    INCLUDE_TEST__STATELESS(sort_list_manager__allocate_sort_list),
    INCLUDE_TEST__STATELESS(sort_list_manager__release_sort_list),
    INCLUDE_TEST__STATELESS(sort_list_manager__allocate_multiple),
    INCLUDE_TEST__STATELESS(sort_list_manager__release_and_reallocate),
    INCLUDE_TEST__STATELESS(sort_list_manager__get_sort_list_by_index),
    INCLUDE_TEST__STATELESS(sort_list_manager__get_sort_node_by_index),
    INCLUDE_TEST__STATELESS(sort_list_manager__all_nodes_initially_unallocated),
    INCLUDE_TEST__STATELESS(sort_list_manager__all_lists_initially_unallocated),
    END_TESTS)
