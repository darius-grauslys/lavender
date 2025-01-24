#include "defines.h"
#include "serialization/serialization_header.h"

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity) {
    memset(p_entity, 0, sizeof(Entity));
    initialize_serialization_header(
            &p_entity->_serialization_header,
            p_entity->_serialization_header.uuid,
            sizeof(Entity));
}

