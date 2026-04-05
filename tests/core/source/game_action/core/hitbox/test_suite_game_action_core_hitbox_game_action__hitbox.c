#include <game_action/core/hitbox/test_suite_game_action_core_hitbox_game_action__hitbox.h>

#include <game_action/core/hitbox/game_action__hitbox.c>

TEST_FUNCTION(game_action__hitbox__initialize__sets_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    Vector__3i32F4 position = {1, 2, 3};
    Vector__3i32F4 velocity = {4, 5, 6};
    Vector__3i16F8 acceleration = {7, 8, 9};

    initialize_game_action_for__hitbox(
            &ga,
            42,
            position,
            velocity,
            acceleration,
            Hitbox_Kind__AABB);

    munit_assert_int(
            get_kind_of__game_action(&ga),
            ==,
            Game_Action_Kind__Hitbox);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__hitbox__initialize__sets_target_uuid) {
    Game_Action ga;
    initialize_game_action(&ga);

    Vector__3i32F4 position = {0, 0, 0};
    Vector__3i32F4 velocity = {0, 0, 0};
    Vector__3i16F8 acceleration = {0, 0, 0};

    initialize_game_action_for__hitbox(
            &ga,
            12345,
            position,
            velocity,
            acceleration,
            Hitbox_Kind__AABB);

    munit_assert_uint32(
            ga.ga_kind__hitbox__uuid_of__target,
            ==,
            12345);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__hitbox__initialize__sets_position) {
    Game_Action ga;
    initialize_game_action(&ga);

    Vector__3i32F4 position = {100, 200, 300};
    Vector__3i32F4 velocity = {0, 0, 0};
    Vector__3i16F8 acceleration = {0, 0, 0};

    initialize_game_action_for__hitbox(
            &ga,
            1,
            position,
            velocity,
            acceleration,
            Hitbox_Kind__AABB);

    munit_assert_int32(
            ga.ga_kind__hitbox__position__3i32F4.x__i32F4,
            ==,
            100);
    munit_assert_int32(
            ga.ga_kind__hitbox__position__3i32F4.y__i32F4,
            ==,
            200);
    munit_assert_int32(
            ga.ga_kind__hitbox__position__3i32F4.z__i32F4,
            ==,
            300);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__hitbox__initialize__sets_velocity) {
    Game_Action ga;
    initialize_game_action(&ga);

    Vector__3i32F4 position = {0, 0, 0};
    Vector__3i32F4 velocity = {10, 20, 30};
    Vector__3i16F8 acceleration = {0, 0, 0};

    initialize_game_action_for__hitbox(
            &ga,
            1,
            position,
            velocity,
            acceleration,
            Hitbox_Kind__AABB);

    munit_assert_int32(
            ga.ga_kind__hitbox__velocity__3i32F4.x__i32F4,
            ==,
            10);
    munit_assert_int32(
            ga.ga_kind__hitbox__velocity__3i32F4.y__i32F4,
            ==,
            20);
    munit_assert_int32(
            ga.ga_kind__hitbox__velocity__3i32F4.z__i32F4,
            ==,
            30);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__hitbox__initialize__sets_hitbox_kind) {
    Game_Action ga;
    initialize_game_action(&ga);

    Vector__3i32F4 position = {0, 0, 0};
    Vector__3i32F4 velocity = {0, 0, 0};
    Vector__3i16F8 acceleration = {0, 0, 0};

    initialize_game_action_for__hitbox(
            &ga,
            1,
            position,
            velocity,
            acceleration,
            Hitbox_Kind__AABB);

    munit_assert_int(
            ga.ga_kind__hitbox__the_kind_of__hitbox,
            ==,
            Hitbox_Kind__AABB);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action__hitbox__register_for_server__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__hitbox_for__server(&table);

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

TEST_FUNCTION(game_action__hitbox__register_for_offline__populates_table) {
    Game_Action_Logic_Table table;
    initialize_game_action_logic_table(&table);

    register_game_action__hitbox_for__offline(&table);

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

DEFINE_SUITE(game_action__hitbox,
    INCLUDE_TEST__STATELESS(game_action__hitbox__initialize__sets_kind),
    INCLUDE_TEST__STATELESS(game_action__hitbox__initialize__sets_target_uuid),
    INCLUDE_TEST__STATELESS(game_action__hitbox__initialize__sets_position),
    INCLUDE_TEST__STATELESS(game_action__hitbox__initialize__sets_velocity),
    INCLUDE_TEST__STATELESS(game_action__hitbox__initialize__sets_hitbox_kind),
    INCLUDE_TEST__STATELESS(game_action__hitbox__register_for_server__populates_table),
    INCLUDE_TEST__STATELESS(game_action__hitbox__register_for_offline__populates_table),
    END_TESTS)
