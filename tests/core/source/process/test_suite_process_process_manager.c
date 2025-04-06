#include "defines.h"
#include "process/process_manager.h"
#include <process/test_suite_process_process_manager.h>

#include <process/process_manager.c>

TEST_FUNCTION(initialize_process_manager) {
    Process_Manager process_manager;
    initialize_process_manager(&process_manager);
    
    munit_assert_int(
            get_quantity_of__processes_in__process_manager(
                &process_manager),
            ==,
            0);

    return MUNIT_OK;
}

TEST_FUNCTION(release_process_from__process_manager) {
    return MUNIT_SKIP;
}

///
/// Gets the next available process.
/// Return nullptr if no process is available.
///
TEST_FUNCTION(allocate_process_in__process_manager) {
    return MUNIT_SKIP;
}

///
/// Don't invoke.
/// Returns quantity of ticks elapsed.
///
TEST_FUNCTION(poll_process_manager) {
    return MUNIT_OK;
}

///
/// returns null on failure.
///
TEST_FUNCTION(run_process_with__uuid) {
    return MUNIT_SKIP;
}

void _TEST_process(Process *p_process, Game *p_game) {
}

TEST_FUNCTION(run_process) {
    Process_Manager process_manager;
    initialize_process_manager(&process_manager);

    Process *p_process =
        run_process(
                &process_manager, 
                _TEST_process, 
                PROCESS_FLAGS__NONE);

    munit_assert_ptr_not_null(p_process);

    return MUNIT_OK;
}

TEST_FUNCTION(get_quantity_of__processes_in__process_manager) {
    Process_Manager process_manager;
    initialize_process_manager(&process_manager);
    
    munit_assert_int(
            get_quantity_of__processes_in__process_manager(
                &process_manager),
            ==,
            0);

    Process *p_process = allocate_process_in__process_manager(
            &process_manager, 
            0);

    munit_assert_ptr_not_null(p_process);

    munit_assert_int(
            get_quantity_of__processes_in__process_manager(
                &process_manager),
            ==,
            1);

    release_process_from__process_manager(
            &process_manager, 
            p_process);

    munit_assert_int(
            get_quantity_of__processes_in__process_manager(
                &process_manager),
            ==,
            0);

    return MUNIT_OK;
}

DEFINE_SUITE(
        process_manager, 
        INCLUDE_TEST__STATELESS(initialize_process_manager),
        INCLUDE_TEST__STATELESS(release_process_from__process_manager),
        INCLUDE_TEST__STATELESS(allocate_process_in__process_manager),
        INCLUDE_TEST__STATELESS(poll_process_manager),
        INCLUDE_TEST__STATELESS(run_process_with__uuid),
        INCLUDE_TEST__STATELESS(run_process),
        INCLUDE_TEST__STATELESS(get_quantity_of__processes_in__process_manager),
        END_TESTS)
