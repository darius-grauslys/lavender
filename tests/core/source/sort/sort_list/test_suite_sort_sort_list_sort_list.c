#include <sort/sort_list/test_suite_sort_sort_list_sort_list.h>

#include <sort/sort_list/sort_list.c>

static Signed_Quantity__i32 test_heuristic__ascending(
        Sort_Node *p_node__one,
        Sort_Node *p_node__two) {
    return (Signed_Quantity__i32)p_node__one->heuristic_value
         - (Signed_Quantity__i32)p_node__two->heuristic_value;
}

TEST_FUNCTION(sort_list__initialize_as_empty) {
    Sort_List list;
    list.is_allocated = true;
    list.size_of__p_node_list = 99;
    list.p_node_list = (Sort_Node*)0xDEADBEEF;

    initialize_sort_list_as__empty(&list);

    munit_assert_false(is_sort_list__allocated(&list));
    munit_assert_uint32(get_length_of__sort_list(&list), ==, 0);
    munit_assert_ptr_null(get_p_node_list_from__sort_list(&list));

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__initialize_as_allocated) {
    Sort_List list;
    Sort_Node nodes[8];

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            8);

    munit_assert_true(is_sort_list__allocated(&list));
    munit_assert_uint32(get_length_of__sort_list(&list), ==, 8);
    munit_assert_ptr_equal(get_p_node_list_from__sort_list(&list), nodes);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__get_length) {
    Sort_List list;
    Sort_Node nodes[16];

    for (int i = 0; i < 16; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            16);

    munit_assert_uint32(get_length_of__sort_list(&list), ==, 16);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__is_not_extended_by_default) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            4);

    munit_assert_false(is_sort_list__extexted(&list));
    munit_assert_ptr_null(get_extension_of__sort_list(&list));

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__get_node_by_index) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            4);

    for (int i = 0; i < 4; i++) {
        Sort_Node *p_node =
            get_p_sort_node_by__index_from__sort_list(&list, i);
        munit_assert_ptr_equal(p_node, &nodes[i]);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__get_index_of_node) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            4);

    for (int i = 0; i < 4; i++) {
        Index__u16 index =
            get_index_of__sort_node_in__sort_list(&list, &nodes[i]);
        munit_assert_uint16(index, ==, i);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__point_nodes_to_range) {
    Sort_List list;
    Sort_Node nodes[4];
    int data[4] = { 10, 20, 30, 40 };

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heuristic__ascending,
            4);

    point_sort_list__sort_nodes_to__this_range(
            &list,
            data,
            sizeof(int));

    for (int i = 0; i < 4; i++) {
        munit_assert_ptr_equal(nodes[i].p_node_data, &data[i]);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__set_heuristic) {
    Sort_List list;
    Sort_Node nodes[2];

    for (int i = 0; i < 2; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            NULL,
            2);

    set_sort_list__sort_heuristic(&list, test_heuristic__ascending);

    munit_assert_ptr_not_null((void*)list.f_sort_heuristic);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_list__allocation_flags) {
    Sort_List list;
    initialize_sort_list_as__empty(&list);

    munit_assert_false(is_sort_list__allocated(&list));

    set_sort_list_as__allocated(&list);
    munit_assert_true(is_sort_list__allocated(&list));

    set_sort_list_as__deallocated(&list);
    munit_assert_false(is_sort_list__allocated(&list));

    return MUNIT_OK;
}

DEFINE_SUITE(sort_list,
    INCLUDE_TEST__STATELESS(sort_list__initialize_as_empty),
    INCLUDE_TEST__STATELESS(sort_list__initialize_as_allocated),
    INCLUDE_TEST__STATELESS(sort_list__get_length),
    INCLUDE_TEST__STATELESS(sort_list__is_not_extended_by_default),
    INCLUDE_TEST__STATELESS(sort_list__get_node_by_index),
    INCLUDE_TEST__STATELESS(sort_list__get_index_of_node),
    INCLUDE_TEST__STATELESS(sort_list__point_nodes_to_range),
    INCLUDE_TEST__STATELESS(sort_list__set_heuristic),
    INCLUDE_TEST__STATELESS(sort_list__allocation_flags),
    END_TESTS)
