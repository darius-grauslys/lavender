#include <game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__multiplayer.h>

#include <game_action/core/global_space/game_action__global_space__request__multiplayer.c>

TEST_FUNCTION(game_action__global_space__request__multiplayer__register_server__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__global_space__request_for__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Global_Space__Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__global_space__request__multiplayer__register_client__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__global_space__request_for__client(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Global_Space__Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__global_space__request__multiplayer,
    INCLUDE_TEST__STATELESS(game_action__global_space__request__multiplayer__register_server__populates_table),
    INCLUDE_TEST__STATELESS(game_action__global_space__request__multiplayer__register_client__populates_table),
    END_TESTS)
