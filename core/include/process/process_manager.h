#ifndef PROCESS_MANAGER_H
#define PROCESS_MANAGER_H

#include "defines_weak.h"
#include <defines.h>

void initialize_process_manager(
        Process_Manager *p_process_manager);

void deallocate_process_from__process_manager(
        Process_Manager *p_process_manager,
        Process *p_process);

///
/// Gets the next available process.
/// Return nullptr if no process is available.
///
Process *allocate_process_in__process_manager(
        Process_Manager *p_process_manager);

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
Process *run_process(
        Process_Manager *p_process_manager,
        m_Process m_process,
        Process_Flags__u8 process_flags__u8);

#endif
