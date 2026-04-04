#include <game_action/core/tcp/test_suite_game_action_core_tcp_game_action__tcp_delivery.h>

#include <game_action/core/tcp/game_action__tcp_delivery.c>

TEST_FUNCTION(game_action__tcp_delivery__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__tcp_delivery(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__TCP_Delivery);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__tcp_delivery__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    uint8_t payload[4] = {0xAA, 0xBB, 0xCC, 0xDD};

    initialize_game_action_for__tcp_delivery(
            &ga,
            100,
            200,
            payload,
            4,
            0);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__TCP_Delivery);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__tcp_delivery__initialize__sets_client_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    uint8_t payload[4] = {0};

    initialize_game_action_for__tcp_delivery(
            &ga,
            555,
            200,
            payload,
            4,
            0);

    munit_assert_uint32(
            get_client_uuid_from__game_action(&ga),
            ==,
            555);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__tcp_delivery__initialize__sets_response_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    uint8_t payload[4] = {0};

    initialize_game_action_for__tcp_delivery(
            &ga,
            100,
            999,
            payload,
            4,
            0);

    munit_assert_uint32(
            get_response_uuid_from__game_action(&ga),
            ==,
            999);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__tcp_delivery__initialize__sets_packet_index) {
    Game_Action ga;
    initialize_game_action(&ga);

    uint8_t payload[4] = {0};

    initialize_game_action_for__tcp_delivery(
            &ga,
            100,
            200,
            payload,
            4,
            7);

    munit_assert_uint16(
            ga.ga_kind__tcp_delivery__packet_index,
            ==,
            7);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__tcp_delivery__initialize__copies_payload) {
    Game_Action ga;
    initialize_game_action(&ga);

    uint8_t payload[4] = {0xDE, 0xAD, 0xBE, 0xEF};

    initialize_game_action_for__tcp_delivery(
            &ga,
            100,
            200,
            payload,
            4,
            0);

    munit_assert_uint8(ga.ga_kind__tcp_delivery__payload[0], ==, 0xDE);
    munit_assert_uint8(ga.ga_kind__tcp_delivery__payload[1], ==, 0xAD);
    munit_assert_uint8(ga.ga_kind__tcp_delivery__payload[2], ==, 0xBE);
    munit_assert_uint8(ga.ga_kind__tcp_delivery__payload[3], ==, 0xEF);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__tcp_delivery,
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__register__populates_table),
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__initialize__sets_client_uuid),
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__initialize__sets_response_uuid),
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__initialize__sets_packet_index),
    INCLUDE_TEST__STATELESS(game_action__tcp_delivery__initialize__copies_payload),
    END_TESTS)
