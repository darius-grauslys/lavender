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
#include "types/implemented/entity_kind.h"
#include <entity/entity_manager.h>
#include <entity/entity.h>
#include <debug/debug.h>

static inline
f_Entity_Initializer get_f_entity_initializer_by__kind_from__entity_manager(
        Entity_Manager *p_entity_manager, 
        Entity_Kind the_kind_of__entity) {
#ifndef NDEBUG
    if (the_kind_of__entity >= Entity_Kind__Unknown) {
        debug_error("get_f_entity_initializer_by__kind_from__entity_manager, the_kind_of__entity >= Entity_Kind__Unknown.");
        return 0;
    }
#endif
    return p_entity_manager->F_entity_initializer_table[
        the_kind_of__entity];
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

    register_entities(p_entity_manager);
}

void register_entity_into__entity_manager(
        Entity_Manager *p_entity_manager,
        Entity_Kind the_kind_of__entity,
        Entity_Functions entity_functions,
        f_Entity_Initializer f_entity_initializer) {
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

    p_entity_manager->F_entity_initializer_table[
        the_kind_of__entity] = f_entity_initializer;
    p_entity_manager->entity_functions[
        the_kind_of__entity] = entity_functions;
}

Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity,
        Vector__3i32F4 position__3i32F4) {
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

    f_Entity_Initializer f_entity_initializer =
        get_f_entity_initializer_by__kind_from__entity_manager(
                p_entity_manager, 
                kind_of_entity);

    if (f_entity_initializer) {
        f_entity_initializer(
                p_game,
                p_world,
                p_entity,
                position__3i32F4);
    }

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
    if (p_entity->p_const_entity_functions->m_entity_dispose_handler) {
        p_entity->p_const_entity_functions->m_entity_dispose_handler(
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
