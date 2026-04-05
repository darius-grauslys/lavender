#include <sort/sort_list/test_suite_sort_sort_list_sort_node.h>

#include <sort/sort_list/sort_node.c>

TEST_FUNCTION(sort_node__initialize_as_empty) {
    Sort_Node node;
    node.p_node_data = (void*)0xDEADBEEF;
    node.heuristic_value = 42;
    node.index_for__next_node = 100;
    node.is_allocated = true;

    initialize_sort_node_as__empty(&node);

    munit_assert_ptr_null(node.p_node_data);
    munit_assert_int(node.heuristic_value, ==, 0);
    munit_assert_false(node.is_allocated);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__initialize_as_allocated) {
    Sort_Node node;
    initialize_sort_node_as__empty(&node);

    initialize_sort_node_as__allocated(&node, 55, 7);

    munit_assert_int(node.heuristic_value, ==, 55);
    munit_assert_uint16(node.index_for__next_node, ==, 7);
    munit_assert_true(node.is_allocated);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__initialize_as_allocated__with_unknown_next) {
    Sort_Node node;
    initialize_sort_node_as__empty(&node);

    initialize_sort_node_as__allocated(&node, -10, INDEX__UNKNOWN__SORT_NODE);

    munit_assert_int(node.heuristic_value, ==, -10);
    munit_assert_uint16(node.index_for__next_node, ==, INDEX__UNKNOWN__SORT_NODE);
    munit_assert_true(node.is_allocated);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__set_allocated) {
    Sort_Node node;
    initialize_sort_node_as__empty(&node);

    munit_assert_false(is_sort_node__allocated(&node));

    set_sort_node_as__allocated(&node);
    munit_assert_true(is_sort_node__allocated(&node));

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__set_deallocated) {
    Sort_Node node;
    initialize_sort_node_as__allocated(&node, 0, 0);

    munit_assert_true(is_sort_node__allocated(&node));

    set_sort_node_as__deallocated(&node);
    munit_assert_false(is_sort_node__allocated(&node));

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__set_p_node_data) {
    Sort_Node node;
    initialize_sort_node_as__empty(&node);

    int data = 12345;
    set_sort_node__p_node_data(&node, &data);

    munit_assert_ptr_equal(node.p_node_data, &data);

    return MUNIT_OK;
}

TEST_FUNCTION(sort_node__negative_heuristic) {
    Sort_Node node;
    initialize_sort_node_as__allocated(&node, -128, 0);

    munit_assert_int(node.heuristic_value, ==, -128);
    munit_assert_true(node.is_allocated);

    return MUNIT_OK;
}

DEFINE_SUITE(sort_node,
    INCLUDE_TEST__STATELESS(sort_node__initialize_as_empty),
    INCLUDE_TEST__STATELESS(sort_node__initialize_as_allocated),
    INCLUDE_TEST__STATELESS(sort_node__initialize_as_allocated__with_unknown_next),
    INCLUDE_TEST__STATELESS(sort_node__set_allocated),
    INCLUDE_TEST__STATELESS(sort_node__set_deallocated),
    INCLUDE_TEST__STATELESS(sort_node__set_p_node_data),
    INCLUDE_TEST__STATELESS(sort_node__negative_heuristic),
    END_TESTS)
