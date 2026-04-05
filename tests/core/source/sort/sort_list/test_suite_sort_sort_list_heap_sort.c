#include <sort/sort_list/test_suite_sort_sort_list_heap_sort.h>

#include <sort/sort_list/heap_sort.c>

static Signed_Quantity__i32 test_heap_heuristic__ascending(
        Sort_Node *p_node__one,
        Sort_Node *p_node__two) {
    return (Signed_Quantity__i32)p_node__one->heuristic_value
         - (Signed_Quantity__i32)p_node__two->heuristic_value;
}

TEST_FUNCTION(heap_sort__initialize_as_heap) {
    Sort_List list;
    Sort_Node nodes[8];

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap(&list);

    munit_assert_ptr_not_null((void*)list.m_sort);

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__initialize_as_heap_sort) {
    Sort_List list;
    Sort_Node nodes[8];

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__empty(&nodes[i]);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap_sort(&list);

    munit_assert_ptr_not_null((void*)list.m_sort);

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__heapify_completes) {
    Sort_List list;
    Sort_Node nodes[8];

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__allocated(&nodes[i], (Signed_Quantity__i16)(8 - i), INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap(&list);
    request_resorting_of__heap(&list);

    munit_assert_false(is_heap__heapifed(&list));

    int max_steps = 1000;
    int steps = 0;
    while (!run_sort__once(&list) && steps < max_steps) {
        steps++;
    }

    munit_assert_true(is_heap__heapifed(&list));

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__heap_sort_completes) {
    Sort_List list;
    Sort_Node nodes[8];

    Signed_Quantity__i16 values[8] = { 5, 3, 8, 1, 7, 2, 6, 4 };

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__allocated(&nodes[i], values[i], INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    int max_steps = 10000;
    int steps = 0;
    while (!run_sort__once(&list) && steps < max_steps) {
        steps++;
    }

    munit_assert_true(is_heap_sort__sorted(&list));

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__heap_sort_produces_sorted_order) {
    Sort_List list;
    Sort_Node nodes[8];

    Signed_Quantity__i16 values[8] = { 5, 3, 8, 1, 7, 2, 6, 4 };

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__allocated(&nodes[i], values[i], INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    run_sort(&list);

    for (int i = 0; i < 7; i++) {
        munit_assert_int(
            nodes[i].heuristic_value, <=,
            nodes[i + 1].heuristic_value);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__single_element) {
    Sort_List list;
    Sort_Node nodes[1];

    initialize_sort_node_as__allocated(&nodes[0], 42, INDEX__UNKNOWN__SORT_NODE);

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            1);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    int max_steps = 100;
    int steps = 0;
    while (!run_sort__once(&list) && steps < max_steps) {
        steps++;
    }

    munit_assert_int(nodes[0].heuristic_value, ==, 42);

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__already_sorted) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__allocated(&nodes[i], (Signed_Quantity__i16)(i + 1), INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            4);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    run_sort(&list);

    for (int i = 0; i < 3; i++) {
        munit_assert_int(
            nodes[i].heuristic_value, <=,
            nodes[i + 1].heuristic_value);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__reverse_sorted) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__allocated(&nodes[i], (Signed_Quantity__i16)(4 - i), INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            4);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    run_sort(&list);

    for (int i = 0; i < 3; i++) {
        munit_assert_int(
            nodes[i].heuristic_value, <=,
            nodes[i + 1].heuristic_value);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__request_resorting_resets_state) {
    Sort_List list;
    Sort_Node nodes[4];

    for (int i = 0; i < 4; i++) {
        initialize_sort_node_as__allocated(&nodes[i], (Signed_Quantity__i16)(4 - i), INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            4);

    initialize_sort_list_as__heap(&list);
    request_resorting_of__heap(&list);

    munit_assert_false(is_heap__heapifed(&list));

    run_sort(&list);

    munit_assert_true(is_heap__heapifed(&list));

    request_resorting_of__heap(&list);

    munit_assert_false(is_heap__heapifed(&list));

    return MUNIT_OK;
}

TEST_FUNCTION(heap_sort__run_sort_with_steps) {
    Sort_List list;
    Sort_Node nodes[8];

    Signed_Quantity__i16 values[8] = { 5, 3, 8, 1, 7, 2, 6, 4 };

    for (int i = 0; i < 8; i++) {
        initialize_sort_node_as__allocated(&nodes[i], values[i], INDEX__UNKNOWN__SORT_NODE);
    }

    initialize_sort_list_as__allocated(
            &list,
            nodes,
            test_heap_heuristic__ascending,
            8);

    initialize_sort_list_as__heap_sort(&list);
    request_resorting_of__heap_sort(&list);

    bool is_done = false;
    int iterations = 0;
    int max_iterations = 1000;
    while (!is_done && iterations < max_iterations) {
        is_done = run_sort_with__this_many_steps(&list, 2);
        iterations++;
    }

    munit_assert_true(is_done);

    for (int i = 0; i < 7; i++) {
        munit_assert_int(
            nodes[i].heuristic_value, <=,
            nodes[i + 1].heuristic_value);
    }

    return MUNIT_OK;
}

DEFINE_SUITE(heap_sort,
    INCLUDE_TEST__STATELESS(heap_sort__initialize_as_heap),
    INCLUDE_TEST__STATELESS(heap_sort__initialize_as_heap_sort),
    INCLUDE_TEST__STATELESS(heap_sort__heapify_completes),
    INCLUDE_TEST__STATELESS(heap_sort__heap_sort_completes),
    INCLUDE_TEST__STATELESS(heap_sort__heap_sort_produces_sorted_order),
    INCLUDE_TEST__STATELESS(heap_sort__single_element),
    INCLUDE_TEST__STATELESS(heap_sort__already_sorted),
    INCLUDE_TEST__STATELESS(heap_sort__reverse_sorted),
    INCLUDE_TEST__STATELESS(heap_sort__request_resorting_resets_state),
    INCLUDE_TEST__STATELESS(heap_sort__run_sort_with_steps),
    END_TESTS)
