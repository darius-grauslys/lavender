#ifndef ENTITY_H
#define ENTITY_H

#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include <defines.h>

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity);

void serialize_entity(
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity);

void deserialize_entity(
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity);

static inline
bool is_entity__allocated(
        Entity *p_entity) {
    return !is_serialized_struct__deallocated(
            &p_entity->_serialization_header);
}

static inline
bool is_entity__enabled(
        Entity *p_entity) {
    return p_entity->entity_flags & ENTITY_FLAG__IS_ENABLED;
}

static inline
void set_entity_as__enabled(Entity *p_entity) {
    p_entity->entity_flags |=
        ENTITY_FLAG__IS_ENABLED;
}

static inline
void set_entity_as__disabled(Entity *p_entity) {
    p_entity->entity_flags &=
        ~ENTITY_FLAG__IS_ENABLED;
}

static inline
Entity_Kind get_kind_of__entity(
        Entity *p_entity) {
    return p_entity->entity_data.the_kind_of__entity;
}

#endif
