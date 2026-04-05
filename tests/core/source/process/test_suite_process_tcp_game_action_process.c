#include <process/test_suite_process_tcp_game_action_process.h>

#include <process/tcp_game_action_process.c>
#include <process/game_action_process.h>

void m_test_tcp_handler__noop(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

TEST_FUNCTION(initialize_tcp_receiver__fails_without_game_context) {
    // TODO: initialize_process_as__tcp_game_action_payload_receiver does not have a implementation, and this module cannot be tested at this time.
    //
    // Process process;
    // Game_Action game_action;
    // Game game;
    // uint8_t buffer[256];

    // memset(&process, 0, sizeof(process));
    // memset(&game_action, 0, sizeof(game_action));
    // memset(&game, 0, sizeof(game));
    // memset(buffer, 0, sizeof(buffer));

    // initialize_process(
    //         &process,
    //         1,
    //         m_test_tcp_handler__noop,
    //         0,
    //         PROCESS_PRIORITY__0_MAXIMUM,
    //         PROCESS_FLAGS__NONE);

    // initialize_process_as__game_action_process(
    //         &process,
    //         &game_action);

    // bool result =
    //     initialize_process_as__tcp_game_action_payload_receiver(
    //             &game,
    //             &process,
    //             buffer,
    //             sizeof(buffer));

    // munit_assert_false(result);

    return MUNIT_FAIL;
}

TEST_FUNCTION(initialize_tcp_receiver__process_data_was_game_action) {
    // TODO: initialize_process_as__tcp_game_action_payload_receiver does not have a implementation, and this module cannot be tested at this time.
    //
    // Process process;
    // Game_Action game_action;

    // memset(&process, 0, sizeof(process));
    // memset(&game_action, 0, sizeof(game_action));

    // initialize_process(
    //         &process,
    //         1,
    //         m_test_tcp_handler__noop,
    //         0,
    //         PROCESS_PRIORITY__0_MAXIMUM,
    //         PROCESS_FLAGS__NONE);

    // initialize_process_as__game_action_process(
    //         &process,
    //         &game_action);

    // munit_assert_ptr_equal(
    //         process.p_process_data,
    //         &game_action);

    return MUNIT_FAIL;
}

DEFINE_SUITE(tcp_game_action_process,
    INCLUDE_TEST__STATELESS(initialize_tcp_receiver__fails_without_game_context),
    INCLUDE_TEST__STATELESS(initialize_tcp_receiver__process_data_was_game_action),
    END_TESTS)
