#include <game_action/test_suite_game_action_game_action_logic_entry.h>

#include <game_action/game_action_logic_entry.c>

static void dummy_process_handler(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

static void dummy_process_handler_2(
        Process *p_this_process,
        Game *p_game) {
    (void)p_this_process;
    (void)p_game;
}

TEST_FUNCTION(game_action_logic_entry__initialize__sets_all_fields) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0xFF, sizeof(entry));

    initialize_game_action_logic_entry(
            &entry,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__NONE,
            0,
            0,
            PROCESS_FLAGS__NONE,
            0,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_null(
            get_m_process__outbound_of__game_action_logic_entry(
                &entry));
    munit_assert_ptr_null(
            get_m_process__inbound_of__game_action_logic_entry(
                &entry));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__initialize_as_process_out__sets_outbound) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0, sizeof(entry));

    initialize_game_action_logic_entry_as__process__out(
            &entry,
            0,
            dummy_process_handler,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_equal(
            get_m_process__outbound_of__game_action_logic_entry(&entry),
            dummy_process_handler);
    munit_assert_ptr_null(
            get_m_process__inbound_of__game_action_logic_entry(&entry));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__initialize_as_process_in__sets_inbound) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0, sizeof(entry));

    initialize_game_action_logic_entry_as__process__in(
            &entry,
            0,
            dummy_process_handler,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_null(
            get_m_process__outbound_of__game_action_logic_entry(&entry));
    munit_assert_ptr_equal(
            get_m_process__inbound_of__game_action_logic_entry(&entry),
            dummy_process_handler);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__initialize_as_process_out_and_in__sets_both) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0, sizeof(entry));

    initialize_game_action_logic_entry_as__process__out_and_in(
            &entry,
            0,
            dummy_process_handler,
            PROCESS_FLAGS__NONE,
            dummy_process_handler_2,
            PROCESS_FLAGS__NONE);

    munit_assert_ptr_equal(
            get_m_process__outbound_of__game_action_logic_entry(&entry),
            dummy_process_handler);
    munit_assert_ptr_equal(
            get_m_process__inbound_of__game_action_logic_entry(&entry),
            dummy_process_handler_2);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__initialize_as_message__sets_no_handlers) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0xFF, sizeof(entry));

    initialize_game_action_logic_entry_as__message(
            &entry);

    munit_assert_ptr_null(
            get_m_process__outbound_of__game_action_logic_entry(&entry));
    munit_assert_ptr_null(
            get_m_process__inbound_of__game_action_logic_entry(&entry));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__get_process_priority__returns_set_value) {
    Game_Action_Logic_Entry entry;
    memset(&entry, 0, sizeof(entry));

    initialize_game_action_logic_entry_as__process__out(
            &entry,
            5,
            dummy_process_handler,
            PROCESS_FLAGS__NONE);

    munit_assert_uint8(
            get_process_priority__game_action_logic_entry(&entry),
            ==,
            5);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__sanitize_outbound__applies_flags) {
    Game_Action_Logic_Entry entry;
    Game_Action ga;
    initialize_game_action(&ga);

    ga.game_action_flags = 0xFF;

    initialize_game_action_logic_entry(
            &entry,
            GAME_ACTION_FLAGS__BIT_IS_LOCAL,
            GAME_ACTION_FLAGS__BIT_IS_ALLOCATED,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__NONE,
            0,
            0,
            PROCESS_FLAGS__NONE,
            0,
            PROCESS_FLAGS__NONE);

    santize_game_action__outbound(&entry, &ga);

    munit_assert_true(is_game_action__allocated(&ga));
    munit_assert_true(is_game_action__local(&ga));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_logic_entry__sanitize_inbound__applies_flags) {
    Game_Action_Logic_Entry entry;
    Game_Action ga;
    initialize_game_action(&ga);

    ga.game_action_flags = 0xFF;

    initialize_game_action_logic_entry(
            &entry,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__NONE,
            GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND,
            GAME_ACTION_FLAGS__BIT_IS_ALLOCATED,
            0,
            0,
            PROCESS_FLAGS__NONE,
            0,
            PROCESS_FLAGS__NONE);

    santize_game_action__inbound(&entry, &ga);

    munit_assert_true(is_game_action__allocated(&ga));
    munit_assert_true(is_game_action__inbound(&ga));

    return MUNIT_OK;
}

DEFINE_SUITE(game_action_logic_entry,
    INCLUDE_TEST__STATELESS(game_action_logic_entry__initialize__sets_all_fields),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__initialize_as_process_out__sets_outbound),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__initialize_as_process_in__sets_inbound),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__initialize_as_process_out_and_in__sets_both),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__initialize_as_message__sets_no_handlers),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__get_process_priority__returns_set_value),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__sanitize_outbound__applies_flags),
    INCLUDE_TEST__STATELESS(game_action_logic_entry__sanitize_inbound__applies_flags),
    END_TESTS)
