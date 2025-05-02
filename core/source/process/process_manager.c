#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "timer.h"
#include <process/process_manager.h>
#include <process/process.h>

static inline
Process *get_p_process_by__index_from__process_manager(
        Process_Manager *p_process_manager,
        Index__u32 index_of__process) {
#ifndef NDEBUG
    if (index_of__process >= PROCESS_MAX_QUANTITY_OF) {
        debug_error("get_p_process_by__index_from__process_manager, index out of bounds: %d/%d",
                index_of__process,
                PROCESS_MAX_QUANTITY_OF);
        return 0;
    }
#endif
    return &p_process_manager->processes[
        index_of__process];
}

static inline
Process **get_p_ptr_process_by__index_from__active_procs_in__process_manager(
        Process_Manager *p_process_manager,
        Index__u32 index_of__process) {
#ifndef NDEBUG
    if (index_of__process >= PROCESS_MAX_QUANTITY_OF) {
        debug_error("get_p_ptr_process_by__index_from__active_processes_in__process_manager, index out of bounds: %d/%d",
                index_of__process,
                PROCESS_MAX_QUANTITY_OF);
        return 0;
    }
#endif
    return &p_process_manager->ptr_array_of__processes[
        index_of__process];
}

void initialize_process_manager(
        Process_Manager *p_process_manager) {
#ifndef NDEBUG
    if (!p_process_manager) {
        debug_abort("initialize_process_manager, p_process_manager is null.");
        return;
    }
#endif
    for (Index__u32 index_of__process = 0;
            index_of__process < PROCESS_MAX_QUANTITY_OF;
            index_of__process++) {
        initialize_process_as__empty_process(
                &p_process_manager
                ->processes[index_of__process]);
    }
    memset(p_process_manager->ptr_array_of__processes,
            0,
            sizeof(p_process_manager->ptr_array_of__processes));
    p_process_manager->next__uuid__u32 = 0;
    p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes = 
        p_process_manager->ptr_array_of__processes;

    initialize_repeatable_psuedo_random(
            &p_process_manager->repeatable_psuedo_random_for__process_uuid,
            (u32)((uint64_t)p_process_manager));
}

Process **get_p_ptr_to__process_in__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    for (Index__u32 index_of__process = 0;
            index_of__process < PROCESS_MAX_QUANTITY_OF;
            index_of__process++) {
        Process **p_ptr_process = 
            get_p_ptr_process_by__index_from__active_procs_in__process_manager(
                    p_process_manager, 
                    index_of__process);
        if (!p_ptr_process) {
            return 0;
        }

        if ((*p_ptr_process) == p_process) {
            return p_ptr_process;
        }
    }
    return 0;
}

void remove_process_from__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    Process **p_ptr_process =
        get_p_ptr_to__process_in__active_processes_in__process_manager(
                p_process_manager, 
                p_process);
    if (!p_ptr_process) {
        debug_error("remove_process_from__active_processes_in__process_manager, failed to find process within process_manager.");
        return;
    }

    if ((p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes - 1)
            == p_ptr_process) {
#ifndef NDEBUG
        if ((p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes - 1)
                - p_process_manager->ptr_array_of__processes
                >= PROCESS_MAX_QUANTITY_OF) {
            debug_error("remove_process_from__active_processes_in__process_manager, intrinsic violated.");
            return;
        }
#endif
        *(--p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes) = 0;
        return;
    }
    *p_ptr_process = *(--p_process_manager
        ->p_ptr_to__last_process_in__ptr_array_of__processes);
    *p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes = 0;
}

bool add_process_to__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    if (p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes >=
            (p_process_manager->ptr_array_of__processes + PROCESS_MAX_QUANTITY_OF)) {
        debug_error("add_process_to__active_processes_in__process_manager, too many active processes.");
        return false;
    }

    *p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes =
        p_process;
    p_process_manager->p_ptr_to__last_process_in__ptr_array_of__processes++;

    return true;
}

void release_process_from__process_manager(
        Game *p_game,
        Process_Manager *p_process_manager,
        Process *p_process) {
#ifndef NDEBUG
    u32 index = p_process
        - p_process_manager->processes;
    if (index >= PROCESS_MAX_QUANTITY_OF) {
        debug_error("release_process_from__process_manager, p_process was not allocated with this process_manager.");
        return;
    }
#endif
    remove_process_from__active_processes_in__process_manager(
            p_process_manager, 
            p_process);
    if (does_process_have__dispose_handler(p_process)) {
        p_process->m_process_dispose__handler(
                p_process,
                p_game);
    }
    initialize_process_as__empty_process(p_process);
}

Identifier__u32 get_next_uuid__u32_from__process_manager(
        Process_Manager *p_process_manager) {
    if (is_identifier_u32__invalid(p_process_manager->next__uuid__u32)) {
        p_process_manager->next__uuid__u32 = 0;
    }
    return p_process_manager->next__uuid__u32++;
}

///
/// Gets the next available process.
/// Return nullptr if no process is available.
///
Process *allocate_process_in__process_manager(
        Process_Manager *p_process_manager,
        Identifier__u32 uuid) {
    Process *p_process =
        (Process*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)p_process_manager->processes, 
            PROCESS_MAX_QUANTITY_OF, 
            uuid);
    if (!p_process) {
        debug_error("allocate_process_in__process_manager, failed to allocate process.");
        return 0;
    }
    if (!is_serialized_struct__deallocated(
                &p_process->_serialization_header)) {
        debug_error("allocate_process_in__process_manager, uuid already in use.");
        return 0;
    }

    add_process_to__active_processes_in__process_manager(
            p_process_manager, 
            p_process);

    initialize_process(
            p_process, 
            uuid, 
            0, 
            0,
            PROCESS_FLAGS__NONE);
    return p_process;
}

void swap_p_ptr_process_with__last_active_process_in__process_manager(
        Process_Manager *p_process_manager,
        Process **p_ptr_process) {
#ifndef NDEBUG
    if (!p_ptr_process) {
        debug_error("swap_p_ptr_process_with__last_active_process_in__process_manager, p_ptr_process == 0.");
        return;
    }
    if (p_ptr_process
            - p_process_manager->ptr_array_of__processes
            >= PROCESS_MAX_QUANTITY_OF) {
        debug_error("swap_p_ptr_process_with__last_active_process_in__process_manager, p_ptr_process is not from this manager.");
    }
#endif
    Process **p_ptr_to__last_process =
        (p_process_manager
                ->p_ptr_to__last_process_in__ptr_array_of__processes-1);
    Process *p_last_process = *p_ptr_to__last_process;
    *p_ptr_to__last_process = *p_ptr_process;
    *p_ptr_process = p_last_process;
}

Quantity__u32 poll_process_manager(
        Process_Manager *p_process_manager,
        Game *p_game) {
    p_process_manager->p_process__latest = 0;
    for (Index__u32 index_of__process = 0;
            index_of__process < PROCESS_MAX_QUANTITY_OF;
            index_of__process++) {
        Process **p_ptr_process = 
            get_p_ptr_process_by__index_from__active_procs_in__process_manager(
                p_process_manager, 
                index_of__process);

        if (!p_ptr_process || !*p_ptr_process)
            break;

        Quantity__u32 ticks_elapsed =
            poll__game_tick_timer(p_game);

        if (!is_process__critical(*p_ptr_process)) {
            if (ticks_elapsed) {
                continue;
            }

            ///
            /// continuously rotate non-critical processes.
            /// if one process constantly causes poll_process_manager to
            /// miss game ticks, it will not cause any process freezes for long.
            ///
            /// this will eventually push the problematic process the the back.
            ///
            swap_p_ptr_process_with__last_active_process_in__process_manager(
                    p_process_manager, 
                    p_ptr_process);
        }

        Process *p_process = *p_ptr_process;

        if (is_process__finished(p_process)) {
            if (p_process->p_enqueued_process) {
                set_process_as__dequeued(
                        p_process->p_enqueued_process);
            }
            release_process_from__process_manager(
                    p_game,
                    p_process_manager, 
                    p_process);
            continue;
        }
        if (is_process__enqueued(p_process)) {
            continue;
        }
        if (!p_process->m_process_run__handler) {
            continue;
        }

        p_process->m_process_run__handler(
                p_process,
                p_game);
    }

    return get_elapsed_ticks__u32F20_of__game(p_game);
}

Process *run_process_with__uuid(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Identifier__u32 uuid,
        Process_Flags__u8 process_flags__u8) {
    Process *p_process =
        allocate_process_in__process_manager(
                p_process_manager,
                uuid);

    if (!p_process) {
        debug_error("run_process, failed to allocate process.");
        return 0;
    }

    initialize_process(
            p_process, 
            p_process->_serialization_header.uuid, 
            m_process, 
            0,
            process_flags__u8);

    p_process_manager->p_process__latest =
        p_process;

    return p_process;
}

Process *run_process(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Process_Flags__u8 process_flags__u8) {
    Identifier__u32 uuid =
        get_next_available__random_uuid_in__contiguous_array(
                (Serialization_Header *)p_process_manager->processes, 
                PROCESS_MAX_QUANTITY_OF, 
                &p_process_manager
                ->repeatable_psuedo_random_for__process_uuid);
    return run_process_with__uuid(
            p_process_manager, 
            m_process, 
            uuid, 
            process_flags__u8);
}

Quantity__u32 get_quantity_of__processes_in__process_manager(
        Process_Manager *p_process_manager) {
    Quantity__u32 quantity_of__processes = 0;
    for (;quantity_of__processes
            < PROCESS_MAX_QUANTITY_OF;
            quantity_of__processes++) {
        Process **p_ptr_process =
            get_p_ptr_process_by__index_from__active_procs_in__process_manager(
                    p_process_manager, 
                    quantity_of__processes);
        if (!p_ptr_process || !*p_ptr_process) {
            return quantity_of__processes;
        }
    }

    return PROCESS_MAX_QUANTITY_OF; 
}
