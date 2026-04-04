#include <game_action/test_suite_game_action_game_action_manager.h>

#include <game_action/game_action_manager.c>

TEST_FUNCTION(game_action_manager__initialize__all_slots_deallocated) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    for (Quantity__u32 i = 0;
            i < MAX_QUANTITY_OF__GAME_ACTIONS; i++) {
        munit_assert_false(
                is_game_action__allocated(
                    &manager.game_actions[i]));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__allocate__returns_non_null) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Game_Action *p_ga =
        allocate_game_action_from__game_action_manager(
                &manager);

    munit_assert_ptr_not_null(p_ga);
    munit_assert_true(is_game_action__allocated(p_ga));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__allocate_with_uuid__returns_non_null) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Identifier__u32 uuid = 12345;
    Game_Action *p_ga =
        allocate_game_action_with__this_uuid_from__game_action_manager(
                &manager,
                uuid);

    munit_assert_ptr_not_null(p_ga);
    munit_assert_true(is_game_action__allocated(p_ga));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__release__deallocates) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Game_Action *p_ga =
        allocate_game_action_from__game_action_manager(
                &manager);

    munit_assert_ptr_not_null(p_ga);
    munit_assert_true(is_game_action__allocated(p_ga));

    bool result =
        release_game_action_from__game_action_manager(
                &manager,
                p_ga);

    munit_assert_true(result);
    munit_assert_false(is_game_action__allocated(p_ga));

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__allocate_copy__copies_kind) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Game_Action source;
    initialize_game_action(&source);
    set_the_kind_of__game_action(&source,
            Game_Action_Kind__Bad_Request);

    Game_Action *p_ga =
        allocate_as__copy_of__game_action_from__game_action_manager(
                &manager,
                &source);

    munit_assert_ptr_not_null(p_ga);
    munit_assert_true(is_game_action__allocated(p_ga));
    munit_assert_int(
            get_kind_of__game_action(p_ga),
            ==,
            Game_Action_Kind__Bad_Request);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__multiple_allocations__return_different_ptrs) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Game_Action *p_ga_1 =
        allocate_game_action_from__game_action_manager(
                &manager);
    Game_Action *p_ga_2 =
        allocate_game_action_from__game_action_manager(
                &manager);

    munit_assert_ptr_not_null(p_ga_1);
    munit_assert_ptr_not_null(p_ga_2);
    munit_assert_ptr_not_equal(p_ga_1, p_ga_2);

    return MUNIT_OK;
}

TEST_FUNCTION(game_action_manager__release_and_reallocate__succeeds) {
    Game_Action_Manager manager;
    initialize_game_action_manager(&manager);

    Game_Action *p_ga =
        allocate_game_action_from__game_action_manager(
                &manager);

    munit_assert_ptr_not_null(p_ga);

    release_game_action_from__game_action_manager(
            &manager,
            p_ga);

    Game_Action *p_ga_2 =
        allocate_game_action_from__game_action_manager(
                &manager);

    munit_assert_ptr_not_null(p_ga_2);
    munit_assert_true(is_game_action__allocated(p_ga_2));

    return MUNIT_OK;
}

DEFINE_SUITE(game_action_manager,
    INCLUDE_TEST__STATELESS(game_action_manager__initialize__all_slots_deallocated),
    INCLUDE_TEST__STATELESS(game_action_manager__allocate__returns_non_null),
    INCLUDE_TEST__STATELESS(game_action_manager__allocate_with_uuid__returns_non_null),
    INCLUDE_TEST__STATELESS(game_action_manager__release__deallocates),
    INCLUDE_TEST__STATELESS(game_action_manager__allocate_copy__copies_kind),
    INCLUDE_TEST__STATELESS(game_action_manager__multiple_allocations__return_different_ptrs),
    INCLUDE_TEST__STATELESS(game_action_manager__release_and_reallocate__succeeds),
    END_TESTS)
