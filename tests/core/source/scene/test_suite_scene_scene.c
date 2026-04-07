#include <scene/test_suite_scene_scene.h>

#include <scene/scene.c>

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.1. Initialization
///
TEST_FUNCTION(initialize_scene__sets_handlers_to_null) {
    Scene scene;
    scene.m_load_scene_handler = (m_Load_Scene)0xDEADBEEF;
    scene.m_enter_scene_handler = (m_Enter_Scene)0xDEADBEEF;
    scene.m_unload_scene_handler = (m_Unload_Scene)0xDEADBEEF;

    initialize_scene(&scene);

    munit_assert_ptr_null(scene.m_load_scene_handler);
    munit_assert_ptr_null(scene.m_enter_scene_handler);
    munit_assert_ptr_null(scene.m_unload_scene_handler);

    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.1. Initialization
///
TEST_FUNCTION(initialize_scene__sets_scene_data_to_null) {
    Scene scene;
    scene.p_scene_data = (void*)0xDEADBEEF;

    initialize_scene(&scene);

    munit_assert_ptr_null(scene.p_scene_data);

    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.1. Initialization
///
TEST_FUNCTION(initialize_scene__sets_parent_scene_to_null) {
    Scene scene;
    scene.p_parent_scene = (Scene*)0xDEADBEEF;

    initialize_scene(&scene);

    munit_assert_ptr_null(scene.p_parent_scene);

    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.1. Initialization
///
TEST_FUNCTION(initialize_scene__sets_is_active_to_false) {
    Scene scene;
    scene.is_active = true;

    initialize_scene(&scene);

    munit_assert_false(scene.is_active);

    return MUNIT_OK;
}

static void dummy_enter_handler(Scene *p_this_scene, Game *p_game) {
    (void)p_this_scene;
    (void)p_game;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.2. Queries (static inline)
///
TEST_FUNCTION(is_scene__valid__returns_true_when_enter_handler_set) {
    Scene scene;
    initialize_scene(&scene);
    scene.m_enter_scene_handler = dummy_enter_handler;

    munit_assert_true(is_scene__valid(&scene));

    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.4.2. Queries (static inline)
///
TEST_FUNCTION(is_scene__valid__returns_false_when_enter_handler_null) {
    Scene scene;
    initialize_scene(&scene);

    munit_assert_false(is_scene__valid(&scene));

    return MUNIT_OK;
}

///
/// @spec    docs/specs/core/scene/scene.h.spec.md
/// @section 1.5.2. Validity Convention
///
TEST_FUNCTION(is_scene__valid__returns_true_even_without_load_and_unload) {
    Scene scene;
    initialize_scene(&scene);
    scene.m_enter_scene_handler = dummy_enter_handler;
    scene.m_load_scene_handler = 0;
    scene.m_unload_scene_handler = 0;

    munit_assert_true(is_scene__valid(&scene));

    return MUNIT_OK;
}

DEFINE_SUITE(scene,
    INCLUDE_TEST__STATELESS(initialize_scene__sets_handlers_to_null),
    INCLUDE_TEST__STATELESS(initialize_scene__sets_scene_data_to_null),
    INCLUDE_TEST__STATELESS(initialize_scene__sets_parent_scene_to_null),
    INCLUDE_TEST__STATELESS(initialize_scene__sets_is_active_to_false),
    INCLUDE_TEST__STATELESS(is_scene__valid__returns_true_when_enter_handler_set),
    INCLUDE_TEST__STATELESS(is_scene__valid__returns_false_when_enter_handler_null),
    INCLUDE_TEST__STATELESS(is_scene__valid__returns_true_even_without_load_and_unload),
    END_TESTS)
