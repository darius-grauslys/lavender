#include <process/test_suite_process_game_action_process.h>

#include <process/game_action_process.c>

void m_test_gap_handler__noop(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

/**
 * Spec:    docs/specs/core/process/game_action_process.h.spec.md
 * Section: 1.3.1 Initialization
 *
 * Verifies that initialize_process_as__game_action_process sets
 * p_process_data to point to the provided Game_Action.
 */
TEST_FUNCTION(initialize_process_as__game_action_process__sets_data_pointer) {
    Process process;
    Game_Action game_action;
    memset(&process, 0, sizeof(process));
    memset(&game_action, 0, sizeof(game_action));

    initialize_process(
            &process,
            1,
            m_test_gap_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__game_action_process(
            &process,
            &game_action);

    munit_assert_ptr_equal(
            process.p_process_data,
            &game_action);

    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/process/game_action_process.h.spec.md
 * Section: 1.3.1 Initialization
 *
 * Verifies that initialize_process_as__game_action_process marks
 * the process kind as Process_Kind__Game_Action.
 */
TEST_FUNCTION(initialize_process_as__game_action_process__sets_kind) {
    Process process;
    Game_Action game_action;
    memset(&process, 0, sizeof(process));
    memset(&game_action, 0, sizeof(game_action));

    initialize_process(
            &process,
            1,
            m_test_gap_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__game_action_process(
            &process,
            &game_action);

    munit_assert_int(
            get_the_kind_of__process(&process),
            ==,
            Process_Kind__Game_Action);

    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/process/game_action_process.h.spec.md
 * Section: 1.3.1 Initialization
 *
 * Verifies that initialize_process_as__game_action_process preserves
 * the previously assigned m_process_run__handler.
 */
TEST_FUNCTION(initialize_process_as__game_action_process__preserves_handler) {
    Process process;
    Game_Action game_action;
    memset(&process, 0, sizeof(process));
    memset(&game_action, 0, sizeof(game_action));

    initialize_process(
            &process,
            1,
            m_test_gap_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__game_action_process(
            &process,
            &game_action);

    munit_assert_ptr_equal(
            process.m_process_run__handler,
            m_test_gap_handler__noop);

    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/process/game_action_process.h.spec.md
 * Section: 1.3.1 Initialization
 *
 * Verifies that initialize_process_as__game_action_process preserves
 * the previously assigned process_priority__u8.
 */
TEST_FUNCTION(initialize_process_as__game_action_process__preserves_priority) {
    Process process;
    Game_Action game_action;
    memset(&process, 0, sizeof(process));
    memset(&game_action, 0, sizeof(game_action));

    initialize_process(
            &process,
            1,
            m_test_gap_handler__noop,
            0,
            PROCESS_PRIORITY__1,
            PROCESS_FLAGS__NONE);

    initialize_process_as__game_action_process(
            &process,
            &game_action);

    munit_assert_uint8(
            process.process_priority__u8,
            ==,
            PROCESS_PRIORITY__1);

    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/process/game_action_process.h.spec.md
 * Section: 1.3.1 Initialization
 *
 * Verifies that initialize_process_as__game_action_process preserves
 * the previously assigned serialization_header uuid.
 */
TEST_FUNCTION(initialize_process_as__game_action_process__preserves_uuid) {
    Process process;
    Game_Action game_action;
    memset(&process, 0, sizeof(process));
    memset(&game_action, 0, sizeof(game_action));

    Identifier__u32 uuid = 777;
    initialize_process(
            &process,
            uuid,
            m_test_gap_handler__noop,
            0,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);

    initialize_process_as__game_action_process(
            &process,
            &game_action);

    munit_assert_uint32(
            process._serialization_header.uuid,
            ==,
            uuid);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action_process,
    INCLUDE_TEST__STATELESS(initialize_process_as__game_action_process__sets_data_pointer),
    INCLUDE_TEST__STATELESS(initialize_process_as__game_action_process__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_process_as__game_action_process__preserves_handler),
    INCLUDE_TEST__STATELESS(initialize_process_as__game_action_process__preserves_priority),
    INCLUDE_TEST__STATELESS(initialize_process_as__game_action_process__preserves_uuid),
    END_TESTS)
