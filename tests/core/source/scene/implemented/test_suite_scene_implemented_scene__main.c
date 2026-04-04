#include <scene/implemented/test_suite_scene_implemented_scene__main.h>

#include <scene/implemented/scene__main.c>

TEST_FUNCTION(register_scene__main__does_not_crash_on_initialized_manager) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scene__main(&scene_manager);

    return MUNIT_OK;
}

DEFINE_SUITE(scene__main,
    INCLUDE_TEST__STATELESS(register_scene__main__does_not_crash_on_initialized_manager),
    END_TESTS)
