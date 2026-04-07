#include <process/test_suite_process_process_manager.h>

#include <process/process_manager.c>

void m_test_pm_handler__noop(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

void m_test_pm_handler__complete_immediately(
        Process *p_this_process,
        Game *p_game) {
    (void)p_game;
    complete_process(p_this_process);
}

void m_test_pm_handler__fail_immediately(
        Process *p_this_process,
        Game *p_game) {
    (void)p_game;
    fail_process(p_this_process);
}

static int test_dispose_call_count = 0;

void m_test_pm_handler__dispose_counter(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
    test_dispose_call_count++;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(initialize_process_manager__all_slots_available) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    for (Index__u32 i = 0; i < PROCESS_MAX_QUANTITY_OF; i++) {
        munit_assert_true(
                is_process__available(&pm.processes[i]));
    }

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(initialize_process_manager__latest_is_null) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    munit_assert_ptr_null(pm.p_process__latest);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.1 Initialization
///
TEST_FUNCTION(initialize_process_manager__process_count_is_zero) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_manager(&pm),
            ==,
            0);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__returns_non_null) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_not_null(p);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__increments_count) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_manager(&pm),
            ==,
            1);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__sets_latest) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process *latest =
        get_p_latest_allocated_process_from__process_manager(&pm);

    munit_assert_ptr_equal(latest, p);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.5 Lookup (static inline)
///
TEST_FUNCTION(get_p_latest__returns_null_after_consumption) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    get_p_latest_allocated_process_from__process_manager(&pm);
    Process *second_call =
        get_p_latest_allocated_process_from__process_manager(&pm);

    munit_assert_ptr_null(second_call);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process_with__uuid__assigns_correct_uuid) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Identifier__u32 uuid = 12345;
    Process *p = run_process_with__uuid(
            &pm,
            m_test_pm_handler__noop,
            uuid,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_not_null(p);
    munit_assert_uint32(
            p->_serialization_header.uuid,
            ==,
            uuid);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.5 Lookup (static inline)
///
TEST_FUNCTION(get_p_process_by__uuid__finds_process) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Identifier__u32 uuid = 54321;
    run_process_with__uuid(
            &pm,
            m_test_pm_handler__noop,
            uuid,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process *found = get_p_process_by__uuid(&pm, uuid);

    munit_assert_ptr_not_null(found);
    munit_assert_uint32(
            found->_serialization_header.uuid,
            ==,
            uuid);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.5 Lookup (static inline)
///
TEST_FUNCTION(get_p_process_by__uuid__returns_null_for_unknown) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *found = get_p_process_by__uuid(&pm, 99999);

    munit_assert_ptr_null(found);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.6 Query
///
TEST_FUNCTION(run_multiple_processes__count_is_correct) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    for (int i = 0; i < 5; i++) {
        run_process(
                &pm,
                m_test_pm_handler__noop,
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAGS__NONE);
    }

    munit_assert_uint32(
            get_quantity_of__processes_in__process_manager(&pm),
            ==,
            5);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__sets_run_handler) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_equal(
            p->m_process_run__handler,
            m_test_pm_handler__noop);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__sets_priority) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    munit_assert_uint8(
            p->process_priority__u8,
            ==,
            PROCESS_PRIORITY__1);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.3 Running Processes
///
TEST_FUNCTION(run_process__sets_flags) {
    Process_Manager pm;
    initialize_process_manager(&pm);

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAG__IS_CRITICAL);

    munit_assert_true(is_process__critical(p));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.2 Allocation / Deallocation
///
TEST_FUNCTION(release_process__decrements_count) {
    Process_Manager pm;
    initialize_process_manager(&pm);
    Game game;
    memset(&game, 0, sizeof(game));

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    release_process_from__process_manager(
            &game, &pm, p);

    munit_assert_uint32(
            get_quantity_of__processes_in__process_manager(&pm),
            ==,
            0);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.2 Allocation / Deallocation
///
TEST_FUNCTION(release_process__invokes_dispose_handler) {
    Process_Manager pm;
    initialize_process_manager(&pm);
    Game game;
    memset(&game, 0, sizeof(game));

    test_dispose_call_count = 0;

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    set_process__dispose_handler(p, m_test_pm_handler__dispose_counter);

    release_process_from__process_manager(
            &game, &pm, p);

    munit_assert_int(test_dispose_call_count, ==, 1);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/process/process_manager.h.spec.md
/// Section: 1.4.2 Allocation / Deallocation
///
TEST_FUNCTION(release_process__slot_becomes_available) {
    Process_Manager pm;
    initialize_process_manager(&pm);
    Game game;
    memset(&game, 0, sizeof(game));

    Process *p = run_process(
            &pm,
            m_test_pm_handler__noop,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    Process *slot = p;
    release_process_from__process_manager(
            &game, &pm, p);

    munit_assert_true(is_process__available(slot));

    return MUNIT_OK;
}

DEFINE_SUITE(process_manager,
    INCLUDE_TEST__STATELESS(initialize_process_manager__all_slots_available),
    INCLUDE_TEST__STATELESS(initialize_process_manager__latest_is_null),
    INCLUDE_TEST__STATELESS(initialize_process_manager__process_count_is_zero),
    INCLUDE_TEST__STATELESS(run_process__returns_non_null),
    INCLUDE_TEST__STATELESS(run_process__increments_count),
    INCLUDE_TEST__STATELESS(run_process__sets_latest),
    INCLUDE_TEST__STATELESS(get_p_latest__returns_null_after_consumption),
    INCLUDE_TEST__STATELESS(run_process_with__uuid__assigns_correct_uuid),
    INCLUDE_TEST__STATELESS(get_p_process_by__uuid__finds_process),
    INCLUDE_TEST__STATELESS(get_p_process_by__uuid__returns_null_for_unknown),
    INCLUDE_TEST__STATELESS(run_multiple_processes__count_is_correct),
    INCLUDE_TEST__STATELESS(run_process__sets_run_handler),
    INCLUDE_TEST__STATELESS(run_process__sets_priority),
    INCLUDE_TEST__STATELESS(run_process__sets_flags),
    INCLUDE_TEST__STATELESS(release_process__decrements_count),
    INCLUDE_TEST__STATELESS(release_process__invokes_dispose_handler),
    INCLUDE_TEST__STATELESS(release_process__slot_becomes_available),
    END_TESTS)
