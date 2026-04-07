#include <game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_connect.h>

#include <game_action/core/tcp/game_action__tcp_connect.c>

///
/// Spec: game_action__tcp_connect.h.spec.md
/// Section: 1.5.2. Initialization
///
TEST_FUNCTION(game_action__tcp_connect__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__tcp_connect(
            &ga,
            0xDEADBEEF);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__TCP_Connect);

    return MUNIT_OK;
}

///
/// Spec: game_action__tcp_connect.h.spec.md
/// Section: 1.5.2. Initialization
///
TEST_FUNCTION(game_action__tcp_connect__initialize__sets_session_token) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__tcp_connect(
            &ga,
            0x12345678ABCDEF00ULL);

    munit_assert_uint64(
            ga.ga_kind__tcp_connect__session_token,
            ==,
            0x12345678ABCDEF00ULL);

    return MUNIT_OK;
}

///
/// Spec: game_action__tcp_connect.h.spec.md
/// Section: 1.5.1. Registration
///
TEST_FUNCTION(game_action__tcp_connect__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__tcp_connect(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__tcp_connect,
    INCLUDE_TEST__STATELESS(game_action__tcp_connect__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__tcp_connect__initialize__sets_session_token),
    INCLUDE_TEST__STATELESS(game_action__tcp_connect__register__populates_table),
    END_TESTS)
