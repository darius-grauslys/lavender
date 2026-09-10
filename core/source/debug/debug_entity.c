#include "debug/debug.h"
#include "defines.h"
#include "entity/entity.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "platform_defines.h"
#include "types/implemented/entity/entity_kind.h"
#include <debug/debug_entity.h>

DEBUG_Entity_Scanner __DEBUG_entity_scanner = {0};

///
/// Returns false if the entity pointer was moved.
/// Precondition: __DEBUG_scene_scanner.p_entity_manager != 0
///
bool __debug_resolve_tracked_entity_in__scanner() {
    Entity_Manager *p_entity_manager = 
        __DEBUG_entity_scanner.p_entity_manager;

    if (__DEBUG_entity_scanner.p_entity__current) {
        Index__u32 index_of__p_entity =
            __DEBUG_entity_scanner
            .p_entity__current
            - p_entity_manager
            ->entities
            ;
        if (index_of__p_entity
                >= MAX_QUANTITY_OF__ENTITIES) {
            // TODO: warn about corrupt memory
            debug_warning("[DEBUG] __debug_resolve_tracked_entity_in__scanner, p_entity out of bounds.");
            debug_warning("[DEBUG] moving pointer to start of bounds.");
            debug_warning("[DEBUG] memory might be corrupt!");
            __DEBUG_entity_scanner.p_entity__current =
                p_entity_manager
                ->ptr_array_of__entities[0];
            return true;
        }
    } 

    if (!__DEBUG_entity_scanner.p_entity__current) {
        __DEBUG_entity_scanner.p_entity__current =
            p_entity_manager
            ->ptr_array_of__entities[0];
        return true;
    }
}

DEBUG_Entity_Scanner __m_debug_entity_scanner__refresh() {
    Entity_Manager *p_entity_manager =
        __DEBUG_entity_scanner.p_entity_manager;
    if (!p_entity_manager) {
        debug_warning("[DEBUG] __m_debug_entity_scanner__refresh, must call debug_get_entity_scanner at least once.");
        goto exit;
    }

    __debug_resolve_tracked_entity_in__scanner();

    __DEBUG_entity_scanner.quantity_of__entities =
        p_entity_manager->p_ptr_entity__next_in_ptr_array
        - p_entity_manager->ptr_array_of__entities
        ;

    Entity *p_entity = __DEBUG_entity_scanner.p_entity__current;

    if (!p_entity) {
        __DEBUG_entity_scanner.uuid_of__entity__current =
            IDENTIFIER__UNKNOWN__u32;
        __DEBUG_entity_scanner.the_kind_of__entity__current =
            Entity_Kind__Unknown;
    } else {
        __DEBUG_entity_scanner.uuid_of__entity__current =
            GET_UUID_P(p_entity);
        __DEBUG_entity_scanner.the_kind_of__entity__current =
            get_kind_of__entity(p_entity);
    }
exit:
    // Module post condition is inforced here.
    return __DEBUG_entity_scanner;
}

DEBUG_Entity_Scanner __m_debug_entity_scanner__next_entity() {
    if (!__DEBUG_entity_scanner.p_entity_manager) {
        debug_warning("[DEBUG] __m_debug_entity_scanner__next_entity, must call debug_get_entity_scanner at least once.");
        goto exit;
    }

    __debug_resolve_tracked_entity_in__scanner();

    Index__u32 index_of__entity =
        __DEBUG_entity_scanner.p_entity__current
        - __DEBUG_entity_scanner.p_entity_manager->entities;
    if (index_of__entity >= MAX_QUANTITY_OF__ENTITIES) {
        __DEBUG_entity_scanner.p_entity__current = 
            &__DEBUG_entity_scanner
            .p_entity_manager
            ->entities[0];
        debug_warning("[DEBUG] __m_debug_entity_scanner__next_entity, entity pointer out of bounds.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto exit;
    }

    index_of__entity = (index_of__entity+1) % MAX_QUANTITY_OF__ENTITIES;
    __DEBUG_entity_scanner.p_entity__current =
        get_p_entity_by__index_from__entity_manager(
                __DEBUG_entity_scanner.p_entity_manager, 
                index_of__entity);
exit:
    __m_debug_entity_scanner__refresh(); // Module post condition
    return __DEBUG_entity_scanner;
}

DEBUG_Entity_Scanner debug_get_entity_scanner(Game *p_game) {
    if (!get_p_world_from__game(p_game)) {
        debug_warning("[DEBUG] debug_get_entity_scanner, p_world == 0.");
        debug_warning("[DEBUG] cannot acquire p_entity_manager.");
        debug_info("[DEBUG] is a world loaded?");
        goto error;
    }

    Entity_Manager *p_entity_manager =
        get_p_entity_manager_from__game(p_game);

    if (!p_entity_manager) {
        debug_warning("[DEBUG] debug_get_entity_scanner, cannot acquire p_entity_manager.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto error;
    }

    __DEBUG_entity_scanner.p_entity_manager = p_entity_manager;
    __DEBUG_entity_scanner.p_entity__current = p_entity_manager->entities;
    __DEBUG_entity_scanner.m_refresh = __m_debug_entity_scanner__refresh;
    __DEBUG_entity_scanner.m_next_entity = __m_debug_entity_scanner__next_entity;

exit:
    __m_debug_entity_scanner__refresh(); // Module post condition
    return __DEBUG_entity_scanner;
error:
    return (DEBUG_Entity_Scanner){0};
}
