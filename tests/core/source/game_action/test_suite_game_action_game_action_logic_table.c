#include <game_action/test_suite_game_action_game_action_logic_table.h>

#include <game_action/game_action_logic_table.c>

static void dummy_process_handler(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

TEST_FUNCTION(game_action_logic_table__initialize__zeroes_entries) {
    Game_Action_Logic_Table table;
    memset(&table, 0xFF, sizeof(table));

    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    munit_assert_ptr_not_null(p_entry);
    munit_assert_ptr_null(
            get_m_process__outbound_of__game_action_logic_entry(
                p_entry));
    munit_assert_ptr_null(
            get_m_process__inbound_of__game_action_logic_entry(
                p_entry));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__get_entry__returns_correct_entry) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry_bad_request =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    Game_Action_Logic_Entry *p_entry_tcp_connect =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect);

    munit_assert_ptr_not_null(p_entry_bad_request);
    munit_assert_ptr_not_null(p_entry_tcp_connect);
    munit_assert_ptr_not_equal(
            p_entry_bad_request,
            p_entry_tcp_connect);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__get_entry__returns_null_for_unknown) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Unknown);

    munit_assert_ptr_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__get_entry__returns_null_for_none) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__None);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__get_outbound_handler__returns_registered) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    initialize_game_action_logic_entry_as__process__out(
            p_entry,
            0,
            dummy_process_handler,
            PROCESS_FLAGS__NONE);

    m_Process handler =
        get_m_process__outbound_for__this_game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    munit_assert_ptr_equal(handler, dummy_process_handler);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__get_inbound_handler__returns_registered) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect);

    initialize_game_action_logic_entry_as__process__in(
            p_entry,
            0,
            dummy_process_handler,
            PROCESS_FLAGS__NONE);

    m_Process handler =
        get_m_process__inbound_for__this_game_action_kind(
                &table,
                Game_Action_Kind__TCP_Connect);

    munit_assert_ptr_equal(handler, dummy_process_handler);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_table__unregistered_kind__has_null_handlers) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    m_Process outbound =
        get_m_process__outbound_for__this_game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    m_Process inbound =
        get_m_process__inbound_for__this_game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    munit_assert_ptr_null(outbound);
    munit_assert_ptr_null(inbound);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action_logic_table,
    INCLUDE_TEST__STATELESS(game_action_logic_table__initialize__zeroes_entries),
    INCLUDE_TEST__STATELESS(game_action_logic_table__get_entry__returns_correct_entry),
    INCLUDE_TEST__STATELESS(game_action_logic_table__get_entry__returns_null_for_unknown),
    INCLUDE_TEST__STATELESS(game_action_logic_table__get_entry__returns_null_for_none),
    INCLUDE_TEST__STATELESS(game_action_logic_table__get_outbound_handler__returns_registered),
    INCLUDE_TEST__STATELESS(game_action_logic_table__get_inbound_handler__returns_registered),
    INCLUDE_TEST__STATELESS(game_action_logic_table__unregistered_kind__has_null_handlers),
    END_TESTS)
