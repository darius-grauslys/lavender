#ifndef SCENE_H
#define SCENE_H

#include "game.h"
#include <defines.h>

void initialize_scene(Scene* scene);

static inline
bool is_scene__valid(Scene *p_scene) {
    return p_scene->m_enter_scene_handler;
}

static inline
bool poll_is__scene_active(
        Game *p_game, 
        Scene *p_scene) {
    return get_p_scene_manager_from__game(p_game)
        ->p_active_scene == p_scene;
}

#endif
