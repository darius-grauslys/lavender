#include <scene/test_suite_scene_scene_manager.h>

#include <scene/scene_manager.c>

static bool test__load_called = false;
static bool test__enter_called = false;
static bool test__unload_called = false;

static void test__m_load_scene(Scene *p_this_scene, Game *p_game) {
    (void)p_this_scene;
    (void)p_game;
    test__load_called = true;
}

static void test__m_enter_scene(Scene *p_this_scene, Game *p_game) {
    (void)p_this_scene;
    (void)p_game;
    test__enter_called = true;
}

static void test__m_unload_scene(Scene *p_this_scene, Game *p_game) {
    (void)p_this_scene;
    (void)p_game;
    test__unload_called = true;
}

static void reset_test_flags(void) {
    test__load_called = false;
    test__enter_called = false;
    test__unload_called = false;
}

TEST_FUNCTION(initialize_scene_manager__sets_active_scene_to_null) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    Scene *p_active =
        get_p_active_scene_from__scene_manager(&scene_manager);

    munit_assert_ptr_null(p_active);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_scene_manager__all_scenes_invalid) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    for (int i = 0; i < Scene_Kind__Unknown; i++) {
        Scene *p_scene =
            get_p_scene_from__scene_manager(&scene_manager, (Scene_Kind)i);
        munit_assert_false(is_scene__valid(p_scene));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(register_scene__makes_scene_valid) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    Scene *p_scene =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_true(is_scene__valid(p_scene));

    return MUNIT_OK;
}

TEST_FUNCTION(register_scene__stores_all_handlers) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    Scene *p_scene =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_ptr_not_null(p_scene->m_load_scene_handler);
    munit_assert_ptr_not_null(p_scene->m_enter_scene_handler);
    munit_assert_ptr_not_null(p_scene->m_unload_scene_handler);

    return MUNIT_OK;
}

TEST_FUNCTION(register_scene__overwrites_previous_registration) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            0,
            test__m_enter_scene,
            0);

    Scene *p_scene =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_ptr_null(p_scene->m_load_scene_handler);
    munit_assert_ptr_not_null(p_scene->m_enter_scene_handler);
    munit_assert_ptr_null(p_scene->m_unload_scene_handler);

    return MUNIT_OK;
}

TEST_FUNCTION(set_active_scene__calls_load_handler) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    reset_test_flags();

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    set_active_scene_for__scene_manager(
            &scene_manager,
            Scene_Kind__None);

    munit_assert_true(test__load_called);

    return MUNIT_OK;
}

TEST_FUNCTION(set_active_scene__sets_active_scene_pointer) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    reset_test_flags();

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    set_active_scene_for__scene_manager(
            &scene_manager,
            Scene_Kind__None);

    Scene *p_active =
        get_p_active_scene_from__scene_manager(&scene_manager);
    Scene *p_expected =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_ptr_equal(p_active, p_expected);

    return MUNIT_OK;
}

TEST_FUNCTION(set_active_scene__is_detected_as_active) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    reset_test_flags();

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    set_active_scene_for__scene_manager(
            &scene_manager,
            Scene_Kind__None);

    Scene *p_scene =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_true(
            is_p_scene_the__active_scene_in__scene_manager(
                &scene_manager, p_scene));

    return MUNIT_OK;
}

TEST_FUNCTION(quit_scene_state_machine__sets_active_to_null) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    reset_test_flags();

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    set_active_scene_for__scene_manager(
            &scene_manager,
            Scene_Kind__None);

    reset_test_flags();

    quit_scene_state_machine(&scene_manager);

    Scene *p_active =
        get_p_active_scene_from__scene_manager(&scene_manager);

    munit_assert_ptr_null(p_active);

    return MUNIT_OK;
}

TEST_FUNCTION(quit_scene_state_machine__calls_unload_handler) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);
    reset_test_flags();

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            test__m_load_scene,
            test__m_enter_scene,
            test__m_unload_scene);

    set_active_scene_for__scene_manager(
            &scene_manager,
            Scene_Kind__None);

    reset_test_flags();

    quit_scene_state_machine(&scene_manager);

    munit_assert_true(test__unload_called);

    return MUNIT_OK;
}

TEST_FUNCTION(quit_scene_state_machine__no_crash_when_no_active_scene) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    quit_scene_state_machine(&scene_manager);

    Scene *p_active =
        get_p_active_scene_from__scene_manager(&scene_manager);

    munit_assert_ptr_null(p_active);

    return MUNIT_OK;
}

TEST_FUNCTION(get_p_scene_from__scene_manager__returns_correct_slot) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    Scene *p_scene_none =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_ptr_not_null(p_scene_none);
    munit_assert_ptr_equal(p_scene_none, &scene_manager.scenes[Scene_Kind__None]);

    return MUNIT_OK;
}

TEST_FUNCTION(register_scene__with_null_load_and_unload__still_valid) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scene_into__scene_manager(
            &scene_manager,
            Scene_Kind__None,
            0,
            test__m_enter_scene,
            0);

    Scene *p_scene =
        get_p_scene_from__scene_manager(&scene_manager, Scene_Kind__None);

    munit_assert_true(is_scene__valid(p_scene));
    munit_assert_ptr_null(p_scene->m_load_scene_handler);
    munit_assert_ptr_null(p_scene->m_unload_scene_handler);

    return MUNIT_OK;
}

DEFINE_SUITE(scene_manager,
    INCLUDE_TEST__STATELESS(initialize_scene_manager__sets_active_scene_to_null),
    INCLUDE_TEST__STATELESS(initialize_scene_manager__all_scenes_invalid),
    INCLUDE_TEST__STATELESS(register_scene__makes_scene_valid),
    INCLUDE_TEST__STATELESS(register_scene__stores_all_handlers),
    INCLUDE_TEST__STATELESS(register_scene__overwrites_previous_registration),
    INCLUDE_TEST__STATELESS(set_active_scene__calls_load_handler),
    INCLUDE_TEST__STATELESS(set_active_scene__sets_active_scene_pointer),
    INCLUDE_TEST__STATELESS(set_active_scene__is_detected_as_active),
    INCLUDE_TEST__STATELESS(quit_scene_state_machine__sets_active_to_null),
    INCLUDE_TEST__STATELESS(quit_scene_state_machine__calls_unload_handler),
    INCLUDE_TEST__STATELESS(quit_scene_state_machine__no_crash_when_no_active_scene),
    INCLUDE_TEST__STATELESS(get_p_scene_from__scene_manager__returns_correct_slot),
    INCLUDE_TEST__STATELESS(register_scene__with_null_load_and_unload__still_valid),
    END_TESTS)
