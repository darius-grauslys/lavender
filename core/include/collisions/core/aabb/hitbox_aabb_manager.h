#ifndef HITBOX_AABB_MANAGER_H
#define HITBOX_AABB_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/hashing.h"

void *f_hitbox_manager__allocator_AABB(
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool);

void f_hitbox_manager__deallocator_AABB(
        void *pM_hitbox_manager,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__deallocate);

bool f_hitbox_manager__opaque_property_access_of__hitbox_AABB(
        void *pV_hitbox,
        void *pV_OPTIONAL_dimensions,
        void *pV_OPTIONAL_position,
        void *pV_OPTIONAL_velocity,
        void *pV_OPTIONAL_acceleration,
        Hitbox_Flags__u8 *p_OPTIONAL_hitbox_flags__u8,
        bool is_setting_or__getting);

void initialize_hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager);

Hitbox_AABB *allocate_hitbox_aabb_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32);

void release_hitbox_aabb_from__hitbox_aabb_manager(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Hitbox_AABB *p_hitbox_aabb);

Hitbox_AABB *get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32);

void poll_hitbox_manager_for__movement(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager);

static inline
Hitbox_AABB *get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Entity *p_entity) {
    return get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
            p_hitbox_aabb_manager, 
            GET_UUID_P(p_entity));
}

static inline
Hitbox_AABB *get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Index__u32 index_of__hitbox) {
#ifndef NDEBUG
    if (index_of__hitbox >= p_hitbox_aabb_manager->quantity_of__hitboxes) {
        debug_error("get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager, index_of__hitbox out of bounds.");
        return 0;
    }
#endif
    return p_hitbox_aabb_manager
        ->pM_ptr_array_of__hitbox_records[
        index_of__hitbox];
}

#endif
