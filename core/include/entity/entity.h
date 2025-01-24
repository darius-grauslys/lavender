#ifndef ENTITY_H
#define ENTITY_H

#include "serialization/serialization_header.h"
#include <defines.h>

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity);

static inline
bool is_entity__allocated(
        Entity *p_entity) {
    return !is_serialized_struct__deallocated(
            &p_entity->_serialization_header);
}

#endif
