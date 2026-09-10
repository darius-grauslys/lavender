#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "process/process.h"
#include "serialization/serialization_header.h"
#include <debug/debug_process.h>

DEBUG_Process_Scanner __DEBUG_process_scanner = {0};

///
/// Precondition: __DEBUG_process_scanner.p_process_manager != 0.
///
/// Returns true if the process tracking is modified.
///
bool __debug_resolve_process_in__scanner() {
    Process_Manager *p_process_manager = 
        __DEBUG_process_scanner.p_process_manager;
    Process **p_ptr_process = 
        __DEBUG_process_scanner.p_ptr_process__current;
    bool is_tracking_moved = false;

    // If null, attempt to get from start of manager.
    if(!p_ptr_process || !*p_ptr_process) {
        p_ptr_process =
            p_process_manager
            ->process_table
            .ptr_array_of__processes
            ;
    }

    // If null still, manager is totally empty, exit.
    if (!*p_ptr_process) {
        goto empty;
    } 
    
    // Process is non-null, validate it's memory range.
    Index__u32 index_of__process = 
        p_ptr_process 
        - p_process_manager
        ->process_table
        .ptr_array_of__processes
        ;

    if (index_of__process
            >= PROCESS_MAX_QUANTITY_OF) {
        // Out of bounds
        debug_warning("[DEBUG] __debug_resolve_process_in__scanner, p_process out of bounds.");
        debug_warning("[DEBUG] attempting to set pointer to start of process_manager.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto reset;
    }

    // Finally, check if the process is deallocated.
    if (IS_DEALLOCATED_P(*p_ptr_process)) {
        debug_info("[DEBUG] __debug_resolve_process_in__scanner, p_process dealocated.");
        goto reset;
    }

    // Process is active, reset in scanner to be sure
    // any changes stick.
    goto exit;
reset:
    is_tracking_moved = true;
    p_ptr_process = p_process_manager
        ->process_table
        .ptr_array_of__processes
        ;
    if (!*p_ptr_process) {
        goto empty;
    }
exit:
    __DEBUG_process_scanner
        .p_ptr_process__current =
        p_ptr_process;
    __DEBUG_process_scanner
        .p_process__current =
        *p_ptr_process;
    __DEBUG_process_scanner
        .copy_of__process__current =
        **p_ptr_process;
    return is_tracking_moved;
empty:
    // NOTE: depending on where we are in debugging, this could
    // possibly be a false positive, if we are debugging the
    // process table restructuring, the assumption that [0]
    // being null => no processes, may be incorrect.
    //
    // Generally, this is true however.
    debug_info("[DEBUG] p_process_manager has no processes.");
    __DEBUG_process_scanner
        .p_ptr_process__current = 0;
    __DEBUG_process_scanner
        .p_process__current = 0;
    initialize_process_as__empty_process(
            &__DEBUG_process_scanner
            .copy_of__process__current);
    return true;
}

DEBUG_Process_Scanner __m_debug_process_scanner__refresh() {
    Process_Manager *p_process_manager = 
        __DEBUG_process_scanner.p_process_manager;
    if (!p_process_manager) {
        debug_warning("[DEBUG] __m_debug_process_scanner__refresh, p_process_manager == 0.");
        debug_warning("[DEBUG] call debug_get_process_scanner(p_game) at least once.");
        goto error;
    }

    __debug_resolve_process_in__scanner();

    Process *p_process =
        __DEBUG_process_scanner.p_process__current;

    if (!p_process) {
        debug_info("[DEBUG] __m_debug_ui_scanner__refresh, p_process_manager is empty.");
        goto exit;
    }
exit:
    return __DEBUG_process_scanner;
error:
    return (DEBUG_Process_Scanner){0};
}

DEBUG_Process_Scanner __m_debug_process_scanner__next_process() {
    Process_Manager *p_process_manager = 
        __DEBUG_process_scanner.p_process_manager;
    if (!p_process_manager) {
        debug_warning("[DEBUG] __m_debug_process_scanner__refresh, p_process_manager == 0.");
        debug_warning("[DEBUG] call debug_get_process_scanner(p_game) at least once.");
        goto error;
    }

    if (__debug_resolve_process_in__scanner()) {
        // Tracking moved, function's semantic complete.
        goto exit;
    }

    Process *p_process =
        __DEBUG_process_scanner
        .p_process__current;

    if (!p_process) {
        debug_info("[DEBUG] __m_debug_process_scanner__next_process, p_process_manager empty.");
        goto exit;
    }

    // Known to be in bounds after __debug_resolve_scene_in__scanner.
    Process **p_ptr_process__next = 0;
    for (Index__u32 offset_of__process = 1;
            offset_of__process < PROCESS_MAX_QUANTITY_OF;
            offset_of__process++) {
        Index__u32 index_of__process =
            __DEBUG_process_scanner
            .p_ptr_process__current
            - p_process_manager
            ->process_table
            .ptr_array_of__processes
            ;

        Index__u32 normalized_index =
            (index_of__process+offset_of__process)
            % PROCESS_MAX_QUANTITY_OF
            ;

        p_ptr_process__next =
            &p_process_manager
            ->process_table
            .ptr_array_of__processes[
                normalized_index]
                ;
        if (*p_ptr_process__next)
            break;
    }

    __DEBUG_process_scanner
        .p_ptr_process__current =
        p_ptr_process__next;

    __debug_resolve_process_in__scanner(); // Module post condition

exit:
    return __DEBUG_process_scanner;
error:
    return (DEBUG_Process_Scanner){0};
}

DEBUG_Process_Scanner debug_get_process_scanner(Game *p_game) {
    __DEBUG_process_scanner.p_process_manager =
        get_p_process_manager_from__game(p_game);
    __debug_resolve_process_in__scanner();
    if (!__DEBUG_process_scanner.p_process_manager) {
        debug_warning("[DEBUG] debug_get_process_scanner, p_process_manager == 0.");
    }

    __DEBUG_process_scanner.m_refresh =
        __m_debug_process_scanner__refresh;
    __DEBUG_process_scanner.m_iterate_process =
        __m_debug_process_scanner__next_process;

    return __DEBUG_process_scanner;
}
