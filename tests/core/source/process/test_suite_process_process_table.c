#include <process/test_suite_process_process_table.h>

#include <process/process_table.c>

TEST_FUNCTION(initialize_process_table__zeroes_pointer_array) {
    Process_Table table;
    initialize_process_table(&table);

    for (Index__u32 i = 0; i < PROCESS_MAX_QUANTITY_OF; i++) {
        munit_assert_ptr_null(table.ptr_array_of__processes[i]);
    }

    return MUNIT_OK;
}

TEST_FUNCTION(get_quantity_of__processes__returns_zero_after_init) {
    Process_Table table;
    initialize_process_table(&table);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            0);

    return MUNIT_OK;
}

TEST_FUNCTION(add_process__returns_true_on_success) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc;
    initialize_process(
            &proc, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    bool result = add_process_to__process_table(&table, &proc);

    munit_assert_true(result);

    return MUNIT_OK;
}

TEST_FUNCTION(add_process__increments_count) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc;
    initialize_process(
            &proc, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            1);

    return MUNIT_OK;
}

TEST_FUNCTION(add_multiple_processes__at_same_priority) {
    Process_Table table;
    initialize_process_table(&table);

    Process procs[3];
    for (int i = 0; i < 3; i++) {
        initialize_process(
                &procs[i], i + 1, 0, 0,
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAGS__NONE);
        add_process_to__process_table(&table, &procs[i]);
    }

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            3);

    return MUNIT_OK;
}

TEST_FUNCTION(add_processes__at_different_priorities) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_p0;
    initialize_process(
            &proc_p0, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process proc_p1;
    initialize_process(
            &proc_p1, 2, 0, 0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_p0);
    add_process_to__process_table(&table, &proc_p1);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            2);

    return MUNIT_OK;
}

TEST_FUNCTION(remove_process__decrements_count) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc;
    initialize_process(
            &proc, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc);
    remove_process_from__process_table(&table, &proc);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            0);

    return MUNIT_OK;
}

TEST_FUNCTION(remove_process__from_middle_of_priority) {
    Process_Table table;
    initialize_process_table(&table);

    Process procs[3];
    for (int i = 0; i < 3; i++) {
        initialize_process(
                &procs[i], i + 1, 0, 0,
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAGS__NONE);
        add_process_to__process_table(&table, &procs[i]);
    }

    remove_process_from__process_table(&table, &procs[1]);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            2);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__returns_null_when_empty) {
    Process_Table table;
    initialize_process_table(&table);

    begin_polling_of__process_table(&table);
    Process *p = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_null(p);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__returns_single_process) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc;
    initialize_process(
            &proc, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc);

    begin_polling_of__process_table(&table);
    Process *p = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_equal(p, &proc);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__returns_null_after_all_polled) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc;
    initialize_process(
            &proc, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc);

    begin_polling_of__process_table(&table);
    poll_next_p_process_from__process_table(&table);
    Process *p = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_null(p);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__higher_priority_polled_first) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_p1;
    initialize_process(
            &proc_p1, 1, 0, 0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    Process proc_p0;
    initialize_process(
            &proc_p0, 2, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_p1);
    add_process_to__process_table(&table, &proc_p0);

    begin_polling_of__process_table(&table);
    Process *first = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_equal(first, &proc_p0);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__all_processes_across_priorities) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_p0;
    initialize_process(
            &proc_p0, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process proc_p1;
    initialize_process(
            &proc_p1, 2, 0, 0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_p0);
    add_process_to__process_table(&table, &proc_p1);

    begin_polling_of__process_table(&table);

    Process *first = poll_next_p_process_from__process_table(&table);
    Process *second = poll_next_p_process_from__process_table(&table);
    Process *third = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_not_null(first);
    munit_assert_ptr_not_null(second);
    munit_assert_ptr_null(third);

    return MUNIT_OK;
}

TEST_FUNCTION(poll__round_robin_within_priority) {
    Process_Table table;
    initialize_process_table(&table);

    Process procs[3];
    for (int i = 0; i < 3; i++) {
        initialize_process(
                &procs[i], i + 1, 0, 0,
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAGS__NONE);
        add_process_to__process_table(&table, &procs[i]);
    }

    begin_polling_of__process_table(&table);
    Process *a = poll_next_p_process_from__process_table(&table);
    Process *b = poll_next_p_process_from__process_table(&table);
    Process *c = poll_next_p_process_from__process_table(&table);
    Process *end = poll_next_p_process_from__process_table(&table);

    munit_assert_ptr_not_null(a);
    munit_assert_ptr_not_null(b);
    munit_assert_ptr_not_null(c);
    munit_assert_ptr_null(end);

    munit_assert_ptr_not_equal(a, b);
    munit_assert_ptr_not_equal(b, c);
    munit_assert_ptr_not_equal(a, c);

    return MUNIT_OK;
}

TEST_FUNCTION(add_remove_add__count_is_correct) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_a;
    initialize_process(
            &proc_a, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process proc_b;
    initialize_process(
            &proc_b, 2, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_a);
    remove_process_from__process_table(&table, &proc_a);
    add_process_to__process_table(&table, &proc_b);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            1);

    return MUNIT_OK;
}

TEST_FUNCTION(remove_from_different_priority__maintains_other_priorities) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_p0;
    initialize_process(
            &proc_p0, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process proc_p1;
    initialize_process(
            &proc_p1, 2, 0, 0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_p0);
    add_process_to__process_table(&table, &proc_p1);

    remove_process_from__process_table(&table, &proc_p1);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_table(&table),
            ==,
            1);

    begin_polling_of__process_table(&table);
    Process *p = poll_next_p_process_from__process_table(&table);
    munit_assert_ptr_equal(p, &proc_p0);

    return MUNIT_OK;
}

DEFINE_SUITE(process_table,
    INCLUDE_TEST__STATELESS(initialize_process_table__zeroes_pointer_array),
    INCLUDE_TEST__STATELESS(get_quantity_of__processes__returns_zero_after_init),
    INCLUDE_TEST__STATELESS(add_process__returns_true_on_success),
    INCLUDE_TEST__STATELESS(add_process__increments_count),
    INCLUDE_TEST__STATELESS(add_multiple_processes__at_same_priority),
    INCLUDE_TEST__STATELESS(add_processes__at_different_priorities),
    INCLUDE_TEST__STATELESS(remove_process__decrements_count),
    INCLUDE_TEST__STATELESS(remove_process__from_middle_of_priority),
    INCLUDE_TEST__STATELESS(poll__returns_null_when_empty),
    INCLUDE_TEST__STATELESS(poll__returns_single_process),
    INCLUDE_TEST__STATELESS(poll__returns_null_after_all_polled),
    INCLUDE_TEST__STATELESS(poll__higher_priority_polled_first),
    INCLUDE_TEST__STATELESS(poll__all_processes_across_priorities),
    INCLUDE_TEST__STATELESS(poll__round_robin_within_priority),
    INCLUDE_TEST__STATELESS(add_remove_add__count_is_correct),
    INCLUDE_TEST__STATELESS(remove_from_different_priority__maintains_other_priorities),
    END_TESTS)
