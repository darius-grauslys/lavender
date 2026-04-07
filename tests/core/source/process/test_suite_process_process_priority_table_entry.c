#include <process/test_suite_process_process_priority_table_entry.h>

#include <process/process_priority_table_entry.c>
#include <process/process_table.h>
#include <process/process.h>

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(initialize_process_priority_table_entry__sets_pointers) {
    Process_Priority_Table_Entry entry;
    Process *ptr_array[PROCESS_MAX_QUANTITY_OF];
    memset(ptr_array, 0, sizeof(ptr_array));

    initialize_process_priority_table_entry(
            &entry,
            &ptr_array[0]);

    munit_assert_ptr_equal(
            entry.p_ptr_process__youngest_of__priority,
            &ptr_array[0]);
    munit_assert_ptr_equal(
            entry.p_ptr_process__oldest_of__priority,
            &ptr_array[0]);
    munit_assert_ptr_equal(
            entry.p_ptr_process__current_priority_to__swap,
            &ptr_array[0]);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.5 Validation (static inline)
///
TEST_FUNCTION(is_process_priority_table_entry__empty__true_when_initialized) {
    Process_Priority_Table_Entry entry;
    Process *ptr_array[PROCESS_MAX_QUANTITY_OF];
    memset(ptr_array, 0, sizeof(ptr_array));

    initialize_process_priority_table_entry(
            &entry,
            &ptr_array[0]);

    munit_assert_true(
            is_process_priority_table_entry__empty(&entry));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.5 Validation (static inline)
///
TEST_FUNCTION(get_quantity_of__processes__returns_zero_when_empty) {
    Process_Priority_Table_Entry entry;
    Process *ptr_array[PROCESS_MAX_QUANTITY_OF];
    memset(ptr_array, 0, sizeof(ptr_array));

    initialize_process_priority_table_entry(
            &entry,
            &ptr_array[0]);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_priority_table_entry(&entry),
            ==,
            0);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.3 Insertion / Removal
///
TEST_FUNCTION(add_process__increases_count) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_a;
    initialize_process(
            &proc_a, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_a);

    Quantity__u32 count =
        get_quantity_of__processes_in__process_priority_table_entry(
                &table.process_priority_table[0]);

    munit_assert_uint32(count, ==, 1);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.3 Insertion / Removal
///
TEST_FUNCTION(add_two_processes__count_is_two) {
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
    add_process_to__process_table(&table, &proc_b);

    Quantity__u32 count =
        get_quantity_of__processes_in__process_priority_table_entry(
                &table.process_priority_table[0]);

    munit_assert_uint32(count, ==, 2);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.3 Insertion / Removal
///
TEST_FUNCTION(remove_process__decreases_count) {
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
    add_process_to__process_table(&table, &proc_b);

    remove_process_from__process_table(&table, &proc_a);

    Quantity__u32 count =
        get_quantity_of__processes_in__process_priority_table_entry(
                &table.process_priority_table[0]);

    munit_assert_uint32(count, ==, 1);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.4 Polling
///
TEST_FUNCTION(poll_next__returns_process_from_entry) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_a;
    initialize_process(
            &proc_a, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_a);

    Process *p_out = 0;
    poll_next_p_process_from__process_priority_table_entry(
            &table.process_priority_table[0],
            &p_out);

    munit_assert_ptr_equal(p_out, &proc_a);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.4 Polling
///
TEST_FUNCTION(poll_next__wraps_around_single_process) {
    Process_Table table;
    initialize_process_table(&table);

    Process proc_a;
    initialize_process(
            &proc_a, 1, 0, 0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    add_process_to__process_table(&table, &proc_a);

    Process *p_out = 0;
    bool wrapped =
        poll_next_p_process_from__process_priority_table_entry(
                &table.process_priority_table[0],
                &p_out);

    munit_assert_true(wrapped);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_priority_table_entry.h.spec.md
/// Section: 1.4.4 Polling
///
TEST_FUNCTION(poll_next__empty_entry_returns_true_immediately) {
    Process_Priority_Table_Entry entry;
    Process *ptr_array[PROCESS_MAX_QUANTITY_OF];
    memset(ptr_array, 0, sizeof(ptr_array));

    initialize_process_priority_table_entry(
            &entry,
            &ptr_array[0]);

    Process *p_out = 0;
    bool wrapped =
        poll_next_p_process_from__process_priority_table_entry(
                &entry,
                &p_out);

    munit_assert_true(wrapped);

    return MUNIT_OK;
}

DEFINE_SUITE(process_priority_table_entry,
    INCLUDE_TEST__STATELESS(initialize_process_priority_table_entry__sets_pointers),
    INCLUDE_TEST__STATELESS(is_process_priority_table_entry__empty__true_when_initialized),
    INCLUDE_TEST__STATELESS(get_quantity_of__processes__returns_zero_when_empty),
    INCLUDE_TEST__STATELESS(add_process__increases_count),
    INCLUDE_TEST__STATELESS(add_two_processes__count_is_two),
    INCLUDE_TEST__STATELESS(remove_process__decreases_count),
    INCLUDE_TEST__STATELESS(poll_next__returns_process_from_entry),
    INCLUDE_TEST__STATELESS(poll_next__wraps_around_single_process),
    INCLUDE_TEST__STATELESS(poll_next__empty_entry_returns_true_immediately),
    END_TESTS)
