#include <game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_connect__reject.h>

#include <game_action/core/tcp/game_action__tcp_connect__reject.c>

///
/// Spec: game_action__tcp_connect__reject.h.spec.md
/// Section: 1.5.1. Registration
///
TEST_FUNCTION(game_action__tcp_connect__reject__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__tcp_connect__reject(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect__Reject);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__tcp_connect__reject,
    INCLUDE_TEST__STATELESS(game_action__tcp_connect__reject__register__populates_table),
    END_TESTS)
