#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "scene/scene_manager.h"
#include "types/implemented/scene/scene_kind.h"
#include <debug/debug_scene.h>

DEBUG_Scene_Scanner __DEBUG_scene_scanner = {0};

DEBUG_Scene_Scanner _m_debug_scene_scanner__iterate_scene() {
    if (!__DEBUG_scene_scanner.p_scene_manager) {
        debug_warning("[DEBUG] _m_debug_scene_scanner__iterate_scene, p_scene_manager == 0.");
        debug_warning("[DEBUG] call debug_get_ui_scanner at least once.");
        goto error;
    }

    Index__u32 index_of__scene = 
        __DEBUG_scene_scanner.p_scene__current_in__scan
        - __DEBUG_scene_scanner
        .p_scene_manager
        ->scenes
        ;

    if (index_of__scene >= Scene_Kind__Unknown) {
        debug_warning("[DEBUG] _m_debug_scene_scanner__iterate_scene, iterated scene out of bounds.");
        debug_warning("[DEBUG] recovering to first scene of manager.");
        debug_warning("[DEBUG] memory might be corrupted!");

        __DEBUG_scene_scanner.p_scene__current_in__scan =
            __DEBUG_scene_scanner.p_scene_manager->scenes;
        goto finish;
    }

    Scene *p_scene = 0;
    for (Index__u32 offset_of__scene = index_of__scene;
            offset_of__scene < Scene_Kind__Unknown
            && p_scene == 0;
            offset_of__scene++) {
        Index__u32 normalized_index = 
            (index_of__scene+offset_of__scene)
            % Scene_Kind__Unknown
            ;

        p_scene = 
            &__DEBUG_scene_scanner
            .p_scene_manager
            ->scenes[normalized_index]
            ;
    }

    __DEBUG_scene_scanner.p_scene__current_in__scan = p_scene;

finish:
    return __DEBUG_scene_scanner;
error:
    return (DEBUG_Scene_Scanner){0};
}

DEBUG_Scene_Scanner _m_debug_scene_scanner__go_to__scene() {
    if (!__DEBUG_scene_scanner.p_scene_manager) {
        debug_warning("[DEBUG] _m_debug_scene_scanner__go_to__scene, p_scene_manager == 0.");
        debug_warning("[DEBUG] call debug_get_ui_scanner at least once.");
        goto error;
    }

    if (!__DEBUG_scene_scanner.p_scene__current_in__scan) {
        debug_warning("[DEBUG] _m_debug_scene_scanner__go_to__scene, p_scene__current_in__scan == 0.");
        debug_warning("[DEBUG] call debug_get_ui_scanner at least once.");
        goto error;
    }

    Index__u32 index_of__scene = 
        __DEBUG_scene_scanner.p_scene__current_in__scan
        - __DEBUG_scene_scanner
        .p_scene_manager
        ->scenes
        ;

    if (index_of__scene >= Scene_Kind__Unknown) {
        debug_warning("[DEBUG] _m_debug_scene_scanner__go_to__scene, iterated scene out of bounds.");
        debug_warning("[DEBUG] recovering to first scene of manager.");
        debug_warning("[DEBUG] scene transition is not occuring at this time.");
        debug_warning("[DEBUG] memory might be corrupted!");

        __DEBUG_scene_scanner.p_scene__current_in__scan =
            __DEBUG_scene_scanner.p_scene_manager->scenes;
        goto finish;
    }

    set_active_scene_for__scene_manager(
            __DEBUG_scene_scanner.p_scene_manager, 
            index_of__scene);

finish:
    return __DEBUG_scene_scanner;
error:
    return (DEBUG_Scene_Scanner){0};
}

DEBUG_Scene_Scanner debug_get_scene_scanner(Game *p_game) {
    if (!p_game) {
        debug_warning("[DEBUG] debug_get_scene_scanner, p_game == 0.");
        goto error;
    }

    Scene_Manager *p_scene_manager =
        get_p_scene_manager_from__game(p_game);

    if (!p_scene_manager) {
        debug_warning("[DEBUG] debug_get_scene_scanner, p_scene_manager == 0.");
        goto error;
    }

    __DEBUG_scene_scanner.p_scene_manager = p_scene_manager;
    __DEBUG_scene_scanner.p_scene__running = p_scene_manager->p_active_scene;
    __DEBUG_scene_scanner.p_scene__current_in__scan = p_scene_manager->scenes;
    __DEBUG_scene_scanner.m_iterate_scene = _m_debug_scene_scanner__iterate_scene;
    __DEBUG_scene_scanner.m_go_to__scene = _m_debug_scene_scanner__go_to__scene;

    return __DEBUG_scene_scanner;
error:
    return (DEBUG_Scene_Scanner){0};
}
