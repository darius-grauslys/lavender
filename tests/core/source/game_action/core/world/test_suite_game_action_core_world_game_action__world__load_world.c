#include <game_action/core/world/test_suite_game_action_core_world_game_action__world__load_world.h>

#include <game_action/core/world/game_action__world__load_world.c>

///
/// @spec    game_action__world__load_world.h.spec.md
/// @section 1.3. Game_Action_Kind
/// @section 1.5.2. Initialization
///
TEST_FUNCTION(game_action__world__load_world__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__world__load_world(
            &ga,
            42);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__World__Load_World);

    return MUNIT_OK;
}

///
/// @spec    game_action__world__load_world.h.spec.md
/// @section 1.4. Payload Fields
/// @section 1.5.2. Initialization
///
TEST_FUNCTION(game_action__world__load_world__initialize__sets_client_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__world__load_world(
            &ga,
            12345);

    munit_assert_uint32(
            ga.ga_kind__world__load_world__uuid_of__client__u32,
            ==,
            12345);

    return MUNIT_OK;
}

///
/// @spec    game_action__world__load_world.h.spec.md
/// @section 1.5.1. Registration
///
TEST_FUNCTION(game_action__world__load_world__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__world__load_world(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__World__Load_World);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__world__load_world,
    INCLUDE_TEST__STATELESS(game_action__world__load_world__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__world__load_world__initialize__sets_client_uuid),
    INCLUDE_TEST__STATELESS(game_action__world__load_world__register__populates_table),
    END_TESTS)
