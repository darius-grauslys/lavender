#ifndef SCENE_H
#define SCENE_H

#include <defines.h>

void initialize_scene(Scene* scene);

static inline
bool is_scene__valid(Scene *p_scene) {
    return p_scene->m_enter_scene_handler;
}

#endif
