#include <process/test_suite_process_filesystem_process.h>

#include <process/filesystem_process.c>

void m_test_fsp_handler__noop(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

/**
 * @spec    docs/specs/core/process/filesystem_process.h.spec.md
 * @section 1.3.1 Initialization — initialize_process_as__filesystem_process
 *
 * Verifies that the process's p_process_data is set to the
 * provided Serialization_Request pointer.
 */
TEST_FUNCTION(initialize_process_as__filesystem_process__sets_data_to_serialization_request) {
    Process process;
    Serialization_Request sr;
    int user_data = 42;

    memset(&process, 0, sizeof(process));
    memset(&sr, 0, sizeof(sr));

    initialize_process(
            &process,
            1,
            m_test_fsp_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__filesystem_process(
            &process,
            &sr,
            &user_data);

    munit_assert_ptr_equal(
            process.p_process_data,
            &sr);

    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/process/filesystem_process.h.spec.md
 * @section 1.3.1 Initialization — initialize_process_as__filesystem_process
 *
 * Verifies that the user data pointer is stored in
 * Serialization_Request.p_data.
 */
TEST_FUNCTION(initialize_process_as__filesystem_process__sets_sr_data_to_user_data) {
    Process process;
    Serialization_Request sr;
    int user_data = 42;

    memset(&process, 0, sizeof(process));
    memset(&sr, 0, sizeof(sr));

    initialize_process(
            &process,
            1,
            m_test_fsp_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__filesystem_process(
            &process,
            &sr,
            &user_data);

    munit_assert_ptr_equal(
            sr.p_data,
            &user_data);

    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/process/filesystem_process.h.spec.md
 * @section 1.3.1 Initialization — initialize_process_as__filesystem_process
 *
 * Verifies that the process kind is marked as
 * Process_Kind__Serialized after initialization.
 */
TEST_FUNCTION(initialize_process_as__filesystem_process__sets_kind_to_serialized) {
    Process process;
    Serialization_Request sr;

    memset(&process, 0, sizeof(process));
    memset(&sr, 0, sizeof(sr));

    initialize_process(
            &process,
            1,
            m_test_fsp_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__filesystem_process(
            &process,
            &sr,
            0);

    munit_assert_int(
            get_the_kind_of__process(&process),
            ==,
            Process_Kind__Serialized);

    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/process/filesystem_process.h.spec.md
 * @section 1.3.1 Initialization — initialize_process_as__filesystem_process
 *
 * Verifies that the process run handler previously set via
 * initialize_process is preserved and not overwritten.
 */
TEST_FUNCTION(initialize_process_as__filesystem_process__preserves_handler) {
    Process process;
    Serialization_Request sr;

    memset(&process, 0, sizeof(process));
    memset(&sr, 0, sizeof(sr));

    initialize_process(
            &process,
            1,
            m_test_fsp_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__filesystem_process(
            &process,
            &sr,
            0);

    munit_assert_ptr_equal(
            process.m_process_run__handler,
            m_test_fsp_handler__noop);

    return MUNIT_OK;
}

/**
 * @spec    docs/specs/core/process/filesystem_process.h.spec.md
 * @section 1.3.1 Initialization — initialize_process_as__filesystem_process
 *
 * Verifies that passing NULL as user data results in
 * Serialization_Request.p_data being set to NULL.
 */
TEST_FUNCTION(initialize_process_as__filesystem_process__null_user_data) {
    Process process;
    Serialization_Request sr;

    memset(&process, 0, sizeof(process));
    memset(&sr, 0, sizeof(sr));

    initialize_process(
            &process,
            1,
            m_test_fsp_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__filesystem_process(
            &process,
            &sr,
            0);

    munit_assert_ptr_null(sr.p_data);

    return MUNIT_OK;
}

DEFINE_SUITE(filesystem_process,
    INCLUDE_TEST__STATELESS(initialize_process_as__filesystem_process__sets_data_to_serialization_request),
    INCLUDE_TEST__STATELESS(initialize_process_as__filesystem_process__sets_sr_data_to_user_data),
    INCLUDE_TEST__STATELESS(initialize_process_as__filesystem_process__sets_kind_to_serialized),
    INCLUDE_TEST__STATELESS(initialize_process_as__filesystem_process__preserves_handler),
    INCLUDE_TEST__STATELESS(initialize_process_as__filesystem_process__null_user_data),
    END_TESTS)
