#include "scene/implemented/scene__main.h"
#include "defines.h"
#include "scene/scene.h"
#include "scene/scene_manager.h"
#include "game.h"

void m_load_scene_as__main_handler(
        Scene *p_this_scene,
        Game *p_game) {
}

void m_enter_scene_as__main_handler(
        Scene *p_this_scene,
        Game *p_game) {
    while (poll_is__scene_active(
                p_game, 
                p_this_scene)) {
        while(!poll__game_tick_timer(p_game));
        manage_game__pre_render(p_game);
        manage_game__post_render(p_game);
    }
}

void register_scene__main(Scene_Manager *p_scene_manager) {
    register_scene_into__scene_manager(
            p_scene_manager, 
            Scene_Kind__None, 
            m_load_scene_as__main_handler, 
            m_enter_scene_as__main_handler, 
            0);
}
