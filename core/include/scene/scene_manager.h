#ifndef SCENE_MANAGER_H
#define SCENE_MANAGER_H

#include "defines_weak.h"
#include <defines.h>

void initialize_scene_manager(
        Scene_Manager *p_scene_manager);

void register_scene_into__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of_scene_to__register,
        m_Load_Scene m_load_scene,
        m_Enter_Scene m_enter_scene,
        m_Unload_Scene m_unload_scene);

Scene *get_p_scene_from__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of__scene);

void set_p_active_scene_for__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene_Kind the_kind_of__scene);

void quit_scene_state_machine(Scene_Manager *p_scene_manager);

static inline 
Scene *get_p_active_scene_from__scene_manager(
        Scene_Manager *p_scene_manager) {
    return p_scene_manager->p_active_scene;
}

static inline
bool is_p_scene_the__active_scene_in__scene_manager(
        Scene_Manager *p_scene_manager,
        Scene *p_scene) {
    return p_scene
        == get_p_active_scene_from__scene_manager(
                p_scene_manager);
}

#endif
