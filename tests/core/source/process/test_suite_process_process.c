#include <process/test_suite_process_process.h>

#include <process/process.c>

TEST_FUNCTION(initialize_process_as__empty_process__sets_status_to_none) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__None);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__empty_process__sets_uuid_to_unknown) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_uint32(
            process._serialization_header.uuid,
            ==,
            IDENTIFIER__UNKNOWN__u32);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__empty_process__clears_handlers) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_ptr_null(process.m_process_run__handler);
    munit_assert_ptr_null(process.m_process_dispose__handler);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__empty_process__clears_data_pointer) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_ptr_null(process.p_process_data);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__empty_process__clears_enqueued_process) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_ptr_null(process.p_enqueued_process);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__empty_process__clears_scratch_values) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_int32(process.process_valueA__i32, ==, 0);
    munit_assert_int32(process.process_valueB__i32, ==, 0);

    return MUNIT_OK;
}

void m_test_handler__dummy(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

TEST_FUNCTION(initialize_process__sets_uuid) {
    Process process;
    Identifier__u32 uuid = 42;

    initialize_process(
            &process,
            uuid,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_uint32(
            process._serialization_header.uuid,
            ==,
            uuid);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process__sets_run_handler) {
    Process process;

    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_equal(
            process.m_process_run__handler,
            m_test_handler__dummy);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process__sets_data_pointer) {
    Process process;
    int my_data = 99;

    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            &my_data,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_equal(
            process.p_process_data,
            &my_data);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process__sets_priority) {
    Process process;

    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    munit_assert_uint8(
            process.process_priority__u8,
            ==,
            PROCESS_PRIORITY__1);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process__sets_flags) {
    Process process;

    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAG__IS_CRITICAL);

    munit_assert_uint8(
            process.process_flags__u8,
            ==,
            PROCESS_FLAG__IS_CRITICAL);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process__sets_status_to_idle) {
    Process process;

    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Idle);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__serialized_process__sets_kind_to_serialized) {
    Process process;
    Serialization_Request sr;
    memset(&sr, 0, sizeof(sr));

    initialize_process_as__serialized_process(
            &process,
            1,
            m_test_handler__dummy,
            &sr,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_int(
            process.the_kind_of__process_this__process_is,
            ==,
            Process_Kind__Serialized);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_process_as__serialized_process__sets_critical_flag) {
    Process process;
    Serialization_Request sr;
    memset(&sr, 0, sizeof(sr));

    initialize_process_as__serialized_process(
            &process,
            1,
            m_test_handler__dummy,
            &sr,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_true(is_process__critical(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(complete_process__sets_status_to_complete) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    complete_process(&process);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Complete);

    return MUNIT_OK;
}

TEST_FUNCTION(fail_process__sets_status_to_fail) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    fail_process(&process);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Fail);

    return MUNIT_OK;
}

TEST_FUNCTION(stop_process__sets_status_to_stopping) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    stop_process(&process);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Stopping);

    return MUNIT_OK;
}

TEST_FUNCTION(set_process_as__stopped__sets_status_to_stopped) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    stop_process(&process);
    set_process_as__stopped(&process);

    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Stopped);

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__active__true_when_idle) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_true(is_process__active(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__active__false_when_complete) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    complete_process(&process);

    munit_assert_false(is_process__active(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__active__false_when_failed) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    fail_process(&process);

    munit_assert_false(is_process__active(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__finished__true_when_complete) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    complete_process(&process);

    munit_assert_true(is_process__finished(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__finished__true_when_failed) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    fail_process(&process);

    munit_assert_true(is_process__finished(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__finished__true_when_stopped) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    stop_process(&process);
    set_process_as__stopped(&process);

    munit_assert_true(is_process__finished(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__finished__false_when_active) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_false(is_process__finished(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__available__true_when_none) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_true(is_process__available(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__available__false_when_active) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_false(is_process__available(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(enqueue_process__sets_enqueued_status) {
    Process process_first;
    Process process_second;

    initialize_process(
            &process_first,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process(
            &process_second,
            2,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    enqueue_process(&process_second, &process_first);

    munit_assert_true(is_process__enqueued(&process_second));

    return MUNIT_OK;
}

TEST_FUNCTION(enqueue_process__links_enqueued_process) {
    Process process_first;
    Process process_second;

    initialize_process(
            &process_first,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process(
            &process_second,
            2,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    enqueue_process(&process_second, &process_first);

    munit_assert_ptr_equal(
            process_first.p_enqueued_process,
            &process_second);

    return MUNIT_OK;
}

TEST_FUNCTION(set_process_as__dequeued__sets_status_to_idle) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process_as__enqueued(&process);
    munit_assert_true(is_process__enqueued(&process));

    set_process_as__dequeued(&process);
    munit_assert_int(
            process.the_kind_of_status__this_process_has,
            ==,
            Process_Status_Kind__Idle);

    return MUNIT_OK;
}

TEST_FUNCTION(does_process_have__run_handler__true_when_set) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_true(does_process_have__run_handler(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(does_process_have__run_handler__false_when_empty) {
    Process process;
    initialize_process_as__empty_process(&process);

    munit_assert_false(does_process_have__run_handler(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(does_process_have__dispose_handler__false_when_not_set) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_false(does_process_have__dispose_handler(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(set_process__dispose_handler__sets_handler) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process__dispose_handler(&process, m_test_handler__dummy);

    munit_assert_true(does_process_have__dispose_handler(&process));
    munit_assert_ptr_equal(
            process.m_process_dispose__handler,
            m_test_handler__dummy);

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__critical__false_by_default) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_false(is_process__critical(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(set_process_as__critical__sets_flag) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process_as__critical(&process);

    munit_assert_true(is_process__critical(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(set_process_as__NOT_critical__clears_flag) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAG__IS_CRITICAL);

    munit_assert_true(is_process__critical(&process));

    set_process_as__NOT_critical(&process);

    munit_assert_false(is_process__critical(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(is_process__sub_process__false_by_default) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_false(is_process__sub_process(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(set_process_as__sub_process__sets_flag) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process_as__sub_process(&process);

    munit_assert_true(is_process__sub_process(&process));

    return MUNIT_OK;
}

TEST_FUNCTION(get_the_kind_of__process__returns_correct_kind) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_int(
            get_the_kind_of__process(&process),
            ==,
            Process_Kind__None);

    return MUNIT_OK;
}

TEST_FUNCTION(set_process__sub_state__sets_sub_state) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process__sub_state(&process, 5);

    munit_assert_uint8(
            process.process_sub_state__u8,
            ==,
            5);

    return MUNIT_OK;
}

TEST_FUNCTION(get_process_priorty_of__process__returns_priority) {
    Process process;
    initialize_process(
            &process,
            1,
            m_test_handler__dummy,
            0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    munit_assert_uint8(
            get_process_priorty_of__process(&process),
            ==,
            PROCESS_PRIORITY__1);

    return MUNIT_OK;
}

DEFINE_SUITE(process,
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__sets_status_to_none),
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__sets_uuid_to_unknown),
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__clears_handlers),
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__clears_data_pointer),
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__clears_enqueued_process),
    INCLUDE_TEST__STATELESS(initialize_process_as__empty_process__clears_scratch_values),
    INCLUDE_TEST__STATELESS(initialize_process__sets_uuid),
    INCLUDE_TEST__STATELESS(initialize_process__sets_run_handler),
    INCLUDE_TEST__STATELESS(initialize_process__sets_data_pointer),
    INCLUDE_TEST__STATELESS(initialize_process__sets_priority),
    INCLUDE_TEST__STATELESS(initialize_process__sets_flags),
    INCLUDE_TEST__STATELESS(initialize_process__sets_status_to_idle),
    INCLUDE_TEST__STATELESS(initialize_process_as__serialized_process__sets_kind_to_serialized),
    INCLUDE_TEST__STATELESS(initialize_process_as__serialized_process__sets_critical_flag),
    INCLUDE_TEST__STATELESS(complete_process__sets_status_to_complete),
    INCLUDE_TEST__STATELESS(fail_process__sets_status_to_fail),
    INCLUDE_TEST__STATELESS(stop_process__sets_status_to_stopping),
    INCLUDE_TEST__STATELESS(set_process_as__stopped__sets_status_to_stopped),
    INCLUDE_TEST__STATELESS(is_process__active__true_when_idle),
    INCLUDE_TEST__STATELESS(is_process__active__false_when_complete),
    INCLUDE_TEST__STATELESS(is_process__active__false_when_failed),
    INCLUDE_TEST__STATELESS(is_process__finished__true_when_complete),
    INCLUDE_TEST__STATELESS(is_process__finished__true_when_failed),
    INCLUDE_TEST__STATELESS(is_process__finished__true_when_stopped),
    INCLUDE_TEST__STATELESS(is_process__finished__false_when_active),
    INCLUDE_TEST__STATELESS(is_process__available__true_when_none),
    INCLUDE_TEST__STATELESS(is_process__available__false_when_active),
    INCLUDE_TEST__STATELESS(enqueue_process__sets_enqueued_status),
    INCLUDE_TEST__STATELESS(enqueue_process__links_enqueued_process),
    INCLUDE_TEST__STATELESS(set_process_as__dequeued__sets_status_to_idle),
    INCLUDE_TEST__STATELESS(does_process_have__run_handler__true_when_set),
    INCLUDE_TEST__STATELESS(does_process_have__run_handler__false_when_empty),
    INCLUDE_TEST__STATELESS(does_process_have__dispose_handler__false_when_not_set),
    INCLUDE_TEST__STATELESS(set_process__dispose_handler__sets_handler),
    INCLUDE_TEST__STATELESS(is_process__critical__false_by_default),
    INCLUDE_TEST__STATELESS(set_process_as__critical__sets_flag),
    INCLUDE_TEST__STATELESS(set_process_as__NOT_critical__clears_flag),
    INCLUDE_TEST__STATELESS(is_process__sub_process__false_by_default),
    INCLUDE_TEST__STATELESS(set_process_as__sub_process__sets_flag),
    INCLUDE_TEST__STATELESS(get_the_kind_of__process__returns_correct_kind),
    INCLUDE_TEST__STATELESS(set_process__sub_state__sets_sub_state),
    INCLUDE_TEST__STATELESS(get_process_priorty_of__process__returns_priority),
    END_TESTS)
