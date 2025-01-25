#include "scene/implemented/scene_registrar.h"
#include "scene/implemented/scene__test.h"

void register_scenes(Scene_Manager *p_scene_manager) {
    register_scene__test(p_scene_manager);
    debug_warning("register_scenes, impl.");
}
