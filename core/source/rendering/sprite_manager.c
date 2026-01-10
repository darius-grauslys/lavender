#include "rendering/sprite_manager.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/sprite_pool.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include <stdlib.h>
#include <string.h>

void initialize_sprite_manager(
        Sprite_Manager *p_sprite_manager) {
    memset(p_sprite_manager, 0, sizeof(Sprite_Manager));
}

bool allocate_sprite_pools_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Quantity__u8 quantity_of__sprite_pools) {
    if (is_sprite_pools_allocated_in__sprite_manager(p_sprite_manager)) {
        debug_error("allocate_sprite_pools_from__sprite_manager, pM_sprite_pools != 0.");
        return false;
    }

    p_sprite_manager->pM_sprite_pools =
        malloc(sizeof(Sprite_Pool) * quantity_of__sprite_pools);

    p_sprite_manager->max_quantity_of__sprite_pools = quantity_of__sprite_pools;

    for (Index__u8 index_of__sprite_manager = 0;
            index_of__sprite_manager < quantity_of__sprite_pools;
            index_of__sprite_manager++) {
        initialize_sprite_pool(
                &p_sprite_manager->pM_sprite_pools[index_of__sprite_manager]);
    }

    return p_sprite_manager->pM_sprite_pools != 0;
}

void release_sprite_pools_from__sprite_manager(
        Sprite_Manager *p_sprite_manager) {
    if (!is_sprite_pools_allocated_in__sprite_manager(p_sprite_manager)) {
        debug_error("release_sprite_pools_from__sprite_manager, pM_sprite_pools == 0.");
        return;
    }

    free(p_sprite_manager->pM_sprite_pools);
}

Sprite_Pool *allocate_sprite_pool_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Identifier__u32 uuid_of__sprite_pool,
        Quantity__u32 max_quantity_of__sprites_in__sprite_pool) {
    if (!is_sprite_pools_allocated_in__sprite_manager(p_sprite_manager)) {
        debug_error("allocate_sprite_pool_from__sprite_manager, pM_sprite_pools == 0.");
        return 0;
    }

    Sprite_Pool *p_sprite_pool =
        (Sprite_Pool*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)p_sprite_manager->pM_sprite_pools, 
                p_sprite_manager->max_quantity_of__sprite_pools, 
                uuid_of__sprite_pool);

    if (!p_sprite_pool) {
        debug_warning("The sprite pool is likely full!");
        debug_error("allocate_sprite_pool_from__sprite_manager, p_sprite_pool == 0.");
        return 0;
    }

    if (!allocate_sprite_pool__members(
                p_sprite_pool, 
                max_quantity_of__sprites_in__sprite_pool)) {
        debug_error("allocate_sprite_pool_from__sprite_manager, failed to allocate sprite pool data.");
        return 0;
    }

    ALLOCATE_P(p_sprite_pool, uuid_of__sprite_pool);

    return p_sprite_pool;
}

void release_sprite_pool_from__sprite_manager(
        Sprite_Manager *p_sprite_manager,
        Sprite_Pool *p_sprite_pool) {
#ifndef NDEBUG
    if (!p_sprite_manager) {
        debug_error("release_sprite_from__sprite_manager, p_sprite_manager == 0.");
        return;
    }
#endif
    if (!p_sprite_pool) {
        debug_error("release_sprite_from__sprite_manager, p_sprite_pool == 0.");
        return;
    }
    if (p_sprite_pool - p_sprite_manager->pM_sprite_pools 
            >= p_sprite_manager->max_quantity_of__sprite_pools) {
        debug_error("release_sprite_from__sprite_manager, p_sprite_pool was not allocated with this p_sprite_manager.");
        return;
    }
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_sprite_pool, 
            sizeof(Sprite_Pool));
}
