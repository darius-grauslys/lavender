#include <game_action/core/entity/test_suite_game_action_core_entity_game_action__entity__spawn.h>

#include <game_action/core/entity/game_action__entity__spawn.c>

///
/// Spec: core/game_action/entity/game_action__entity__spawn.h.spec.md
/// Section: 1.3. Game_Action_Kind
///
TEST_FUNCTION(game_action__entity__spawn__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__entity__spawn(
            &ga,
            42,
            Entity_Kind__Unknown);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Entity__Spawn);

    return MUNIT_OK;
}

///
/// Spec: core/game_action/entity/game_action__entity__spawn.h.spec.md
/// Section: 1.4. Payload Fields
///
TEST_FUNCTION(game_action__entity__spawn__initialize__sets_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__entity__spawn(
            &ga,
            12345,
            Entity_Kind__Unknown);

    munit_assert_uint32(
            ga.ga_kind__entity__uuid,
            ==,
            12345);

    return MUNIT_OK;
}

///
/// Spec: core/game_action/entity/game_action__entity__spawn.h.spec.md
/// Section: 1.4. Payload Fields
///
TEST_FUNCTION(game_action__entity__spawn__initialize__sets_entity_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    initialize_game_action_for__entity__spawn(
            &ga,
            1,
            Entity_Kind__Unknown);

    munit_assert_int(
            ga.ga_kind__entity__the_kind_of__entity,
            ==,
            Entity_Kind__Unknown);

    return MUNIT_OK;
}

///
/// Spec: core/game_action/entity/game_action__entity__spawn.h.spec.md
/// Section: 1.5.1. Registration
///
TEST_FUNCTION(game_action__entity__spawn__register_for_server__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__entity__spawn_for__server(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

///
/// Spec: core/game_action/entity/game_action__entity__spawn.h.spec.md
/// Section: 1.5.1. Registration
///
TEST_FUNCTION(game_action__entity__spawn__register_for_client__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__entity__spawn_for__client(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Entity__Spawn);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__entity__spawn,
    INCLUDE_TEST__STATELESS(game_action__entity__spawn__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__entity__spawn__initialize__sets_uuid),
    INCLUDE_TEST__STATELESS(game_action__entity__spawn__initialize__sets_entity_kind),
    INCLUDE_TEST__STATELESS(game_action__entity__spawn__register_for_server__populates_table),
    INCLUDE_TEST__STATELESS(game_action__entity__spawn__register_for_client__populates_table),
    END_TESTS)
