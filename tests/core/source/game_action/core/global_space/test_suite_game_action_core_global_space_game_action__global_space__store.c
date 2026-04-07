#include <game_action/core/global_space/test_suite_game_action_core_global_space_game_action__global_space__store.h>

#include <game_action/core/global_space/game_action__global_space__store.c>

/**
 * Spec: docs/specs/core/game_action/global_space/game_action__global_space__store.h.spec.md
 * Section: 1.5.2. Initialization
 *
 * Verifies that initialize_game_action_for__global_space__store sets the
 * game action kind to Game_Action_Kind__Global_Space__Store.
 */
TEST_FUNCTION(game_action__global_space__store__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    Global_Space_Vector__3i32 gsv = {3, 7, 11};

    initialize_game_action_for__global_space__store(
            &ga,
            gsv);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Global_Space__Store);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/game_action/global_space/game_action__global_space__store.h.spec.md
 * Section: 1.4. Payload Fields
 *
 * Verifies that initialize_game_action_for__global_space__store correctly
 * stores the provided Global_Space_Vector__3i32 coordinates into the
 * ga_kind__global_space__store__gsv__3i32 payload field.
 */
TEST_FUNCTION(game_action__global_space__store__initialize__sets_coordinates) {
    Game_Action ga;
    initialize_game_action(&ga);

    Global_Space_Vector__3i32 gsv = {-5, 100, 0};

    initialize_game_action_for__global_space__store(
            &ga,
            gsv);

    munit_assert_int32(
            ga.ga_kind__global_space__store__gsv__3i32.x__i32,
            ==,
            -5);
    munit_assert_int32(
            ga.ga_kind__global_space__store__gsv__3i32.y__i32,
            ==,
            100);
    munit_assert_int32(
            ga.ga_kind__global_space__store__gsv__3i32.z__i32,
            ==,
            0);

    return MUNIT_OK;
}

/**
 * Spec: docs/specs/core/game_action/global_space/game_action__global_space__store.h.spec.md
 * Section: 1.5.1. Registration
 *
 * Verifies that register_game_action__global_space__store populates the
 * Game_Action_Logic_Table with a valid entry for
 * Game_Action_Kind__Global_Space__Store.
 */
TEST_FUNCTION(game_action__global_space__store__register__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__global_space__store(&table);

    Game_Action_Logic_Entry *p_entry =
        get_p_game_action_logic_entry_by__game_action_kind(
                &table,
                Game_Action_Kind__Global_Space__Store);

    munit_assert_ptr_not_null(p_entry);

    return MUNIT_OK;
}

DEFINE_SUITE(game_action__global_space__store,
    INCLUDE_TEST__STATELESS(game_action__global_space__store__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__global_space__store__initialize__sets_coordinates),
    INCLUDE_TEST__STATELESS(game_action__global_space__store__register__populates_table),
    END_TESTS)
