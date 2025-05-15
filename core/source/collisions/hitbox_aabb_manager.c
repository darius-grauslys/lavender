#include "collisions/hitbox_aabb_manager.h"
#include "collisions/collision_node.h"
#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "game.h"
#include "game_action/core/hitbox/game_action__hitbox.h"
#include "numerics.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"

static inline
Hitbox_AABB *get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager(
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
    memset(p_hitbox_aabb_manager,
            0,
            sizeof(Hitbox_AABB_Manager));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)p_hitbox_aabb_manager->hitboxes, 
            MAX_QUANTITY_OF__HITBOX_AABB, 
            sizeof(Hitbox_AABB));
}

Hitbox_AABB *allocate_hitbox_aabb_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
    if (p_hitbox_aabb_manager
            ->index_of__next_hitbox_aabb_in__ptr_array
            >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, hitbox_manager is full.");
        return 0;
    }
    Index__u32 index_of__hitbox =
        poll_for__uuid_collision(
                (Serialization_Header *)p_hitbox_aabb_manager->hitboxes, 
                MAX_QUANTITY_OF__HITBOX_AABB, 
                uuid__u32,
                INDEX__UNKNOWN__u32);
    if (is_index_u32__out_of_bounds(index_of__hitbox)) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, failed to allocate hitbox.");
        return 0;
    }

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager(
                p_hitbox_aabb_manager, 
                index_of__hitbox);
    
    if (!is_serialized_struct__deallocated(
                &p_hitbox_aabb->_serialization_header)) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, uuid__u32 already in use.");
        return 0;
    }

    p_hitbox_aabb_manager->ptr_array_of__active_hitboxes[
        p_hitbox_aabb_manager
            ->index_of__next_hitbox_aabb_in__ptr_array++] =
            p_hitbox_aabb;

    initialize_serialization_header(
            &p_hitbox_aabb->_serialization_header, 
            uuid__u32, 
            sizeof(Hitbox_AABB));
    return p_hitbox_aabb;
}

void release_hitbox_aabb_from__hitbox_aabb_manager(
        Game *p_game,
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

    for (Index__u32 index_of__hitbox = 0;
            index_of__hitbox < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__hitbox++) {
        Hitbox_AABB *p_hitbox_aabb__in_ptr_array =
            get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager, 
                    index_of__hitbox);

        if (!p_hitbox_aabb__in_ptr_array) {
            debug_warning("release_hitbox_aabb_from__hitbox_aabb_manager, p_hitbox_aabb was not found in ptr_array.");
            break;
        }

        if (p_hitbox_aabb__in_ptr_array == p_hitbox_aabb) {
            p_hitbox_aabb_manager->ptr_array_of__active_hitboxes[
                index_of__hitbox] =
                    p_hitbox_aabb_manager->ptr_array_of__active_hitboxes[
                    --p_hitbox_aabb_manager
                        ->index_of__next_hitbox_aabb_in__ptr_array];
            p_hitbox_aabb_manager->ptr_array_of__active_hitboxes[
                p_hitbox_aabb_manager
                    ->index_of__next_hitbox_aabb_in__ptr_array] = 0;
            break;
        }
    }

    Global_Space *p_global_space =
        (is_world_allocated_for__game(p_game))
        ? get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__game(p_game), 
                vector_3i32F4_to__chunk_vector_3i32(
                    p_hitbox_aabb->position__3i32F4))
        : 0
        ;

    if (p_global_space) {
        remove_entry_from__collision_node(
                get_p_collision_node_pool_from__world(
                    get_p_world_from__game(p_game)), 
                get_p_collision_node_from__global_space(
                    p_global_space), 
                GET_UUID_P(p_hitbox_aabb));
    }

    initialize_hitbox(p_hitbox_aabb);
}

Hitbox_AABB *get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
    return (Hitbox_AABB*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_hitbox_aabb_manager->hitboxes, 
            MAX_QUANTITY_OF__HITBOX_AABB, 
            uuid__u32);
}

void poll_hitbox_manager_for__movement(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager) {
    for (Index__u32 index_of__hitbox = 0;
            index_of__hitbox
            < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__hitbox++) {
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager, 
                    index_of__hitbox);
        if (!p_hitbox_aabb)
            break;

        dispatch_game_action__hitbox(
                p_game, 
                GET_UUID_P(p_hitbox_aabb), 
                add_vectors__3i32F4(
                    get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb), 
                    get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb)),
                get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb));
        // TODO: do ground friction on acceleration
        p_hitbox_aabb->velocity__3i32F4 =
            VECTOR__3i32F4__0_0_0;
    }
}
