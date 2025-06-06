#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/implemented/entity_registrar.h"
#include "platform_defines.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "timer.h"
#include "types/implemented/entity_functions.h"
#include "types/implemented/entity_kind.h"
#include <entity/entity_manager.h>
#include <entity/entity.h>
#include <debug/debug.h>

void f_entity_initializer__default(
        Game *p_game,
        World *p_world,
        Entity *p_entity) {
    memset((u8*)(p_entity) + sizeof(Serialization_Header),
            0,
            sizeof(Entity) - sizeof(Serialization_Header));
    p_entity->entity_functions.m_entity_dispose_handler =
        m_entity_dispose_handler__default;
    p_entity->entity_functions.m_entity_deserialize_handler =
        m_entity_deserialization_handler__default;
    p_entity->entity_functions.m_entity_serialize_handler =
        m_entity_serialization_handler__default;
}

void initialize_entity_manager(Entity_Manager *p_entity_manager) {
#ifndef NDEBUG
    if (!p_entity_manager) {
        debug_error("initialize_entity_manager, p_entity_manager == 0.");
        return;
    }
#endif
    memset(p_entity_manager,
            0,
            sizeof(Entity_Manager));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_entity_manager->entities, 
            MAX_QUANTITY_OF__ENTITIES, 
            sizeof(Entity));
    initialize_repeatable_psuedo_random(
            &p_entity_manager->randomizer, 
            (u32)(uint64_t)p_entity_manager);

    p_entity_manager->p_ptr_entity__next_in_ptr_array =
        p_entity_manager->ptr_array_of__entities;

    p_entity_manager->f_entity_initializer =
        f_entity_initializer__default;

    register_entities(p_entity_manager);
}

void register_entity_into__entity_manager(
        Entity_Manager *p_entity_manager,
        Entity_Kind the_kind_of__entity,
        Entity_Functions entity_functions) {
#ifndef NDEBUG
    if (!p_entity_manager) {
        debug_error("register_f_entity_initializer_into__entity_manager, p_entity_manager == 0.");
        return;
    }
    if (the_kind_of__entity >= Entity_Kind__Unknown) {
        debug_error("register_f_entity_initializer_into__entity_manager, the_kind_of__entity >= Entity_Kind__Unknown.");
        return;
    }
#endif

    p_entity_manager->entity_functions[
        the_kind_of__entity] = entity_functions;
}

void sanitize_entity_functions(
        Entity_Manager *p_entity_manager,
        Entity *p_entity) {

    Entity_Functions *p_entity_functions =
        &p_entity_manager->entity_functions[
        p_entity->entity_data.the_kind_of__entity];

    for (Index__u32 index_of__function_pointer = 0;
            index_of__function_pointer
            < sizeof(Entity_Functions) / sizeof(void*);
            index_of__function_pointer++) {
        void *p_function_ptr =
            ((void**)p_entity_functions)[index_of__function_pointer];
        if (!p_function_ptr)
            continue;
        ((void**)&p_entity->entity_functions)[index_of__function_pointer] =
            p_function_ptr;
    }
}

///
/// Create a new entity instance within the entity_manager object pool.
/// Return nullptr (0) if fails to get new entity.
///
Entity *allocate_entity_with__this_uuid_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity,
        Identifier__u32 uuid__u32) {
    // TODO: do better on this condition check.
    if (!p_entity_manager || !p_entity_manager->entities->_serialization_header.size_of__struct) {
        debug_error("allocate_entity_with__this_uuid_in__entity_manager, p_entity_manager is not initialized.");
        return 0;
    }
    Entity *p_entity =
        (Entity*)allocate_serialization_header_with__this_uuid(
                (Serialization_Header*)p_entity_manager->entities, 
                MAX_QUANTITY_OF__ENTITIES,
                uuid__u32);
    
    if (!p_entity) {
        debug_error("allocate__entity, failed to allocate new entity.");
        debug_warning("Is the entity limit reached?");
        return 0;
    }

    if (p_entity_manager->f_entity_initializer) {
        p_entity_manager->f_entity_initializer(
                p_game,
                p_world,
                p_entity);
    }

    p_entity->entity_data.the_kind_of__entity =
        kind_of_entity;

    sanitize_entity_functions(
            p_entity_manager, 
            p_entity);

    set_entity_as__enabled(p_entity);
    *p_entity_manager->p_ptr_entity__next_in_ptr_array =
        p_entity;
    p_entity_manager->p_ptr_entity__next_in_ptr_array++;
    
    return p_entity;
}

Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity) {
    Entity *p_entity =
        (Entity*)allocate_serialization_header_with__uuid_branding(
                (Serialization_Header*)p_entity_manager->entities, 
                MAX_QUANTITY_OF__ENTITIES,
                &p_entity_manager->randomizer,
                Lavender_Type__Entity);
    
    if (!p_entity) {
        debug_error("allocate__entity, failed to allocate new entity.");
        debug_warning("Is the entity limit reached?");
        return 0;
    }

    if (p_entity_manager->f_entity_initializer) {
        p_entity_manager->f_entity_initializer(
                p_game,
                p_world,
                p_entity);
    }

    p_entity->entity_data.the_kind_of__entity =
        kind_of_entity;

    sanitize_entity_functions(
            p_entity_manager, 
            p_entity);

    set_entity_as__enabled(p_entity);
    *p_entity_manager->p_ptr_entity__next_in_ptr_array =
        p_entity;
    p_entity_manager->p_ptr_entity__next_in_ptr_array++;
    
    return p_entity;
}

void release_entity_from__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager, 
        Entity *p_entity) {
    if (p_entity->entity_functions.m_entity_dispose_handler) {
        p_entity->entity_functions.m_entity_dispose_handler(
                p_entity,
                p_game,
                p_world);
    }
    initialize_entity(
            p_entity,
            Entity_Kind__None);
    initialize_serialization_header_for__deallocated_struct(
            &p_entity->_serialization_header, 
            sizeof(Entity));

    for (Index__u32 index_of__entity = 0;
            index_of__entity
            < MAX_QUANTITY_OF__ENTITIES;
            index_of__entity++) {
        if (p_entity
                != p_entity_manager->ptr_array_of__entities[index_of__entity]) {
            continue;
        }

        p_entity_manager->p_ptr_entity__next_in_ptr_array--;
        p_entity_manager->ptr_array_of__entities[index_of__entity] =
            *p_entity_manager->p_ptr_entity__next_in_ptr_array;
        *p_entity_manager->p_ptr_entity__next_in_ptr_array = 0;
        break;
    }
}
