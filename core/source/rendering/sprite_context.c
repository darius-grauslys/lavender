#include "rendering/sprite_context.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/sprite_manager.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"
#include <stdlib.h>
#include <string.h>

void initialize_sprite_context(
        Sprite_Context *p_sprite_context) {
    memset(p_sprite_context, 0, sizeof(Sprite_Context));
}

bool allocate_sprite_managers_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Quantity__u8 quantity_of__sprite_managers) {
    if (is_sprite_managers_allocated_in__sprite_context(p_sprite_context)) {
        debug_error("allocate_sprite_managers_from__sprite_context, pM_sprite_managers != 0.");
        return false;
    }

    p_sprite_context->pM_sprite_managers =
        malloc(sizeof(Sprite_Manager) * quantity_of__sprite_managers);

    p_sprite_context->max_quantity_of__sprite_managers = quantity_of__sprite_managers;

    for (Index__u8 index_of__sprite_context = 0;
            index_of__sprite_context < quantity_of__sprite_managers;
            index_of__sprite_context++) {
        initialize_sprite_manager(
                &p_sprite_context->pM_sprite_managers[index_of__sprite_context]);
    }

    return p_sprite_context->pM_sprite_managers != 0;
}

void release_sprite_managers_from__sprite_context(
        Sprite_Context *p_sprite_context) {
    if (!is_sprite_managers_allocated_in__sprite_context(p_sprite_context)) {
        debug_error("release_sprite_managers_from__sprite_context, pM_sprite_managers == 0.");
        return;
    }

    free(p_sprite_context->pM_sprite_managers);
}

Sprite_Manager *allocate_sprite_manager_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Identifier__u32 uuid_of__sprite_manager,
        Quantity__u32 max_quantity_of__sprites_in__sprite_manager) {
    if (!is_sprite_managers_allocated_in__sprite_context(p_sprite_context)) {
        debug_error("allocate_sprite_manager_from__sprite_context, pM_sprite_managers == 0.");
        return 0;
    }

    Sprite_Manager *p_sprite_manager =
        (Sprite_Manager*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)p_sprite_context->pM_sprite_managers, 
                p_sprite_context->max_quantity_of__sprite_managers, 
                uuid_of__sprite_manager);

    if (!p_sprite_manager) {
        debug_warning("The sprite pool is likely full!");
        debug_error("allocate_sprite_manager_from__sprite_context, p_sprite_manager == 0.");
        return 0;
    }

    if (!allocate_sprite_manager__members(
                p_sprite_manager, 
                max_quantity_of__sprites_in__sprite_manager)) {
        debug_error("allocate_sprite_manager_from__sprite_context, failed to allocate sprite pool data.");
        return 0;
    }

    ALLOCATE_P(p_sprite_manager, uuid_of__sprite_manager);

    return p_sprite_manager;
}

void release_sprite_manager_from__sprite_context(
        Sprite_Context *p_sprite_context,
        Sprite_Manager *p_sprite_manager) {
#ifndef NDEBUG
    if (!p_sprite_context) {
        debug_error("release_sprite_from__sprite_context, p_sprite_context == 0.");
        return;
    }
#endif
    if (!p_sprite_manager) {
        debug_error("release_sprite_from__sprite_context, p_sprite_manager == 0.");
        return;
    }
    if (p_sprite_manager - p_sprite_context->pM_sprite_managers 
            >= p_sprite_context->max_quantity_of__sprite_managers) {
        debug_error("release_sprite_from__sprite_context, p_sprite_manager was not allocated with this p_sprite_context.");
        return;
    }
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header*)p_sprite_manager, 
            sizeof(Sprite_Manager));
}
