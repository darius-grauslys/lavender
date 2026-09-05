#ifndef DEBUG_ENTITY_H
#define DEBUG_ENTITY_H

#include <defines.h>

/*
 * debug_entiy.h provides functions which are intended to be invoked through
 * gdb or other debug modules.
 *
 * DO NOT USE debug_* functions in non-debug modules.
 * With the only exception being debug_* functions for logging.
 * See docs/core/debug/debug.md
 * TODO: make docs/core/debug/debug.md
 */

#ifndef NDEBUG

typedef struct DEBUG_Entity_Scanner_t DEBUG_Entity_Scanner;

///
/// A function to perform debug scanning operations with.
///
typedef DEBUG_Entity_Scanner (*m_DEBUG_Entity_Scanner_Func)();

typedef struct DEBUG_Entity_Scanner_t {
    Entity_Manager *p_entity_manager;
    Entity *p_entity__current;
    m_DEBUG_Entity_Scanner_Func m_next_entity;
} DEBUG_Entity_Scanner;

DEBUG_Entity_Scanner debug_get_entity_scanner(Game *p_game);

#endif

#endif
