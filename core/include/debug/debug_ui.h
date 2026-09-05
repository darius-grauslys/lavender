#ifndef DEBUG_UI_H
#define DEBUG_UI_H

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
    m_DEBUG_UI_Scanner_Func m_next_manager;
    m_DEBUG_UI_Scanner_Func m_next_element;
} DEBUG_UI_Scanner;

DEBUG_UI_Scanner debug_get_ui_scanner(Game *p_game);

#endif

#endif
