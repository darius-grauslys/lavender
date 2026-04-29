#include "collisions/core/aabb/hitbox_aabb_manager.h"
#include "collisions/core/aabb/hitbox_aabb.h"
#include "collisions/hitbox.h"
#include "defines_weak.h"
#include "game_action/core/hitbox/game_action__hitbox.h"
#include "collisions/collision_node.h"
#include "defines.h"
#include "game.h"
#include "numerics.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"
#include <string.h>

static inline
Hitbox_AABB *get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Index__u32 index_of__hitbox) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return 0;
    }
    if (index_of__hitbox >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager, index out of bounds, %d/%d", index_of__hitbox, MAX_QUANTITY_OF__HITBOX_AABB);
        return 0;
    }
#endif
    return &p_hitbox_aabb_manager->pM_pool_of__hitboxes[index_of__hitbox];
}

void *f_hitbox_manager__allocator_AABB(
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__allocate,
        Quantity__u32 quantity_of__hitboxes_to__pool) {
    void *pM_hitbox_manager = malloc(sizeof(Hitbox_AABB_Manager));
    if (!pM_hitbox_manager) {
        debug_error("f_hitbox_manager__allocator_AABB, failed to allocate manager.");
        return 0;
    }

    void *pM_pool_of__hitboxes = 
        malloc(sizeof(Hitbox_AABB) * quantity_of__hitboxes_to__pool);
    if (!pM_pool_of__hitboxes) {
        debug_error("f_hitbox_manager__allocator_AABB, failed to allocate hitbox pool.");
        free(pM_hitbox_manager);
        return 0;
    }

    void *pM_ptr_array_of__hitbox_records = 
        malloc(sizeof(Hitbox_AABB*) * quantity_of__hitboxes_to__pool);
    if (!pM_ptr_array_of__hitbox_records) {
        debug_error("f_hitbox_manager__allocator_AABB, failed to allocate hitbox pointer array.");
        free(pM_hitbox_manager);
        free(pM_pool_of__hitboxes);
        return 0;
    }

    Hitbox_AABB_Manager *p_hitbox_manager__aabb =
        (Hitbox_AABB_Manager*)pM_hitbox_manager;

    initialize_hitbox_aabb_manager(
            p_hitbox_manager__aabb,
            pM_pool_of__hitboxes,
            pM_ptr_array_of__hitbox_records,
            quantity_of__hitboxes_to__pool
            );

    return pM_hitbox_manager;
}

void f_hitbox_manager__deallocator_AABB(
        void *pM_hitbox_manager,
        Hitbox_Manager_Type the_type_of__hitbox_manager_to__deallocate) {
    if (!pM_hitbox_manager) {
        debug_error("f_hitbox_manager__deallocator_AABB, pM_hitbox_manager == 0.");
        return;
    }

#ifndef NDEBUG
    if (Hitbox_Manager_Type__AABB
            != the_type_of__hitbox_manager_to__deallocate) {
        debug_error("f_hitbox_manager__deallocator_AABB, incompatible type.");
        return;
    }
#endif

    Hitbox_AABB_Manager *p_hitbox_manager__aabb = 
        (Hitbox_AABB_Manager*)pM_hitbox_manager;

    free(p_hitbox_manager__aabb->pM_pool_of__hitboxes);
    free(p_hitbox_manager__aabb->pM_ptr_array_of__hitbox_records);
    free(p_hitbox_manager__aabb);
}

bool f_hitbox_manager__opaque_property_access_of__hitbox_AABB(
        void *pV_hitbox, 
        void *pV_OPTIONAL_dimensions, 
        void *pV_OPTIONAL_position, 
        void *pV_OPTIONAL_velocity, 
        void *pV_OPTIONAL_acceleration, 
        Hitbox_Flags__u8 *p_OPTIONAL_hitbox_flags__u8, 
        bool is_setting_or__getting) {
    if (!pV_hitbox) {
        debug_error("f_hitbox_manager__opaque_property_access_of__hitbox_AABB, pV_hitbox == 0.");
        return false;
    }

    Hitbox_AABB *p_hitbox_aabb = pV_hitbox;

    if (is_setting_or__getting) {
        // Set values of the hitbox
        if (p_OPTIONAL_hitbox_flags__u8)
            p_hitbox_aabb->hitbox_aabb_flags__u8 = *p_OPTIONAL_hitbox_flags__u8;

        if (pV_OPTIONAL_dimensions) {
            u32 *p_dimentions = pV_OPTIONAL_dimensions;
            p_hitbox_aabb->width__quantity_u32 = 
                p_dimentions[0];
            p_hitbox_aabb->height__quantity_u32 = 
                p_dimentions[1];
        }
        if (pV_OPTIONAL_position)
            p_hitbox_aabb->position__3i32F4 = 
                *(Vector__3i32F4*)pV_OPTIONAL_position;
        if (pV_OPTIONAL_velocity)
            p_hitbox_aabb->velocity__3i32F4 = 
                *(Vector__3i32F4*)pV_OPTIONAL_velocity;
        if (pV_OPTIONAL_acceleration)
            p_hitbox_aabb->acceleration__3i16F8 = 
                *(Vector__3i16F8*)pV_OPTIONAL_acceleration;

        set_hitbox_flags_as__dirty(&p_hitbox_aabb->hitbox_aabb_flags__u8);
    } else {
        // Get values of the hitbox
        if (p_OPTIONAL_hitbox_flags__u8)
            *p_OPTIONAL_hitbox_flags__u8 = p_hitbox_aabb->hitbox_aabb_flags__u8;

        if (pV_OPTIONAL_dimensions) {
            u32 *p_dimensions = pV_OPTIONAL_dimensions;
            p_dimensions[0] = p_hitbox_aabb->width__quantity_u32;
            p_dimensions[1] = p_hitbox_aabb->height__quantity_u32;
        }

        if (pV_OPTIONAL_position)
            *(Vector__3i32F4 *)pV_OPTIONAL_position =
                p_hitbox_aabb->position__3i32F4;

        if (pV_OPTIONAL_velocity)
            *(Vector__3i32F4 *)pV_OPTIONAL_velocity =
                p_hitbox_aabb->velocity__3i32F4;

        if (pV_OPTIONAL_acceleration)
            *(Vector__3i16F8 *)pV_OPTIONAL_acceleration =
                p_hitbox_aabb->acceleration__3i16F8;
    }

    return true;
}

void initialize_hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        void *pM_pool_of__hitboxes,
        void **pM_ptr_array_of__hitbox_records,
        Quantity__u32 quantity_of__hitboxes_to__pool) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("initialize_hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return;
    }
#endif
    p_hitbox_aabb_manager->pM_pool_of__hitboxes =
        (Hitbox_AABB*)pM_pool_of__hitboxes;
    p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records =
        (Hitbox_AABB**)pM_ptr_array_of__hitbox_records;
    p_hitbox_aabb_manager->quantity_of__hitboxes =
        quantity_of__hitboxes_to__pool;

    initialize_serialization_header__contiguous_array(
            pM_pool_of__hitboxes, 
            quantity_of__hitboxes_to__pool, 
            sizeof(Hitbox_AABB));
    memset(
            pM_ptr_array_of__hitbox_records, 
            0, 
            sizeof(Hitbox_AABB*)
            * quantity_of__hitboxes_to__pool);

    p_hitbox_aabb_manager->index_of__next_hitbox_aabb_in__records = 0;
}

Hitbox_AABB *allocate_hitbox_aabb_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return 0;
    }
#endif
    if (p_hitbox_aabb_manager
            ->index_of__next_hitbox_aabb_in__records
            >= p_hitbox_aabb_manager->quantity_of__hitboxes) {
        debug_error("allocate_hitbox_aabb_from__hitbox_aabb_manager, hitbox_manager is full.");
        return 0;
    }
    Index__u32 index_of__hitbox =
        poll_for__uuid_collision(
                (Serialization_Header *)p_hitbox_aabb_manager->pM_pool_of__hitboxes, 
                p_hitbox_aabb_manager->quantity_of__hitboxes, 
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

    p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[
        p_hitbox_aabb_manager
            ->index_of__next_hitbox_aabb_in__records++] =
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
    if (!p_hitbox_aabb_manager) {
        debug_error("release_hitbox_aabb_from__hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return;
    }
    u32 index = p_hitbox_aabb
        - p_hitbox_aabb_manager->pM_pool_of__hitboxes;
    if (index >= p_hitbox_aabb_manager->quantity_of__hitboxes) {
        debug_error("release_hitbox_aabb_from__hitbox_aabb_manager, p_hitbox is not allocated with this manager.");
        return;
    }
#endif

    for (Index__u32 index_of__hitbox = 0;
            index_of__hitbox < p_hitbox_aabb_manager->quantity_of__hitboxes;
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
            p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[
                index_of__hitbox] =
                    p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[
                    --p_hitbox_aabb_manager
                        ->index_of__next_hitbox_aabb_in__records];
            p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[
                p_hitbox_aabb_manager
                    ->index_of__next_hitbox_aabb_in__records] = 0;
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

    initialize_hitbox_aabb(p_hitbox_aabb);
}

Hitbox_AABB *get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Identifier__u32 uuid__u32) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return 0;
    }
#endif
    return (Hitbox_AABB*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_hitbox_aabb_manager->pM_pool_of__hitboxes, 
            p_hitbox_aabb_manager->quantity_of__hitboxes, 
            uuid__u32);
}

void poll_hitbox_manager_for__movement(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("poll_hitbox_manager_for__movement, p_hitobx_aabb_manager == 0.");
        return;
    }
#endif
    for (Index__u32 index_of__hitbox = 0;
            index_of__hitbox
            < p_hitbox_aabb_manager->quantity_of__hitboxes;
            index_of__hitbox++) {
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager, 
                    index_of__hitbox);
        if (!p_hitbox_aabb)
            break;
        if (!is_hitbox_aabb__dirty(p_hitbox_aabb)
                || !is_hitbox_aabb__active(p_hitbox_aabb))
            continue;

        dispatch_game_action__hitbox(
                p_game, 
                GET_UUID_P(p_hitbox_aabb), 
                add_vectors__3i32F4(
                    get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb), 
                    get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb)),
                add_vectors__3i32F4(
                    get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb), 
                    vector_3i16F8_to__vector_3i32F4(
                        get_acceleration_3i16F8_of__hitbox_aabb(p_hitbox_aabb))),
                VECTOR__3i16F8__0_0_nGRAVITY_PER_TICK,
                Hitbox_Kind__AABB);
    }
}
