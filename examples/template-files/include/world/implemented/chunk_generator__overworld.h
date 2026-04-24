#ifndef AG__CHUNK_GENERATOR_OVERWORLD_H
#define AG__CHUNK_GENERATOR_OVERWORLD_H

#include "defines.h"

i32 get_natural_world_height_at__xy_for__overworld(
        Repeatable_Psuedo_Random *p_random,
        i32 x,
        i32 y);

void m_process__chunk_generator__overworld(
        Process *p_this_process,
        Game *p_game);

#endif
