#include <game_action/core/test_suite_game_action_core_game_action__bad_request.h>

#include <game_action/core/game_action__bad_request.c>

TEST_FUNCTION(game_action__bad_request__initialize__sets_kind) {
    Game_Action ga;
    Game_Action original;
    initialize_game_action(&ga);
    initialize_game_action(&original);
    original._serialiation_header.uuid = 555;

    initialize_game_action_for__bad_request(
            &ga,
            &original,
            42);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Bad_Request);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__bad_request__initialize__sets_error_code) {
    Game_Action ga;
    Game_Action original;
    initialize_game_action(&ga);
    initialize_game_action(&original);
    original._serialiation_header.uuid = 555;

    initialize_game_action_for__bad_request(
            &ga,
            &original,
            99);

    munit_assert_uint32(
            ga.ga_kind__bad_request__request_error_code,
            ==,
            99);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__bad_request__initialize__sets_response_uuid) {
    Game_Action ga;
    Game_Action original;
    initialize_game_action(&ga);
    initialize_game_action(&original);
    original._serialiation_header.uuid = 777;

    initialize_game_action_for__bad_request(
            &ga,
            &original,
            1);

    munit_assert_uint32(
            ga.uuid_of__game_action__responding_to,
            ==,
            777);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__bad_request__initialize__sets_bad_request_flag) {
    Game_Action ga;
    Game_Action original;
    initialize_game_action(&ga);
    initialize_game_action(&original);
    original._serialiation_header.uuid = 100;

    initialize_game_action_for__bad_request(
            &ga,
            &original,
            0);

    munit_assert_true(is_game_action__bad_request(&ga));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__bad_request__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__bad_request(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Bad_Request);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__bad_request,
    INCLUDE_TEST__STATELESS(game_action__bad_request__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__bad_request__initialize__sets_error_code),
    INCLUDE_TEST__STATELESS(game_action__bad_request__initialize__sets_response_uuid),
    INCLUDE_TEST__STATELESS(game_action__bad_request__initialize__sets_bad_request_flag),
    INCLUDE_TEST__STATELESS(game_action__bad_request__register__populates_table),
    END_TESTS)
