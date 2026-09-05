#include "debug/debug.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "platform_defines.h"
#include <debug/debug_entity.h>

DEBUG_Entity_Scanner __DEBUG_entity_scanner = {0};

DEBUG_Entity_Scanner __m_debug_entity_scanner__next_entity() {
    if (!__DEBUG_entity_scanner.p_entity_manager) {
        debug_warning("[DEBUG] __m_debug_entity_scanner__next_entity, must call debug_get_entity_scanner at least once.");
        goto exit;
    }

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
    return __DEBUG_entity_scanner;
}

DEBUG_Entity_Scanner debug_get_entity_scanner(Game *p_game) {
    if (!get_p_world_from__game(p_game)) {
        debug_warning("[DEBUG] debug_get_entity_scanner, p_world == 0.");
        debug_warning("[DEBUG] cannot acquire p_entity_manager.");
        debug_info("[DEBUG] is a world loaded?");
        return (DEBUG_Entity_Scanner){0};
    }

    Entity_Manager *p_entity_manager =
        get_p_entity_manager_from__game(p_game);

    if (!p_entity_manager) {
        debug_warning("[DEBUG] debug_get_entity_scanner, cannot acquire p_entity_manager.");
        debug_warning("[DEBUG] memory might be corrupted!");
        return (DEBUG_Entity_Scanner){0};
    }

    __DEBUG_entity_scanner.p_entity_manager = p_entity_manager;
    __DEBUG_entity_scanner.p_entity__current = p_entity_manager->entities;
    __DEBUG_entity_scanner.m_next_entity = __m_debug_entity_scanner__next_entity;

    return __DEBUG_entity_scanner;
}
