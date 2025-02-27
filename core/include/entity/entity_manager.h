#ifndef ENTITY_MANAGER_H
#define ENTITY_MANAGER_H

#include "defines_weak.h"
#include "platform_defines.h"
#include "serialization/hashing.h"
#include <defines.h>
#include <debug/debug.h>

void initialize_entity_manager(Entity_Manager *p_entity_manager);

///
/// Create a new entity instance within the entity_manager object pool.
/// Return nullptr (0) if fails to get new entity.
///
Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity,
        Vector__3i32F4 position,
        Graphics_Window
            *p_graphics_window);

///
/// Release entity from the entity_manager object pool.
///
void release_entity_from__entity_manager(
        Entity_Manager *p_manager, 
        Entity *p_entity);

bool resolve_p_serialized_entity_ptr_with__entity_manager(
        Entity_Manager *p_entity_manager,
        Serialized_Entity_Ptr *s_entity_ptr);

static inline
Entity *get_p_entity_by__uuid_from__entity_manager(
        Entity_Manager *p_entity_manager,
        Identifier__u32 uuid) {
    return (Entity*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)&p_entity_manager->entities, 
            ENTITY_MAXIMUM_QUANTITY_OF, 
            uuid);
}

static Entity inline *get_p_entity_from__entity_manager(
        Entity_Manager *p_entity_manager,
        Index__u32 index_of__entity) {
#ifndef NDEBUG
    if (ENTITY_MAXIMUM_QUANTITY_OF 
            <= index_of__entity) {
        debug_abort("get_p_entity_from__entity_manager, index out of bounds %d",
                index_of__entity);
        return 0;
    }
#endif
    return &p_entity_manager->entities[index_of__entity];
}


#endif
