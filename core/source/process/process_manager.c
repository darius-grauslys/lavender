#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
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
    return &p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes[
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
    p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes = 0;
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

    if ((p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes)
            == p_ptr_process) {
        p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes--;
#ifndef NDEBUG
        if (p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes
                - p_process_manager->ptr_array_of__processes
                >= PROCESS_MAX_QUANTITY_OF) {
            debug_error("remove_process_from__active_processes_in__process_manager, intrinsic violated. (1/2)");
        }
#endif
        return;
    }
    Process **p_ptr_process__next_end =
        p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes - 1;
#ifndef NDEBUG
        if (p_ptr_process__next_end
                - p_process_manager->ptr_array_of__processes
                >= PROCESS_MAX_QUANTITY_OF) {
            debug_error("remove_process_from__active_processes_in__process_manager, intrinsic violated. (2/2)");
        }
#endif
    *p_ptr_process = *p_process_manager
        ->p_ptr_to__next_slot_in__ptr_array_of__processes;
    *p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes = 0;
    p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes =
        p_ptr_process__next_end;
}

bool add_process_to__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    if (p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes >=
            (p_process_manager->ptr_array_of__processes + PROCESS_MAX_QUANTITY_OF)) {
        debug_error("add_process_to__active_processes_in__process_manager, too many active processes.");
        return false;
    }

    *p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes =
        p_process;
    p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes++;

    return true;
}

void deallocate_process_from__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
#ifndef NDEBUG
    u32 index = p_process
        - p_process_manager->processes;
    if (index >= PROCESS_MAX_QUANTITY_OF) {
        debug_error("deallocate_process_from__process_manager, p_process was not allocated with this process_manager.");
        return;
    }
#endif

    Serialized_Field s_process;
    initialize_serialized_field_as__unlinked(
            &s_process, 
            p_process->_serialization_header.uuid);
    link_serialized_field_against__contiguous_array(
            &s_process, 
            (Serialization_Header *)p_process_manager->processes, 
            PROCESS_MAX_QUANTITY_OF);
    if (!is_p_serialized_field__linked(&s_process)) {
        debug_error("deallocate_process_from__process_manager, failed to find process.");
        return;
    }
    remove_process_from__active_processes_in__process_manager(
            p_process_manager, 
            p_process);
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
        Process_Manager *p_process_manager) {
    Identifier__u32 uuid__u32 =
        get_next_available__uuid_in__contiguous_array(
                (Serialization_Header*)p_process_manager->processes, 
                PROCESS_MAX_QUANTITY_OF, 
                get_next_uuid__u32_from__process_manager(
                    p_process_manager));
    if (is_identifier_u32__invalid(uuid__u32)) {
        debug_error("allocate_process_in__process_manager, failed to allocate process.");
        return 0;
    }
    Index__u32 index = poll_for__uuid_collision(
            (Serialization_Header*)p_process_manager->processes, 
            PROCESS_MAX_QUANTITY_OF, 
            uuid__u32);

    Process *p_process = 
        get_p_process_by__index_from__process_manager(
            p_process_manager, 
            index);

    initialize_serialization_header(
            &p_process->_serialization_header, 
            uuid__u32, 
            sizeof(Process));
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
    Process *p_last_process =
        *p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes;
    p_process_manager->p_ptr_to__next_slot_in__ptr_array_of__processes =
        p_ptr_process;
    *p_ptr_process = p_last_process;
}

Quantity__u32 poll_process_manager(
        Process_Manager *p_process_manager,
        Game *p_game) {
    for (Index__u32 index_of__process = 0;
            index_of__process < PROCESS_MAX_QUANTITY_OF;
            index_of__process++) {
        Process **p_ptr_process = get_p_ptr_process_by__index_from__active_procs_in__process_manager(
                p_process_manager, 
                index_of__process);

        if (!p_ptr_process || !*p_ptr_process)
            break;

        Quantity__u32 ticks_elapsed =
            poll__game_tick_timer(p_game);

        if (!is_process__critical(*p_ptr_process)) {
            if (ticks_elapsed)
                continue;

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

#ifndef NDEBUG
        if (!(*p_ptr_process)->m_process_run__handler) {
            debug_error("poll_process_manager, process:%p, lacks m_process_run__handler.");
            deallocate_process_from__process_manager(
                    p_process_manager, 
                    *p_ptr_process);
        }
#endif

        (*p_ptr_process)->m_process_run__handler(
                *p_ptr_process,
                p_game);
    }

    return poll__game_tick_timer(p_game);
}

Process *run_process(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Process_Flags__u8 process_flags__u8) {
    Process *p_process =
        allocate_process_in__process_manager(
                p_process_manager);

    if (!p_process) 
        return 0;

    initialize_process(
            p_process, 
            p_process->_serialization_header.uuid, 
            m_process, 
            0);

    return p_process;
}
