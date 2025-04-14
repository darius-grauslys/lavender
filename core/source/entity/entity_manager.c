#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "timer.h"
#include <entity/entity_manager.h>
#include <entity/entity.h>
#include <debug/debug.h>

void initialize_entity_manager(Entity_Manager *entity_manager) {
    entity_manager->entity_count__quantity_u32 = 0;
    for (uint32_t i=0;i<ENTITY_MAXIMUM_QUANTITY_OF;i++) {
        Entity *p_entity =
            &entity_manager->entities[i];
        initialize_entity(
                p_entity,
                Entity_Kind__None);
        p_entity->_serialization_header.uuid =
            IDENTIFIER__UNKNOWN__u32;
    }
    initialize_repeatable_psuedo_random(
            &entity_manager->randomizer, 
            (u32)(uint64_t)entity_manager);
}

Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        Entity_Manager* entity_manager,
        enum Entity_Kind kind_of_entity,
        Vector__3i32F4 position__3i32F4,
        Graphics_Window 
            *p_graphics_window) {
    // TODO: do better than bellow:
    switch (kind_of_entity) {
        default:
            debug_abort("allocate__entity, unhandled entity_kind %d.",
                    kind_of_entity);
            debug_warning("Did you forget to include your new entity kind within entity_manager.c, allocate__entity?");
            return 0;
    }

    Identifier__u32 uuid__u32 =
        get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header*)entity_manager->entities, 
                ENTITY_MAXIMUM_QUANTITY_OF, 
                &entity_manager->randomizer);

    Entity *p_entity =
        (Entity*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)entity_manager->entities, 
                ENTITY_MAXIMUM_QUANTITY_OF, 
                uuid__u32);
    
    if (!p_entity) {
        debug_error("allocate__entity, failed to allocate new entity.");
        debug_warning("Is the entity limit reached?");
        return 0;
    }

    p_entity->_serialization_header.uuid = uuid__u32;

    entity_manager->entity_count__quantity_u32++;
    
    return p_entity;
}

void release_entity_from__entity_manager(
        Entity_Manager *p_entity_manager, 
        Entity *p_entity) {
    if (p_entity_manager->entity_count__quantity_u32 > 0)
        p_entity_manager->entity_count__quantity_u32--;
    initialize_entity(
            p_entity,
            Entity_Kind__None);
    initialize_serialization_header_for__deallocated_struct(
            &p_entity->_serialization_header, 
            sizeof(Entity));
}

bool resolve_p_serialized_entity_ptr_with__entity_manager(
        Entity_Manager *p_entity_manager,
        Serialized_Entity_Ptr *s_entity_ptr) {
    if (is_p_serialized_field__linked(
                s_entity_ptr)
            && s_entity_ptr->p_serialized_field__entity
            - p_entity_manager->entities
            < ENTITY_MAXIMUM_QUANTITY_OF
            && s_entity_ptr->p_serialized_field__entity
            - p_entity_manager->entities
            >= 0)
        return true;
    return link_serialized_field_against__contiguous_array(
            s_entity_ptr, 
            (Serialization_Header*)p_entity_manager->entities, 
            ENTITY_MAXIMUM_QUANTITY_OF);
}
