#ifndef PROCESS_MANAGER_H
#define PROCESS_MANAGER_H

#include "defines_weak.h"
#include "serialization/hashing.h"
#include <defines.h>

void initialize_process_manager(
        Process_Manager *p_process_manager);

void release_process_from__process_manager(
        Game *p_game,
        Process_Manager *p_process_manager,
        Process *p_process);

///
/// Gets the next available process.
/// Return nullptr if no process is available.
///
Process *allocate_process_in__process_manager(
        Process_Manager *p_process_manager,
        Identifier__u32 uuid);

///
/// Don't invoke.
/// Returns quantity of ticks elapsed.
///
Quantity__u32 poll_process_manager(
        Process_Manager *p_process_manager,
        Game *p_game);

///
/// returns null on failure.
///
Process *run_process_with__uuid(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Identifier__u32 uuid,
        Process_Flags__u8 process_flags__u8);

Process *run_process(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Process_Flags__u8 process_flags__u8);

Quantity__u32 get_quantity_of__processes_in__process_manager(
        Process_Manager *p_process_manager);

static inline
Process *get_p_process_by__uuid(
        Process_Manager *p_process_manager,
        Identifier__u32 uuid__u32) {
    return (Process*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)p_process_manager->processes, 
            PROCESS_MAX_QUANTITY_OF, 
            uuid__u32);
}

static inline
Process *get_p_latest_allocated_process_from__process_manager(
        Process_Manager *p_process_manager) {
    Process *p_process =
        p_process_manager->p_process__latest;
    p_process_manager->p_process__latest = 0;
    return p_process;
}

#endif
