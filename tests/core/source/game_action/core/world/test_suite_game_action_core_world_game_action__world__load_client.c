#include <game_action/core/world/test_suite_game_action_core_world_game_action__world__load_client.h>

#include <game_action/core/world/game_action__world__load_client.c>

///
/// Spec: game_action__world__load_client.h.spec.md
/// Section: 1.4.2. Initialization
///
/// Verifies that initialize_game_action_for__world__load_client
/// sets the game action kind to Game_Action_Kind__World__Load_Client.
///
TEST_FUNCTION(game_action__world__load_client__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__world__load_client(
            &ga,
            42);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__World__Load_Client);

    return MUNIT_OK;
}

///
/// Spec: game_action__world__load_client.h.spec.md
/// Section: 1.4.2. Initialization, 1.3. Payload Fields
///
/// Verifies that initialize_game_action_for__world__load_client
/// sets the client UUID payload field
/// (ga_kind__world__load_world__uuid_of__client__u32).
///
TEST_FUNCTION(game_action__world__load_client__initialize__sets_client_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__world__load_client(
            &ga,
            67890);

    munit_assert_uint32(
            ga.ga_kind__world__load_world__uuid_of__client__u32,
            ==,
            67890);

    return MUNIT_OK;
}

///
/// Spec: game_action__world__load_client.h.spec.md
/// Section: 1.4.1. Registration
///
/// Verifies that register_game_action__world__load_client
/// populates the Game_Action_Logic_Table with an entry for
/// Game_Action_Kind__World__Load_Client.
///
TEST_FUNCTION(game_action__world__load_client__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__world__load_client(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__World__Load_Client);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__world__load_client,
    INCLUDE_TEST__STATELESS(game_action__world__load_client__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__world__load_client__initialize__sets_client_uuid),
    INCLUDE_TEST__STATELESS(game_action__world__load_client__register__populates_table),
    END_TESTS)
