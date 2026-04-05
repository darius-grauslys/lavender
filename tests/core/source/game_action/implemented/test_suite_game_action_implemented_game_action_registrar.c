#include <game_action/implemented/test_suite_game_action_implemented_game_action_registrar.h>

#include <game_action/implemented/game_action_registrar.c>
#include <game_action/game_action_logic_table.h>
#include <types/implemented/game_action_kind.h>

TEST_FUNCTION(game_action_registrar__register_offline__populates_hitbox) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__offline(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Hitbox);

    munit_assert_ptr_not_null(p_entry);
    munit_assert_ptr_not_null(
            get_m_process__outbound_of__game_action_logic_entry(
                p_entry));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_offline__populates_global_space_request) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__offline(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Global_Space__Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_offline__populates_bad_request) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__offline(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_offline__populates_world_load_world) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__offline(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__World__Load_World);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_server__populates_entity_spawn) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_client__populates_entity_spawn) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__client(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_server__populates_tcp_connect) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_registrar__register_server__populates_tcp_delivery) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_actions__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Delivery);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action_registrar,
    INCLUDE_TEST__STATELESS(game_action_registrar__register_offline__populates_hitbox),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_offline__populates_global_space_request),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_offline__populates_bad_request),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_offline__populates_world_load_world),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_server__populates_entity_spawn),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_client__populates_entity_spawn),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_server__populates_tcp_connect),
    INCLUDE_TEST__STATELESS(game_action_registrar__register_server__populates_tcp_delivery),
    END_TESTS)
