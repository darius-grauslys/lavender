#ifndef DEBUG_UI_H
#define DEBUG_UI_H

#include "defines_weak.h"
#include "types/implemented/ui/ui_element_kind.h"
#include <defines.h>

/*
 * debug_ui.h provides functions which are intended to be invoked through
 * gdb or other debug modules.
 *
 * DO NOT USE debug_* functions in non-debug modules.
 * With the only exception being debug_* functions for logging.
 * See docs/core/debug/debug.md
 * TODO: make docs/core/debug/debug.md
 */

#ifndef NDEBUG

typedef struct DEBUG_UI_Scanner_t DEBUG_UI_Scanner;

///
/// A function to perform debug scanning operations with.
///
typedef DEBUG_UI_Scanner (*m_DEBUG_UI_Scanner_Func)();

typedef struct DEBUG_UI_Scanner_t {
    UI_Context *p_ui_context;
    UI_Manager *p_ui_manager__current;
    UI_Element **p_ptr_ui_element__current;

    ///
    /// Gets the next manager.
    ///
    m_DEBUG_UI_Scanner_Func m_next_manager;

    ///
    /// Gets the next element.
    ///
    m_DEBUG_UI_Scanner_Func m_next_element;

    ///
    /// Refreshes scanner data fields to ground truth.
    ///
    m_DEBUG_UI_Scanner_Func m_refresh;

    ///
    /// Module post condition: these fields
    /// are evaluated on every module function and m_ func.
    ///
    Quantity__u32 array_of__quantity_of__elements_in__all_managers__u32[
        MAX_QUANTITY_OF__UI_MANAGERS];
    Identifier__u32 uuid_of__ui_manager__current;
    Identifier__u32 uuid_of__ui_element__current;
    Quantity__u32 max_quantity_of__ui_managers__u32;
    UI_Element_Kind the_kind_of__ui_element__current;
} DEBUG_UI_Scanner;

DEBUG_UI_Scanner debug_get_ui_scanner(Game *p_game);

#endif

#endif
