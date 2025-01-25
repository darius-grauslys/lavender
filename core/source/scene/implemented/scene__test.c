#include "scene/implemented/scene__test.h"
#include "defines_weak.h"
#include "game.h"
#include "scene/scene_manager.h"

void m_load_scene__test(
        Scene *p_this_scene,
        Game *p_game);
void m_enter_scene__test(
        Scene *p_this_scene,
        Game *p_game);

void register_scene__test(Scene_Manager *p_scene_manager) {
    register_scene_into__scene_manager(
            p_scene_manager, 
            Scene_Kind__Test, 
            m_load_scene__test, 
            m_enter_scene__test, 
            0);
}

void m_load_scene__test(
        Scene *p_this_scene,
        Game *p_game) {
    
}

void m_enter_scene__test(
        Scene *p_this_scene,
        Game *p_game) {
    Scene_Manager *p_scene_manager =
        get_p_scene_manager_from__game(p_game);

    while (
            is_p_scene_the__active_scene_in__scene_manager(
                p_scene_manager, 
                p_this_scene)) {
        manage_game__pre_render(p_game);
        manage_game__post_render(p_game);
    }
}

void m_unload_scene__test(
        Scene *p_this_scene,
        Game *p_game) {

}
