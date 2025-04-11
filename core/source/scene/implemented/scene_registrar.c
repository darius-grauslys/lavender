#include "scene/implemented/scene_registrar.h"
#include "scene/implemented/scene__main.h"

void register_scenes(Scene_Manager *p_scene_manager) {
    register_scene__main(p_scene_manager);
}
