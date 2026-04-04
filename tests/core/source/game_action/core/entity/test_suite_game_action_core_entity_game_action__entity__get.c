#include <game_action/core/entity/test_suite_game_action_core_entity_game_action__entity__get.h>

#include <game_action/core/entity/game_action__entity__get.c>

TEST_FUNCTION(game_action__entity__get__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__entity__get(
            &ga,
            42);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Entity__Get);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__entity__get__initialize__sets_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__entity__get(
            &ga,
            99999);

    munit_assert_uint32(
            ga.ga_kind__entity__uuid,
            ==,
            99999);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__entity__get__register_for_server__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__entity__get_for__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Get);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__entity__get__register_for_client__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__entity__get_for__client(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Get);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__entity__get,
    INCLUDE_TEST__STATELESS(game_action__entity__get__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__entity__get__initialize__sets_uuid),
    INCLUDE_TEST__STATELESS(game_action__entity__get__register_for_server__populates_table),
    INCLUDE_TEST__STATELESS(game_action__entity__get__register_for_client__populates_table),
    END_TESTS)
