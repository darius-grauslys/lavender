#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "process/process_table.h"
#include "random.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "timer.h"
#include <process/process_manager.h>
#include <process/process.h>

static inline
bool is_process_priority_table_entry__empty(
        Process_Priority_Table_Entry *p_process_priority_table_entry) {
    return p_process_priority_table_entry
        ->p_ptr_process__oldest_of__priority
        == 0
        || p_process_priority_table_entry
        ->p_ptr_process__youngest_of__priority
        == 0
        ;
}

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
    initialize_process_table(
            &p_process_manager->process_table);
    p_process_manager->next__uuid__u32 = 0;

    initialize_repeatable_psuedo_random(
            &p_process_manager->repeatable_psuedo_random_for__process_uuid,
            (u32)((uint64_t)p_process_manager));
}

void remove_process_from__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    remove_process_from__process_table(
            &p_process_manager->process_table, 
            p_process);
}

bool add_process_to__active_processes_in__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process) {
    return add_process_to__process_table(
            &p_process_manager->process_table, 
            p_process);
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
        Identifier__u32 uuid,
        uint32_t priority_level) {
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

    initialize_process(
            p_process, 
            uuid, 
            0, 
            0,
            priority_level,
            PROCESS_FLAGS__NONE);

    add_process_to__active_processes_in__process_manager(
            p_process_manager, 
            p_process);

    return p_process;
}

Quantity__u32 poll_process_manager(
        Process_Manager *p_process_manager,
        Game *p_game) {
    begin_polling_of__process_table(&p_process_manager->process_table);
    p_process_manager->p_process__latest = 0;
    Process *p_process = 0;
    Quantity__u32 ticks_elapsed = 0;
    while ((p_process = poll_next_p_process_from__process_table(
                    &p_process_manager->process_table))
            && (is_process__critical(p_process)
            || !ticks_elapsed)) {
        if (!p_process)
            break;
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
            complete_process(p_process);
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
        Process_Priority__u8 process_priority__u8,
        Process_Flags__u8 process_flags__u8) {
    Process *p_process =
        allocate_process_in__process_manager(
                p_process_manager,
                uuid,
                process_priority__u8);

    if (!p_process) {
        debug_error("run_process, failed to allocate process.");
        return 0;
    }

    initialize_process(
            p_process, 
            p_process->_serialization_header.uuid, 
            m_process, 
            0,
            process_priority__u8,
            process_flags__u8);

    p_process_manager->p_process__latest =
        p_process;

    return p_process;
}

Process *run_process(
        Process_Manager *p_process_manager,
        m_Process m_process,
        uint32_t priority_level,
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
            priority_level,
            process_flags__u8);
}

Quantity__u32 get_quantity_of__processes_in__process_manager(
        Process_Manager *p_process_manager) {
    return get_quantity_of__processes_in__process_table(
            &p_process_manager->process_table);
}
