#include <scene/implemented/test_suite_scene_implemented_scene_registrar.h>

#include <scene/implemented/scene_registrar.c>
#include <scene/scene_manager.h>

TEST_FUNCTION(register_scenes__does_not_crash_on_initialized_manager) {
    Scene_Manager scene_manager;
    initialize_scene_manager(&scene_manager);

    register_scenes(&scene_manager);

    return MUNIT_OK;
}

DEFINE_SUITE(scene_registrar,
    INCLUDE_TEST__STATELESS(register_scenes__does_not_crash_on_initialized_manager),
    END_TESTS)
