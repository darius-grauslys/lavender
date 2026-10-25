#ifndef ENTITY__DUMMY_H
#define ENTITY__DUMMY_H

#include "defines.h"
#include "entity/entity.h"

void m_entity_handler__update_dummy(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world);

void register_entity_dummy_into__entity_manager(
        Entity_Manager *p_entity_manager);

#endif
