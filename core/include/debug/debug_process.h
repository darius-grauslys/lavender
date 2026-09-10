#ifndef DEBUG_PROCESS_H
#define DEBUG_PROCESS_H

#include "defines_weak.h"
#include <defines.h>

/*
 * debug_process.h provides functions which are intended to be invoked through
 * gdb or other debug modules.
 *
 * DO NOT USE debug_* functions in non-debug modules.
 * With the only exception being debug_* functions for logging.
 * See docs/core/debug/debug.md
 * TODO: make docs/core/debug/debug.md
 */

#ifndef NDEBUG

typedef struct DEBUG_Process_Scanner_t DEBUG_Process_Scanner;

///
/// A function to perform debug scanning operations with.
///
typedef DEBUG_Process_Scanner (*m_DEBUG_Process_Scanner_Func)();

typedef struct DEBUG_Process_Scanner_t {
    Process_Manager *p_process_manager;
    Process *p_process__current;
    Process **p_ptr_process__current;
    ///
    /// Updates scanner state to reflect game engine state.
    ///
    m_DEBUG_Process_Scanner_Func m_refresh;
    ///
    /// Moves p_process__current_in__scan through available process in the manager,
    ///
    m_DEBUG_Process_Scanner_Func m_iterate_process;

    /// 
    /// Module post condition:
    /// The following fields are always updated to reflect
    /// current game engine state after the conclusion of
    /// every module fuction and the m_ funcs.
    ///
    Quantity__u32 quantity_of__processes;

    Process copy_of__process__current;
} DEBUG_Process_Scanner;

DEBUG_Process_Scanner debug_get_process_scanner(Game *p_game);

#endif

#endif
