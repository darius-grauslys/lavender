#ifndef ENTITY_MANAGER_H
#define ENTITY_MANAGER_H

#include "defines_weak.h"
#include "entity/entity.h"
#include "platform_defines.h"
#include "serialization/hashing.h"
#include "types/implemented/entity_kind.h"
#include <defines.h>
#include <debug/debug.h>

void initialize_entity_manager(Entity_Manager *p_entity_manager);

void f_entity_initializer__default(
        Game *p_game,
        World *p_world,
        Entity *p_entity);

void register_entity_into__entity_manager(
        Entity_Manager *p_entity_manager,
        Entity_Kind the_kind_of__entity,
        Entity_Functions entity_functions);

///
/// Ensure that the entity has the proper functions
/// for it's type. This is called whenever an entity
/// is allocated, or deserialized.
///
void sanitize_entity_functions(
        Entity_Manager *p_entity_manager,
        Entity *p_entity);

///
/// Create a new entity instance within the entity_manager object pool.
/// Return nullptr (0) if fails to get new entity.
///
Entity *allocate_entity_with__this_uuid_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity,
        Identifier__u32 uuid__u32);

///
/// Create a new entity instance within the entity_manager object pool.
/// Return nullptr (0) if fails to get new entity.
///
Entity *allocate_entity_in__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_entity_manager,
        enum Entity_Kind kind_of_entity);

///
/// Release entity from the entity_manager object pool.
///
void release_entity_from__entity_manager(
        Game *p_game,
        World *p_world,
        Entity_Manager *p_manager, 
        Entity *p_entity);

static inline
void set_entity_initializer_in__entity_manager(
        Entity_Manager *p_entity_manager,
        f_Entity_Initializer f_entity_initializer) {
    p_entity_manager->f_entity_initializer =
        f_entity_initializer;
}

static inline
Entity *get_p_entity_by__uuid_from__entity_manager(
        Entity_Manager *p_entity_manager,
        Identifier__u32 uuid) {
    return (Entity*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)&p_entity_manager->entities, 
            MAX_QUANTITY_OF__ENTITIES, 
            uuid);
}

static inline
void set_entity_functions(
        Entity_Manager *p_entity_manager,
        Entity *p_entity) {
#ifndef NDEBUG
    if (get_kind_of__entity(p_entity)
            >= Entity_Kind__Unknown) {
        debug_error("set_entity_functions, invalid entity kind.");
        return;
    }
#endif
    p_entity->entity_functions =
        p_entity_manager->entity_functions[
            get_kind_of__entity(p_entity)];
}

///
/// NOTE: this is NOT a reliable way to reference specific entities
/// and this function should only be used to blindly iterate over
/// ALL entities. In other words, there is no guarantee that the
/// entity "at index 1" will be the same entity 5 seconds ago.
///
/// If you need to keep track of a specific entity, hold onto
/// that entity's UUID, and use the corresponding entity_manager 
/// getter function to acquire it.
///
static inline
Entity *get_p_entity_by__index_from__entity_manager(
        Entity_Manager *p_entity_manager,
        Index__u32 index_of__entity) {
#ifndef NDEBUG
    if (!p_entity_manager) {
        debug_error("p_entity_manager == 0.");
        return 0;
    }
    if (index_of__entity >= MAX_QUANTITY_OF__ENTITIES) {
        debug_error("get_p_entity_by__index_from__entity_manager, index out of bounds.");
        return 0;
    }
#endif
    return p_entity_manager->ptr_array_of__entities[index_of__entity];
}

#endif
