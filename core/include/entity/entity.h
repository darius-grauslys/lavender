#ifndef ENTITY_H
#define ENTITY_H

#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include <defines.h>

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity);

PLATFORM_Write_File_Error serialize_entity(
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity);

PLATFORM_Read_File_Error deserialize_entity(
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
    return p_entity->entity_data.entity_flags & ENTITY_FLAG__IS_ENABLED;
}

static inline
void set_entity_as__enabled(Entity *p_entity) {
    p_entity->entity_data.entity_flags |=
        ENTITY_FLAG__IS_ENABLED;
}

static inline
bool is_entity__serialized_with__hitbox(
        Entity *p_entity) {
    return p_entity->entity_data.entity_flags
        & ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION;
}

static inline
bool is_entity__serialized_with__inventory(
        Entity *p_entity) {
    return p_entity->entity_data.entity_flags
        & ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION;
}

static inline
void set_entity_as__disabled(Entity *p_entity) {
    p_entity->entity_data.entity_flags &=
        ~ENTITY_FLAG__IS_ENABLED;
}

static inline
Entity_Kind get_kind_of__entity(
        Entity *p_entity) {
    return p_entity->entity_data.the_kind_of__entity;
}

static inline
void set_m_entity_update_handler_for__entity(
        Entity *p_entity,
        m_Entity_Handler m_entity_update_handler) {
    p_entity->entity_functions.m_entity_update_handler =
        m_entity_update_handler;
}

#endif
