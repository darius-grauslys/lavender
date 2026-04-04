#include <game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__request__offline.h>

#include <game_action/core/global_space/game_action__global_space__request__offline.c>

TEST_FUNCTION(game_action__global_space__request__offline__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__global_space__request_for__offline(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Global_Space__Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__global_space__request__offline,
    INCLUDE_TEST__STATELESS(game_action__global_space__request__offline__register__populates_table),
    END_TESTS)
