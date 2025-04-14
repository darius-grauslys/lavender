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
    memset(p_entity_manager,
            0,
            sizeof(Entity_Manager));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_entity_manager->entities, 
            ENTITY_MAXIMUM_QUANTITY_OF, 
            sizeof(Entity));
    initialize_repeatable_psuedo_random(
            &p_entity_manager->randomizer, 
            (u32)(uint64_t)p_entity_manager);

    register_entities(p_entity_manager);
}

void register_f_entity_initializer_into__entity_manager(
        Entity_Manager *p_entity_manager,
        f_Entity_Initializer f_entity_initializer,
        Entity_Kind the_kind_of__entity) {
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
}

Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity,
        Vector__3i32F4 position__3i32F4) {
    Entity *p_entity =
        (Entity*)get_next_available__random_allocation_in__contiguous_array(
                (Serialization_Header*)p_entity_manager->entities, 
                ENTITY_MAXIMUM_QUANTITY_OF,
                &p_entity_manager->randomizer);
    
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

    p_entity_manager->entity_count__quantity_u32++;
    
    return p_entity;
}

void release_entity_from__entity_manager(
        Game *p_game,
        Entity_Manager *p_entity_manager, 
        Entity *p_entity) {
    if (p_entity_manager->entity_count__quantity_u32 > 0)
        p_entity_manager->entity_count__quantity_u32--;
    if (p_entity->entity_functions.m_entity_dispose_handler) {
        p_entity->entity_functions.m_entity_dispose_handler(
                p_entity,
                p_game);
    }
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
