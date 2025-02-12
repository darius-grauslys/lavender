#include "collisions/hitbox_aabb_manager.h"
#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "numerics.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"

static inline
Hitbox_AABB *get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Index__u32 index_of__hitbox) {
#ifndef NDEBUG
    if (index_of__hitbox >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager, index out of bounds, %d/%d", index_of__hitbox, MAX_QUANTITY_OF__HITBOX_AABB);
        return 0;
    }
#endif
    return &p_hitbox_aabb_manager->hitboxes[index_of__hitbox];
}

void initialize_hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_hitbox_aabb_manager->hitboxes, 
            MAX_QUANTITY_OF__HITBOX_AABB, 
            sizeof(Hitbox_AABB));
}

Hitbox_AABB *allocate_hitbox_aabb_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
    Index__u32 index_of__hitbox =
        poll_for__uuid_collision(
                (Serialization_Header *)p_hitbox_aabb_manager->hitboxes, 
                MAX_QUANTITY_OF__HITBOX_AABB, 
                uuid__u32);
    if (is_index_u32__out_of_bounds(index_of__hitbox)) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, failed to allocate hitbox.");
        return 0;
    }

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
                p_hitbox_aabb_manager, 
                index_of__hitbox);
    
    if (is_serialized_struct__deallocated(
                &p_hitbox_aabb->_serialization_header)) {
        initialize_serialization_header(
                &p_hitbox_aabb->_serialization_header, 
                uuid__u32, 
                sizeof(Hitbox_AABB));
        return p_hitbox_aabb;
    }

    debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, uuid__u32 already in use.");
    return 0;
}

void release_hitbox_aabb_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Hitbox_AABB *p_hitbox_aabb) {
#ifndef NDEBUG
    u32 index = p_hitbox_aabb
        - p_hitbox_aabb_manager->hitboxes;
    if (index >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("release_hitbox_aabb_from__hitbox_aabb_manager, p_hitbox is not allocated with this manager.");
        return;
    }
#endif

    initialize_hitbox(p_hitbox_aabb);
}

Hitbox_AABB *get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
    Index__u32 index_of__hitbox =
        poll_for__uuid_collision(
                (Serialization_Header *)p_hitbox_aabb_manager->hitboxes, 
                MAX_QUANTITY_OF__HITBOX_AABB, 
                uuid__u32);

    if (is_index_u32__out_of_bounds(index_of__hitbox)) {
        debug_error("get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager, hitbox not found.");
        return 0;
    }

    return get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
            p_hitbox_aabb_manager, 
            index_of__hitbox);
}
