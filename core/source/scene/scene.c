#include "debug/debug.h"
#include "defines_weak.h"
#include "input/input.h"
#include "ui/ui_element.h"
#include <scene/scene.h>
#include <game.h>

void initialize_scene(Scene* scene) {
    scene->m_enter_scene_handler = 0;
    scene->m_load_scene_handler = 0;
    scene->m_unload_scene_handler = 0;
    scene->p_parent_scene = 0;
    scene->scene__identifier_u16 = IDENTIFIER__UNKNOWN__u16;
    scene->p_scene_data = 0;
    scene->is_active = false;
}
